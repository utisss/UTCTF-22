FROM golang:alpine

RUN mkdir /app
ADD . /app/
WORKDIR /app

RUN go build server.go

CMD ["./server"]
