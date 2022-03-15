#[macro_use]
extern crate log;

use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::fmt::{Display, Formatter};
use std::hash::Hash;
use std::mem;
use std::ops::{Add, AddAssign, Sub, SubAssign};

use futures_util::sink::SinkExt;
use futures_util::StreamExt;
use prost::Message;
use rand::distributions::{Distribution, Standard};
use rand::{CryptoRng, Rng};
use serde::Serialize;
use tokio::io::{AsyncRead, AsyncWrite};
use tokio_tungstenite::WebSocketStream;
use tungstenite::handshake::server::{ErrorResponse, Request, Response};
use tungstenite::http::HeaderValue;

mod battleship_prost {
    include!(concat!(env!("OUT_DIR"), "/battleship.rs"));
}

fn div_ceil(dividend: u32, divisor: u32) -> u32 {
    let mut quotient = dividend / divisor;
    if dividend % divisor != 0 {
        quotient += 1
    };
    quotient
}

#[derive(Debug, Hash, Eq, PartialEq, Copy, Clone, Ord, PartialOrd)]
#[repr(transparent)]
struct BoardUnit(u32);

impl Add for BoardUnit {
    type Output = BoardUnit;

    fn add(self, rhs: Self) -> Self::Output { Self(self.0.add(rhs.0)) }
}

impl AddAssign for BoardUnit {
    fn add_assign(&mut self, rhs: Self) { self.0.add_assign(rhs.0) }
}

impl Sub for BoardUnit {
    type Output = BoardUnit;

    fn sub(self, rhs: Self) -> Self::Output { Self(self.0.sub(rhs.0)) }
}

impl SubAssign for BoardUnit {
    fn sub_assign(&mut self, rhs: Self) { self.0.sub_assign(rhs.0) }
}

#[derive(Debug, Hash, Eq, PartialEq, Copy, Clone)]
struct Point {
    row: BoardUnit,
    col: BoardUnit,
}

#[derive(Debug, Hash, Eq, PartialEq, Copy, Clone)]
enum Orientation {
    Down,
    Right,
}

impl Distribution<Orientation> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Orientation {
        match rng.gen_range(0..=1) {
            0 => Orientation::Down,
            1 => Orientation::Right,
            _ => unreachable!(),
        }
    }
}

impl From<battleship_prost::ship::Orientation> for Orientation {
    fn from(unverified_orientation: battleship_prost::ship::Orientation) -> Self {
        match unverified_orientation {
            battleship_prost::ship::Orientation::Down => Self::Down,
            battleship_prost::ship::Orientation::Right => Self::Right,
        }
    }
}

impl From<Orientation> for battleship_prost::ship::Orientation {
    fn from(orientation: Orientation) -> Self {
        match orientation {
            Orientation::Down => Self::Down,
            Orientation::Right => Self::Right,
        }
    }
}

#[derive(Debug, Clone)]
struct Ship {
    start:          Point,
    orientation:    Orientation,
    hit_vector:     Vec<usize>,
    remaining_hits: BoardUnit,
    length:         BoardUnit,
}

impl From<&Ship> for battleship_prost::Ship {
    fn from(ship: &Ship) -> Self {
        battleship_prost::Ship {
            start:       ship.start.into(),
            orientation: battleship_prost::ship::Orientation::from(ship.orientation).into(),
            length:      ship.length.0,
        }
    }
}

#[derive(Debug, Hash, Copy, Clone)]
enum MissileResult {
    Hit(Option<BoardUnit>),
    Miss,
}

impl Ship {
    fn mark_hit(&mut self, hit_index: BoardUnit) -> Option<BoardUnit> {
        assert!(hit_index < self.length);

        let i = (hit_index.0 / usize::MAX.count_ones()) as usize;
        let m = 1usize << (hit_index.0 % usize::MAX.count_ones());
        let change = (self.hit_vector[i] & m) == 0;
        self.hit_vector[i] |= m;

        if change {
            self.remaining_hits -= BoardUnit(1);
            Some(self.remaining_hits)
        } else {
            None
        }
    }

    fn strike(&mut self, target: Point) -> MissileResult {
        fn intersects(low: BoardUnit, high: BoardUnit, strike: BoardUnit) -> bool {
            low <= strike && high > strike
        }

        fn hit_index(low: BoardUnit, _high: BoardUnit, strike: BoardUnit) -> BoardUnit {
            strike - low
        }

        if !match self.orientation {
            Orientation::Down => target.col == self.start.col,
            Orientation::Right => target.row == self.start.row,
        } {
            return MissileResult::Miss;
        }

        let (low, high, strike) = match self.orientation {
            Orientation::Down => (self.start.row, self.start.row + self.length, target.row),
            Orientation::Right => (self.start.col, self.start.col + self.length, target.col),
        };

        if intersects(low, high, strike) {
            MissileResult::Hit(self.mark_hit(hit_index(low, high, strike)))
        } else {
            MissileResult::Miss
        }
    }
}

#[derive(Debug, Clone)]
struct Board {
    width:      BoardUnit,
    height:     BoardUnit,
    ships:      Vec<Ship>,
    ships_left: BoardUnit,
}

impl Board {
    fn strike(&mut self, target: Point) -> battleship_prost::MissileResult {
        for ship in &mut self.ships {
            match ship.strike(target) {
                MissileResult::Hit(Some(updated_spots_left)) => {
                    debug!("New hit with {:?} spots left.", updated_spots_left);
                    let mut ship_sunk = None;
                    if updated_spots_left == BoardUnit(0) {
                        self.ships_left -= BoardUnit(1);
                        ship_sunk = Some((&*ship).into());
                    }
                    return battleship_prost::MissileResult {
                        missile_result: battleship_prost::missile_result::MissileResult::Hit.into(),
                        ship_sunk,
                    };
                },
                MissileResult::Hit(None) =>
                    return battleship_prost::MissileResult {
                        missile_result: battleship_prost::missile_result::MissileResult::Hit.into(),
                        ship_sunk:      None,
                    },
                MissileResult::Miss => continue,
            }
        }

        debug!("Miss!");
        return battleship_prost::MissileResult {
            missile_result: battleship_prost::missile_result::MissileResult::Miss.into(),
            ship_sunk:      None,
        };
    }
}

impl Board {
    async fn rand_board(
        width: BoardUnit,
        height: BoardUnit,
        ship_lengths: &[BoardUnit],
    ) -> Result<Self, tokio::task::JoinError> {
        let ship_lengths = ship_lengths.to_vec();
        tokio::task::spawn_blocking(move || {
            let mut rng = rand::thread_rng();
            Self::rand_board_internal(&mut rng, width, height, &ship_lengths)
        })
        .await
        .map(|result| result.0)
    }

    fn rand_board_internal<R>(
        rng: &mut R,
        width: BoardUnit,
        height: BoardUnit,
        ship_lengths: &[BoardUnit],
    ) -> (Self, usize)
    where
        R: Rng + CryptoRng,
    {
        let mut ships = Vec::with_capacity(ship_lengths.len());
        let ship_length_sum = ship_lengths.iter().fold(BoardUnit(0), |sum, &l| sum + l).0 as usize;
        let mut counter = 0;

        loop {
            counter += 1;

            for &length in ship_lengths {
                let orientation = rng.sample(rand::distributions::Standard);

                let (max_row, max_col) = match orientation {
                    Orientation::Down => (height - length, width),
                    Orientation::Right => (height, width - length),
                };
                let row = BoardUnit(rng.gen_range(0..max_row.0));
                let col = BoardUnit(rng.gen_range(0..max_col.0));

                ships.push(Ship {
                    start: Point {
                        row,
                        col,
                    },
                    orientation,
                    hit_vector: Vec::with_capacity(0),
                    remaining_hits: length,
                    length,
                });
            }

            if ship_length_sum !=
                ships
                    .iter()
                    .flat_map(|ship| ship.into_iter())
                    .collect::<HashSet<_>>()
                    .len()
            {
                ships.clear();
            } else {
                break;
            }
        }

        for mut ship in &mut ships {
            ship.hit_vector = vec![0; div_ceil(ship.length.0, usize::MAX.count_ones()) as usize];
        }

        (
            Board {
                width,
                height,
                ships,
                ships_left: BoardUnit(ship_lengths.len() as u32),
            },
            counter,
        )
    }
}

#[derive(Debug, Hash, Eq, PartialEq, Copy, Clone)]
enum Turn {
    Mine,
    Opponent,
}

impl Turn {
    fn end_turn(&mut self) {
        let _ = mem::replace(
            self,
            match self {
                Self::Mine => Self::Opponent,
                Self::Opponent => Self::Mine,
            },
        );
    }
}


const BOARD_WIDTH: BoardUnit = BoardUnit(20);
const BOARD_HEIGHT: BoardUnit = BoardUnit(20);
const NUM_SHIPS: BoardUnit = BoardUnit(10);
const SHIP_LENGTHS: [BoardUnit; NUM_SHIPS.0 as usize] = [
    BoardUnit(5),
    BoardUnit(4),
    BoardUnit(3),
    BoardUnit(3),
    BoardUnit(2),
    BoardUnit(5),
    BoardUnit(4),
    BoardUnit(3),
    BoardUnit(3),
    BoardUnit(2),
];
const STARTING_TURN: Turn = Turn::Opponent;
const TURN_WAIT_MILLIS: u64 = 500;

#[derive(Debug, Clone)]
pub struct BoardValidateError {
    unverified_board: battleship_prost::Board,
}

impl Display for BoardValidateError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "Failed to validate board: {:?}", self.unverified_board)
    }
}

impl Error for BoardValidateError {}

fn ship_is_in_bounds(
    width: BoardUnit,
    height: BoardUnit,
    start: Point,
    orientation: Orientation,
    length: BoardUnit,
) -> bool {
    let (max_row, max_col) = match orientation {
        Orientation::Down => (start.row + length, start.col),
        Orientation::Right => (start.row, start.col + length),
    };

    max_col <= width && max_row <= height
}

impl TryFrom<battleship_prost::Board> for Board {
    type Error = BoardValidateError;

    fn try_from(unverified_board: battleship_prost::Board) -> Result<Self, Self::Error> {
        fn len_freq<I>(iter: I) -> HashMap<BoardUnit, BoardUnit>
        where
            I: Iterator<Item = BoardUnit>,
        {
            iter.fold(HashMap::new(), |mut map, l| {
                map.entry(l)
                    .or_insert(BoardUnit(0))
                    .add_assign(BoardUnit(1));
                map
            })
        }

        if BoardUnit(unverified_board.width) != BOARD_WIDTH ||
            BoardUnit(unverified_board.height) != BOARD_HEIGHT ||
            unverified_board.ships.len() != NUM_SHIPS.0 as usize ||
            len_freq(SHIP_LENGTHS.iter().copied()) !=
                len_freq(
                    unverified_board
                        .ships
                        .iter()
                        .map(|ship| ship.length)
                        .map(|l| BoardUnit(l)),
                )
        {
            return Err(BoardValidateError {
                unverified_board,
            }
            .into());
        }

        let width = BoardUnit(unverified_board.width);
        let height = BoardUnit(unverified_board.height);
        let mut ships = Vec::with_capacity(unverified_board.ships.len());
        let ships_left = BoardUnit(unverified_board.ships.len() as u32);

        for unverified_ship in &unverified_board.ships {
            let length = BoardUnit(unverified_ship.length);
            let orientation = unverified_ship.orientation().into();
            let start = Point {
                row: BoardUnit(unverified_ship.start.row),
                col: BoardUnit(unverified_ship.start.col),
            };
            if !ship_is_in_bounds(width, height, start, orientation, length) {
                return Err(BoardValidateError {
                    unverified_board,
                }
                .into());
            }


            let hit_vector = vec![0; div_ceil(length.0, usize::MAX.count_ones()) as usize];

            ships.push(Ship {
                start,
                orientation,
                hit_vector,
                remaining_hits: length,
                length,
            })
        }

        let ship_length_sum = SHIP_LENGTHS.iter().fold(BoardUnit(0), |sum, &l| sum + l).0 as usize;
        let unique_points = ships
            .iter()
            .flat_map(|ship| ship.into_iter())
            .collect::<HashSet<_>>()
            .len();
        if unique_points != ship_length_sum {
            return Err(BoardValidateError {
                unverified_board,
            }
            .into());
        }

        Ok(Board {
            width,
            height,
            ships,
            ships_left,
        })
    }
}

impl From<Point> for battleship_prost::Point {
    fn from(point: Point) -> Self {
        battleship_prost::Point {
            row: point.row.0,
            col: point.col.0,
        }
    }
}

#[derive(Debug, Clone)]
struct Solver {
    targets: Vec<Point>,
}

impl IntoIterator for &Ship {
    type IntoIter = ShipIterator;
    type Item = Point;

    fn into_iter(self) -> Self::IntoIter {
        ShipIterator {
            cur:         self.start,
            left:        self.length,
            orientation: self.orientation,
        }
    }
}

struct ShipIterator {
    cur:         Point,
    left:        BoardUnit,
    orientation: Orientation,
}

impl Iterator for ShipIterator {
    type Item = Point;

    fn next(&mut self) -> Option<Self::Item> {
        if self.left > BoardUnit(0) {
            let out = Some(self.cur);
            match self.orientation {
                Orientation::Down => self.cur.row += BoardUnit(1),
                Orientation::Right => self.cur.col += BoardUnit(1),
            }
            self.left -= BoardUnit(1);
            out
        } else {
            None
        }
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let left = self.left.0 as usize;
        (left, Some(left))
    }
}

impl Solver {
    fn new(_my_board: &Board, their_board: &Board) -> Self {
        let targets = their_board
            .ships
            .iter()
            .flat_map(|ship| ship.into_iter())
            .collect();
        Self {
            targets,
        }
    }

    fn next_move(&mut self, _my_board: &Board, their_board: &Board) -> Point {
        let mut rng = rand::thread_rng();
        self.targets.pop().unwrap_or_else(|| {
            let row = BoardUnit(rng.gen_range(0..their_board.height.0));
            let col = BoardUnit(rng.gen_range(0..their_board.width.0));
            Point {
                row,
                col,
            }
        })
    }
}

#[macro_use]
extern crate serde;

#[derive(Debug, Clone, Deserialize)]
struct CaptchaVerifyResponse {
    success:  bool,
    hostname: String,
}

#[derive(Debug, Clone, Serialize)]
struct CaptchaVerifyRequest<T> {
    secret:   T,
    response: String,
}

pub async fn validate_captcha<S, T>(
    mut stream: WebSocketStream<S>,
    captcha_secret: T,
    origin_hostname: &str,
) -> Result<WebSocketStream<S>, Box<dyn Error>>
where
    S: AsyncRead + AsyncWrite + Unpin,
    T: AsRef<String> + Display,
{
    if let Some(Ok(initialize)) = stream.next().await {
        let g_captcha_response =
            battleship_prost::Initialize::decode(initialize.into_data().as_slice())?
                .g_captcha_response;
        let CaptchaVerifyResponse {
            success,
            hostname: captcha_hostname,
        } = reqwest::ClientBuilder::new()
            .use_rustls_tls()
            .https_only(true)
            .user_agent("battleship-server")
            .build()
            .unwrap()
            .post("https://www.google.com/recaptcha/api/siteverify")
            .form(&CaptchaVerifyRequest {
                secret:   captcha_secret.as_ref(),
                response: g_captcha_response,
            })
            .send()
            .await?
            .json::<CaptchaVerifyResponse>()
            .await?;

        if success && origin_hostname == captcha_hostname {
            return Ok(stream);
        }
    }

    Err(std::io::Error::from(std::io::ErrorKind::InvalidData).into())
}

pub async fn handle_stream<S, F>(
    mut stream: WebSocketStream<S>,
    flag: F,
) -> Result<(), Box<dyn Error>>
where
    S: AsyncRead + AsyncWrite + Unpin,
    F: AsRef<String>,
{
    let board = if let Some(Ok(m)) = stream.next().await {
        let data = m.into_data();
        trace!("Board protobuf bytes: {:02X?}", data.as_slice());
        battleship_prost::Board::decode(data.as_slice())?
    } else {
        return Err(std::io::Error::from(std::io::ErrorKind::InvalidData).into());
    };

    trace!("Decoded board: {:?}", board);

    let mut their_board: Board = board.try_into()?;
    debug!("Opponent board validated.");
    let mut my_board = Board::rand_board(BOARD_WIDTH, BOARD_HEIGHT, &SHIP_LENGTHS).await?;
    debug!("My board: {:?}", my_board);
    let mut turn = STARTING_TURN;
    let mut solver = Solver::new(&my_board, &their_board);


    let mut interval = tokio::time::interval(std::time::Duration::from_millis(TURN_WAIT_MILLIS));
    debug!("Game built.");

    loop {
        interval.tick().await;
        match turn {
            Turn::Mine => {
                let target = solver.next_move(&my_board, &their_board);
                // let missile_result =
                their_board.strike(target);
                stream
                    .send(
                        battleship_prost::Missile {
                            target: target.into(),
                        }
                        .encode_to_vec()
                        .into(),
                    )
                    .await?;

                // if let battleship_prost::missile_result::MissileResult::Miss =
                //     missile_result.missile_result()
                // {
                turn.end_turn()
                // }
            },
            Turn::Opponent => {
                let missile = if let Some(Ok(m)) = stream.next().await {
                    let data = m.into_data();
                    trace!("Missile protobuf bytes: {:02X?}", data.as_slice());
                    battleship_prost::Missile::decode(data.as_slice())?
                } else {
                    return Err(std::io::Error::from(std::io::ErrorKind::InvalidData).into());
                };

                if BoardUnit(missile.target.col) >= my_board.width ||
                    BoardUnit(missile.target.row) >= my_board.height
                {
                    return Err(std::io::Error::from(std::io::ErrorKind::InvalidData).into());
                }

                let target = Point {
                    row: BoardUnit(missile.target.row),
                    col: BoardUnit(missile.target.col),
                };

                debug!("Striking target: {:?}", target);
                let missile_result = my_board.strike(target);

                stream.send(missile_result.encode_to_vec().into()).await?;

                if my_board.ships_left == BoardUnit(0) {
                    stream
                        .send(
                            battleship_prost::Flag {
                                flag: flag.as_ref().to_string(),
                            }
                            .encode_to_vec()
                            .into(),
                        )
                        .await?;
                }

                // if let battleship_prost::missile_result::MissileResult::Miss =
                //     missile_result.missile_result()
                // {
                turn.end_turn()
                // }
            },
        };
    }
}

#[cfg(test)]
mod test {
    use crate::{Board, BoardUnit};

    const BOARD_WIDTH: BoardUnit = BoardUnit(20);
    const BOARD_HEIGHT: BoardUnit = BoardUnit(20);
    const SHIP_LENGTHS: [BoardUnit; 10] = [
        BoardUnit(5),
        BoardUnit(4),
        BoardUnit(3),
        BoardUnit(3),
        BoardUnit(2),
        BoardUnit(5),
        BoardUnit(4),
        BoardUnit(3),
        BoardUnit(3),
        BoardUnit(2),
    ];
    const ITERS: usize = 4096;

    #[test]
    fn rand_counter() {
        let mut results = Vec::with_capacity(ITERS);
        let rng = &mut rand::thread_rng();

        for _ in 0..ITERS {
            let tries = Board::rand_board_internal(rng, BOARD_WIDTH, BOARD_HEIGHT, &SHIP_LENGTHS).1;
            results.push(tries);
        }

        println!("Results: {:?}", results);
    }
}

#[derive(Debug, Clone)]
pub struct WSCallback {
    hostname: Option<String>,
}

impl WSCallback {
    pub fn new() -> Self {
        Self {
            hostname: None
        }
    }

    pub fn hostname(&self) -> &str { self.hostname.as_deref().unwrap() }
}

const BAD_REQUEST: u16 = 400;
const HOST_HEADER_NAME: &str = "Host";
const ORIGIN_HEADER_NAME: &str = "Origin";
const UNAUTHORIZED: u16 = 401;

impl tungstenite::handshake::server::Callback for &mut WSCallback {
    fn on_request(self, request: &Request, response: Response) -> Result<Response, ErrorResponse> {
        fn status(code: u16) -> Result<Response, ErrorResponse> {
            Err(tungstenite::http::Response::builder()
                .status(tungstenite::http::StatusCode::from_u16(code).unwrap())
                .body(None)
                .unwrap())
        }

        let host = request.headers().get(HOST_HEADER_NAME);
        let origin = request.headers().get(ORIGIN_HEADER_NAME);
        debug!(
            "Host and origin [UNTRUSTED AFTER HERE]: {:?}, {:?}",
            host, origin,
        );

        if let (Some(Ok(host)), Some(Ok(origin))) = (
            host.map(HeaderValue::to_str),
            origin.map(HeaderValue::to_str),
        ) {
            if let Ok(origin) = url::Url::parse(origin) {
                if let Some(origin_host) = origin.host() {
                    if host ==
                        match (origin.scheme(), origin.port()) {
                            ("https", Some(port)) => format!("{}:{}", origin_host, port),
                            ("https", None) => format!("{}", origin_host),
                            // TODO: Remove
                            ("http", Some(port)) => format!("{}:{}", origin_host, port),
                            // TODO: Remove
                            ("http", None) => format!("{}", origin_host),
                            _ => return status(UNAUTHORIZED),
                        }
                    {
                        self.hostname = Some(origin_host.to_string());
                        return Ok(response);
                    }
                }
            }
        }

        return status(BAD_REQUEST);
    }
}
