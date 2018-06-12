package main 

import (
	"time"
	"fmt"
	"net"
	"os"
	"io"
)

const (
	HOST = "localhost"
	PORT = "5002"
)

func main() {
	addr, err := net.ResolveTCPAddr("tcp", HOST + ":" + PORT)
	exitOnPainc(err)

	listener, err := net.ListenTCP("tcp", addr)
	exitOnPainc(err)

	fmt.Println("listen on port", PORT)

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println(err)
		} else {
			go echo(conn)
		}
	}
}

func echo(conn net.Conn) {
	defer conn.Close()
	defer fmt.Println("close conn")

	fmt.Printf("Connect to %s\n", conn.RemoteAddr().String())
	for {
		buf := make([]byte, 512)
		_, err := conn.Read(buf)
		if err == io.EOF {
			return 
		}

		if err != nil {
			fmt.Println("Error reading")
			fmt.Println(err)
			continue
		}

		fmt.Println(fmt.Sprintf("recive [%s] %s", conn.RemoteAddr().String(), string(buf)))

		daytime := time.Now().String()
		buf = append(buf, " "...)
		buf = append(buf, daytime...)
		_, err = conn.Write(buf)
		fmt.Println(fmt.Sprintf("send [%s] %s", conn.RemoteAddr().String(), string(buf)))
		if err != nil {
			fmt.Println("Error writing")
			fmt.Println(err)
			continue
		}
	}
}


func exitOnPainc(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}