package main

import (
	"net"
	"encoding/pem"
    "encoding/binary"
    "crypto/rsa"
    "crypto/x509"
    "crypto/sha512"
    "crypto/rand"
    "fmt"
)

func encryptWithPublicKey(msg []byte, pub *rsa.PublicKey) []byte {
	hash := sha512.New()
	ciphertext, err := rsa.EncryptOAEP(hash, rand.Reader, pub, msg, nil)
	if err != nil {
		fmt.Println(err)
	}
	return ciphertext
}

func bytesToPublicKey(pub []byte) *rsa.PublicKey {
	block, _ := pem.Decode(pub)
	enc := x509.IsEncryptedPEMBlock(block)
	b := block.Bytes
	var err error
	if enc {
		fmt.Println("is encrypted pem block")
		b, err = x509.DecryptPEMBlock(block, nil)
		if err != nil {
			fmt.Println(err)
		}
	}
	ifc, err := x509.ParsePKIXPublicKey(b)
	if err != nil {
		fmt.Println(err)
	}
	key, ok := ifc.(*rsa.PublicKey)
	if !ok {
		fmt.Println("not ok")
	}
	return key
}

var (
    addr string = "localhost:9855"
)

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func splitLongMessage(msg []byte) [][]byte {
    var result [][]byte
    i := 0
    for i < len(msg) {
        var size int
        if (len(msg)-i) > 254 {
            size = 254
        } else {
            size = len(msg)-i
        }
        result = append(result, msg[i:i+size])
        fmt.Println(string(msg[i:i+size]))
        i += size
    }
    return result
}

func buildDNSRequest(q []byte) []byte {
    queries := splitLongMessage(q)
    req := make([]byte, 0)
    var tID byte = 12
    transactionID := []byte{0x00, tID}
    flags := []byte{0x01, 0x00}
    numQueries := []byte{0x00, byte(len(queries))}
    answerRRs := []byte{0x00, 0x00}
    txtType := []byte{0x00, 0x10}
    class := []byte{0x00, 0x01}
    req = append(req, transactionID...)
    req = append(req, flags...)
    req = append(req, numQueries...)
    req = append(req, answerRRs...)
    req = append(req, answerRRs...)
    req = append(req, answerRRs...)
    for _, query := range queries {
        req = append(req, byte(len(query)))
        fmt.Println("sending query with length", len(query))
        req = append(req, query...)
        req = append(req, byte(0x00))
        req = append(req, txtType...)
        req = append(req, class...)
    }
    return req
}

func collectResponse(msg []byte) []byte {
    var result []byte
    numQueries := binary.BigEndian.Uint16(msg[4:6])
    numAnswers := binary.BigEndian.Uint16(msg[6:8])
    i := 12
    // Loop through queries.
    var q uint16 = 0
    for q < numQueries {
        qSize := msg[i]
        i += int(qSize) + 6
        q += 1
    }
    // Loop through answers.
    var a uint16 = 0
    for a < numAnswers {
        i += 12
        aSize := msg[i]
        i += 1
        result = append(result, msg[i:i+int(aSize)]...)
        i += int(aSize)
        a += 1
    }
    return result
}

func main() {
    raddr, err := net.ResolveUDPAddr("udp", addr)
	check(err)

    conn, err := net.DialUDP("udp", nil, raddr)
    check(err)
	defer conn.Close()

    // Request the public key.
    fmt.Println("Requesting public key ...")
    req := buildDNSRequest([]byte("publickey"))
    _, err = conn.Write(req)
    check(err)

    // Receive the public key.
    buff := make([]byte, 65536)
    n, _, err := conn.ReadFromUDP(buff)
    check(err)
    fmt.Println("Received public key!")
    fmt.Println(string(collectResponse(buff[:n])))
    pubkey := bytesToPublicKey(collectResponse(buff[:n]))

    // Send a command.
    payload := encryptWithPublicKey([]byte("ls -la"), pubkey)
    req = buildDNSRequest(payload)
    _, err = conn.Write(req)
    check(err)
    n, _, err = conn.ReadFromUDP(buff)
    check(err)
    fmt.Println("Received response!")
    fmt.Println(string(collectResponse(buff[:n])))
}
