FROM ubuntu

COPY osint-full /osint-full
COPY token.json /token.json
COPY credentials.json /credentials.json
COPY go.mod /go.mod
COPY go.sum /go.sum
COPY quickstart.go /quickstart.go
RUN apt update
RUN apt install -y apt-transport-https ca-certificates
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt -y install tzdata
RUN apt update && apt install golang-go -y
ENTRYPOINT ["./osint-full"]
