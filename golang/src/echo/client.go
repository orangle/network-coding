package main

import (
	"fmt"
	"os"
	"time"
	"net"
	"io"
)

const (
	HOST = "localhost"
	PORT = "5002"
	PING_PERIOD = 1 * time.Second
)

func main() {
	serveraddr, err := net.ResolveTCPAddr("tcp", HOST + ":" + PORT)
	exitOnPainc(err)

	conn, err := net.DialTCP("tcp", nil, serveraddr)
	exitOnPainc(err)
	fmt.Printf("connect server %s\n", serveraddr)
	for {
		time.Sleep(PING_PERIOD)
		ping(conn, "hello")
	}
}


func ping(conn net.Conn, msg string) {
	_, err := conn.Write([]byte(msg))
	exitOnPainc(err)
	fmt.Println("Send", msg)
	buf := make([]byte, 1024)

	_, err = conn.Read(buf)
	if err != nil {
		if err != io.EOF {
			fmt.Println("read error:", err)
		}
	}
	fmt.Println("Get", string(buf))
}


func exitOnPainc(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}