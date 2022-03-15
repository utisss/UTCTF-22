FROM alpine:latest as build

RUN apk update \
    && apk add --no-cache \
    build-base \
    protoc \
    rustup

RUN rustup-init -y --default-toolchain stable --profile minimal

RUN $HOME/.cargo/bin/cargo new --bin battleship

WORKDIR battleship

COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock
COPY static/protos/ static/protos/
COPY build.rs build.rs

RUN $HOME/.cargo/bin/cargo build --release
RUN rm \
    src/*.rs \
    target/release/deps/*battleship*

COPY src/ src/

RUN $HOME/.cargo/bin/cargo build --release \
    && strip -s target/release/battleship

FROM alpine:latest as prod

RUN adduser --disabled-password --system --no-create-home --shell /sbin/nologin appuser \
    && mkdir -p /usr/app

COPY --from=build /battleship/target/release/battleship /usr/app/battleship

RUN chown -R appuser: /usr/app \
    && chmod -R g-rwx,o-rwx /usr/app \
    && chmod -R u+rwX,g+rX /usr/app

EXPOSE 9998/tcp

WORKDIR /usr/app
USER appuser

ENTRYPOINT ["./battleship"]
