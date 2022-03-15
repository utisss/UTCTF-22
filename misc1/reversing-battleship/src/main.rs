#[macro_use]
extern crate log;

use std::error::Error;
use std::sync::Arc;


const IP_VAR_NAME: &str = "IP";
const PORT_VAR_NAME: &str = "PORT";
const FLAG_VAR_NAME: &str = "FLAG";
const CAPTCHA_SECRET_VAR_NAME: &str = "CAPTCHA_SECRET";
const LOG_LEVEL_VAR_NAME: &str = "RUST_LOG";

fn configure_logging() -> std::io::Result<()> {
    if std::env::var(LOG_LEVEL_VAR_NAME).is_err() {
        #[cfg(debug_assertions)]
        {
            std::env::set_var("RUST_LOG", "debug")
        }
        #[cfg(not(debug_assertions))]
        {
            std::env::set_var("RUST_LOG", "info")
        }
    }

    env_logger::init();

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    configure_logging()?;

    let ip = std::env::var(IP_VAR_NAME)
        .unwrap_or(format!("::"))
        .parse()?;
    let port = std::env::var(PORT_VAR_NAME)
        .unwrap_or(format!("9998"))
        .parse()?;
    let flag = Arc::new(std::env::var(FLAG_VAR_NAME).unwrap_or(format!("utflag{{TESTING_ONLY}}")));
    let captcha_secret = Arc::new(std::env::var(CAPTCHA_SECRET_VAR_NAME)?);
    let listener = tokio::net::TcpListener::bind(std::net::SocketAddr::new(ip, port)).await?;

    info!("Binding to IP: {}", ip);
    info!("Using port: {}", port);

    info!("Initialization complete.");
    loop {
        debug!("Waiting for new connection...");
        let stream = match listener.accept().await {
            Ok((stream, _)) => stream,
            Err(err) => {
                warn!("Error accepting TCP connection: {}", err);
                continue;
            },
        };

        let flag = Arc::clone(&flag);
        let captcha_secret = Arc::clone(&captcha_secret);
        tokio::spawn(async move {
            let mut ws_callback = battleship::WSCallback::new();
            let stream = match tokio_tungstenite::accept_hdr_async(stream, &mut ws_callback).await {
                Ok(stream) => stream,
                Err(err) => {
                    warn!("Error establishing websocket connection: {}", err);
                    return;
                },
            };

            let stream =
                match battleship::validate_captcha(stream, captcha_secret, ws_callback.hostname())
                    .await
                {
                    Ok(stream) => stream,
                    Err(err) => {
                        debug!("Error validating captcha: {}", err);
                        return;
                    },
                };

            if let Err(err) = battleship::handle_stream(stream, flag).await {
                debug!("Error processing stream: {}", err);
            }
        });
    }
}
