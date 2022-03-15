// global vars
let domain = location.host // + ':9998'; //TODO: update w/ utctf domain once assigned
let ws = null;

let protoRoot = null;
protobuf.load('./protos/battleship.proto').then((root) => protoRoot = root);

let grid = [];
let boardWidth = 20;
let boardHeight = 20;
const ships = ['Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer', 'Carrier', 'Battleship', 'Cruiser', 'Submarine', 'Destroyer'];
const shipsLen = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine': 3, 'Destroyer': 2};
let shipIdx = 0;
let curShip = {
    name: "Carrier",
    len: 5,
    isVertical: true,
    topCoord: [0, 0]
};
let canFire = false;
let myTurn = false;
let serverShipsLeft = ships.length;

// captcha global vars
let siteKey = "6LfNK8EeAAAAAPDVHxIS3EPDqpUKlk2ARUGq2Hh8";
let gCaptchaResponse = "";
let gameStarted = false;

captchaOnload = function () {
    grecaptcha.render('captcha', {
        "sitekey": siteKey,
        "theme": "dark",
        "size": "normal",
        "callback": "captchaSuccessCallback",
        "error-callback": "captchaErrorCallback"
    });
}

captchaSuccessCallback = function(token) {
    if (!gameStarted) {
        // make captcha disappear
        document.getElementById('captcha').hidden = true;
        gCaptchaResponse = token;
        ws = connToServer();
    }
}

captchaErrorCallback = function () {
    if (!gameStarted) {
        alert('An error occurred with the captcha :(');
    }
}

window.onload = function (){
    // create and add board pieces
    let myBoard = $('#myBoard');
    let oppBoard = $('#oppBoard');
    for(let r = 0; r < boardHeight; r++){
        let gridRow = [];
        let myRow = $('<div>').addClass('row');
        let oppRow = $('<div>').addClass('row');
        for(let c = 0; c < boardWidth; c++){
            let myBoardPiece = $('<div>').addClass('col board-piece');
            myRow.append(myBoardPiece);
            gridRow.push(myBoardPiece);
            let oppBoardPiece = $('<div>').addClass('col board-piece opp-board-piece').attr('id', r + ',' + c);
            oppBoardPiece.on('click', function(event) {
                if(canFire){
                    canFire = false;
                    let pos = this.id.split(',');
                    sendMissile(ws, pos);
                }
                event.stopPropagation();
            });
            oppRow.append(oppBoardPiece);
        }
        myBoard.append(myRow);
        oppBoard.append(oppRow);
        grid.push(gridRow);
    }

    putShipOnPos(curShip, curShip.topCoord);
    // add event listener to place all ships
    document.addEventListener('keydown', placeShips);
}


function placeShips(e){
    switch(e.key){
        case "Enter":
            // Enter pressed
            // check pos valid
            if(checkValidPos()){
                // update ships arr to record ship info
                ships[shipIdx] = {
                    start: {
                        row: curShip.topCoord[0],
                        col: curShip.topCoord[1]
                    },
                    orientation: curShip.isVertical? 0 : 1,
                    length: curShip.len
                };
                // mark board pieces as occupied
                // don't do it here to handle doing the captcha at the end
                //$('.cur-pos').addClass('occupied-pos').removeClass('cur-pos');
                // move on to next ship if there are more
                if(shipIdx < ships.length - 1){
                    // mark board pieces as occupied
                    $('.cur-pos').addClass('occupied-pos').removeClass('cur-pos');
                    shipIdx++;
                    curShip.name = ships[shipIdx];
                    curShip.len = shipsLen[curShip.name]
                    // give user instructions
                    $('#userInstruc').html('Place your ' + curShip.name + ' (' + curShip.len + ' units) on the board. Use arrow keys to move, space to rotate ship, and enter to finalize the positioning.');
                    putShipOnPos(curShip, [0,0]);
                } else {
                    if(gameStarted){
                        // mark board pieces as occupied
                        $('.cur-pos').addClass('occupied-pos').removeClass('cur-pos');
                        sendBoardConfig();
                        document.removeEventListener('keydown', placeShips);
                        canFire = true;
                        myTurn = true;
                        $('#userInstruc').html("Choose a position on your opponent's board to target");
                    } else {
                        // game not yet started, so try to set up board again
                        alert('You have not verified that you are a human');
                    }
                }
            }
            break;

        case "ArrowLeft":
            // Left pressed
            // make sure not already at leftmost pos
            if(curShip.topCoord[1] > 0){
                putShipOnPos(curShip, [curShip.topCoord[0], curShip.topCoord[1] - 1]);
            }
            break;
        case "ArrowRight":
            // Right pressed
            // make sure not already at rightmost pos
            let botmC = curShip.topCoord[1] + (curShip.isVertical ? 0 : curShip.len - 1);
            if(botmC < boardWidth - 1){
                putShipOnPos(curShip, [curShip.topCoord[0], curShip.topCoord[1] + 1]);
            }
            break;
        case "ArrowUp":
            // Up pressed
            // make sure not already at topmost pos
            if(curShip.topCoord[0] > 0){
                putShipOnPos(curShip, [curShip.topCoord[0] - 1, curShip.topCoord[1]]);
            }
            break;
        case "ArrowDown":
            // Down pressed
            // make sure not already at bottommost pos
            let botmR = curShip.topCoord[0] + (curShip.isVertical ? curShip.len - 1: 0);
            if(botmR < boardHeight - 1){
                putShipOnPos(curShip, [curShip.topCoord[0] + 1, curShip.topCoord[1]]);
            }
            break;
        case " ":
            // Space pressed
            // make sure have enough space to rotate
            if( (curShip.isVertical && curShip.topCoord[1] + curShip.len - 1 < boardWidth)
                || (!curShip.isVertical && curShip.topCoord[0] + curShip.len - 1 < boardHeight) ){
                curShip.isVertical = !curShip.isVertical;
                putShipOnPos(curShip, curShip.topCoord);
            }
    }
}

function putShipOnPos(ship, newPos) {
    $('.cur-pos').removeClass('cur-pos');
    // mark squares on board for ship's cur pos
    let r = newPos[0];
    let c = newPos[1];
    for(let i = 0; i < ship.len; i++){
        if(ship.isVertical)
            grid[r + i][c].addClass('cur-pos');
        else
            grid[r][c + i].addClass('cur-pos');
    }
    ship.topCoord = newPos;
    checkValidPos();
}

function checkValidPos() {
    $('.board-piece').removeClass('invalid-pos');
    // find if this is over another ship; if so, color it red
    let invalid = $('.cur-pos').hasClass('occupied-pos');
    if(invalid){
        $('.cur-pos').addClass('invalid-pos');
    }
    return !invalid;
}

function connToServer(){
    let ws = new WebSocket("ws://" + domain + '/websocket');
    ws.binaryType = 'arraybuffer';
    ws.onopen = function() {
        let InitializeMessage = protoRoot.lookupType('battleship.Initialize');
        let initializeGame = InitializeMessage.encode(InitializeMessage.fromObject({ gCaptchaResponse: gCaptchaResponse })).finish();
        ws.send(initializeGame);
        gameStarted = true;
    }
    return ws;
}

function sendBoardConfig(){
    // send board config
    let board = {
        width: grid[0].length,
        height: grid.length,
        ships: ships
    }
    let BoardMessage = protoRoot.lookupType('battleship.Board');
    let boardConfig = BoardMessage.encode(BoardMessage.fromObject(board)).finish();
    console.log(boardConfig);
    ws.send(boardConfig);
}

function sunkWholeShip(){
    // go through to see if any whole ship sunk
    for(let i = 0; i < ships.length; i++) {
        let shipSunk = true;
        for (let j = 0; j < ships[i].length; j++) {
            let r = ships[i].start.row + (ships[i].orientation ? 0 : j);
            let c = ships[i].start.col + (ships[i].orientation ? j : 0);
            if (!grid[r][c].hasClass('hit')) {
                shipSunk = false;
            }
        }
        if (shipSunk)
            return ships.splice(i, 1)[0];
    }
    return null;
}

function sendMissile(ws, pos){
    // send out the missile
    let MissileMessage = protoRoot.lookupType('battleship.Missile');
    let sendMissile = MissileMessage.encode(MissileMessage.create({target: {row:pos[0], col: pos[1]}})).finish();
    console.log(sendMissile);
    ws.send(sendMissile);
    ws.onmessage = function (response) {
        let MissileResult = protoRoot.lookupType('battleship.MissileResult');
        let buffer = new Uint8Array(response.data);
        if(myTurn) {
            // response was missile result
            let result = MissileResult.toObject(MissileResult.decode(buffer));
            console.log(result);
            let targetPiece = document.getElementById(pos[0] + ',' + pos[1]);
            if(result.missileResult === 1) {
                // missed; mark that
                console.log('missed mark at ' + pos[0] + ', ' + pos[1]);
                targetPiece.classList.add('missed');
            } else {
                // hit; mark that
                console.log('hit mark at ' + pos[0] + ', ' + pos[1]);
                targetPiece.classList.add('hit');
                // sunk a whole ship?
                if(result.shipSunk) {
                    serverShipsLeft--;
                    for(let i = 0; i < result.shipSunk.length; i++){
                        let r = result.shipSunk.start.row + (result.shipSunk.orientation ? 0 : i);
                        let c = result.shipSunk.start.col + (result.shipSunk.orientation ? i : 0);
                        document.getElementById(r + ',' + c).classList.add('ship_sunk');
                    }
                }
            }
            // my turn over
            myTurn = false;
        } else {
            // server either sending missile or flag
            if(serverShipsLeft === 0) {
                // server's ships all sunk! they're giving us the flag :)
                let flagMessage = protoRoot.lookupType('battleship.Flag');
                let flag = flagMessage.toObject(flagMessage.decode(buffer));
                $('#userInstruc').html(flag.flag);
                ws.close();
            } else {
                // server sending a missile
                let serverMissile = MissileMessage.toObject(MissileMessage.decode(buffer));
                let r = serverMissile.target.row;
                let c = serverMissile.target.col;
                if (grid[r][c].hasClass('occupied-pos')) {
                    // server hit one of our ships; mark that
                    grid[r][c].addClass('hit');
                    let sunkShip = sunkWholeShip();
                    if (sunkShip) {
                        // mark ships as sunk
                        for (let i = 0; i < sunkShip.length; i++) {
                            let r = sunkShip.start.row + (sunkShip.orientation ? 0 : i);
                            let c = sunkShip.start.col + (sunkShip.orientation ? i : 0);
                            grid[r][c].addClass('ship_sunk');
                        }
                        // sunk all ships?
                        if (ships.length === 0) {
                            $('#userInstruc').html('All your ships are sunk! You lose XP');
                            ws.close();
                        }
                    }
                } else {
                    // server missed; mark that
                    grid[r][c].addClass('missed');
                }

                // server's turn over
                myTurn = true;
                canFire = true;
            }
        }

    }
}
