FROM alpine:latest as build

RUN apk update \
    && apk add --no-cache \
    libsodium-dev \
    build-base

WORKDIR working

COPY ./app.c ./app.c

RUN gcc -o app -O3 app.c -lsodium


FROM alpine:latest as prod

RUN apk update \
    && apk add --no-cache \
    libsodium

RUN adduser --disabled-password --system --no-create-home --shell /sbin/nologin appuser \
    && mkdir -p /usr/app

COPY --from=build /working/app /usr/app/app

RUN chown -R appuser: /usr/app \
    && chmod -R g-rwx,o-rwx /usr/app \
    && chmod -R u+rwx,g+rX /usr/app

ENV PORT=3000
EXPOSE 3000/tcp

WORKDIR /usr/app
USER appuser

ENTRYPOINT ["./app"]
