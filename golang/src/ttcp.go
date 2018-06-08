package main 

import (
	"strconv"
	"io"
	"time"
	"encoding/binary"
	"flag"
	"fmt"
	"net"
)

// SessionMessage xx
type SessionMessage struct {
	Number, Length int32
}

type options struct {
	port int
	length int 
	number int 
	transmit bool 
	receive bool 
	nodelay bool 
	host string 
}

var opt options

func init() {
	flag.IntVar(&opt.port, "p", 5001, "TCP port")
	flag.IntVar(&opt.length, "l", 65535, "Buffer length")
	flag.IntVar(&opt.number, "n", 8192, "number of buffers")
	flag.BoolVar(&opt.receive, "r", false, "Receive")
	flag.StringVar(&opt.host, "h", "", "host")
	// ??
	check(binary.Size(SessionMessage{}) == 8, "packed struct")
}

func check(v bool, msg string) {
	if !v {
		panic(msg)
	}
}

func panicOnError(err error){
	if err != nil {
		panic(err)
	}
}

func listenTCPOrDie(listenAddr string) net.Listener {
	listener, err := net.Listen("tcp", listenAddr)
	panicOnError(err)
	return listener
}

func transmit() {
	fmt.Println("client start ....")
	sm := SessionMessage{int32(opt.number), int32(opt.length)}
	fmt.Printf("buffer length = %d\nnumber of buffers = %d\n",
			sm.Length, sm.Number)
	totalMb := float64(sm.Number) * float64(sm.Length) / 1024.0 / 1024.0
	fmt.Printf("%.3f MiB in total\n", totalMb)

	conn, err := net.Dial("tcp", net.JoinHostPort(opt.host, strconv.Itoa(opt.port)))
	panicOnError(err)
	// t := conn.(*net.TCPConn)
	// t.SetNoDelay(false)
	defer conn.Close()

	start := time.Now()
	err = binary.Write(conn, binary.BigEndian, &sm)
	panicOnError(err)

	totalLen := 4 + opt.length // binary.Size(int32(0)) == 4
	payload := make([]byte, totalLen)
	binary.BigEndian.PutUint32(payload, uint32(opt.length))
	for i := 0; i < opt.length; i++ {
		payload[4+i] = "0123456789ABCDEF"[i%16]
	}

	for i := 0; i < opt.number; i++ {
		var n int
		n, err = conn.Write(payload)
		panicOnError(err)
		check(n == len(payload), "write payload")

		var ack int32
		err = binary.Read(conn, binary.BigEndian, &ack)
		panicOnError(err)
		check(ack == int32(opt.length), "ack")
	}

	elapsed := time.Since(start).Seconds()
	fmt.Printf("%.3f seconds\n%.3f MiB/s\n", elapsed, totalMb/elapsed)
}


func receive() {
	fmt.Println("server start ...")
	server := listenTCPOrDie(fmt.Sprintf(":%d", opt.port))
	defer server.Close()
	fmt.Println("Listen on ", server.Addr().String())
	conn, err := server.Accept()
	panicOnError(err)
	defer conn.Close()

	var sm SessionMessage
	err = binary.Read(conn, binary.BigEndian, &sm)
	panicOnError(err)

	//first message
	fmt.Printf("receive buffer length = %d\nreceive number of buffers = %d\n",
			sm.Length, sm.Number)

	totalMb := float64(sm.Number) * float64(sm.Length) / 1024 / 1024
	fmt.Printf("%.3f MiB in total\n", totalMb)

	payload := make([]byte, sm.Length)
	start := time.Now()

	for i:=0; i < int(sm.Number); i++ {
		var length int32
		err = binary.Read(conn, binary.BigEndian, &length)
		panicOnError(err)
		//fmt.Println(length, sm.Length)
		check(length == sm.Length, "read length")
		
		var n int 
		n, err = io.ReadFull(conn, payload)
		panicOnError(err)
		check(n == len(payload), "read payload")
		err = binary.Write(conn, binary.BigEndian, &length)
		panicOnError(err)
	}

	elapsed := time.Since(start).Seconds()
	fmt.Printf("%.3f seconds\n%.3f MiB/s\n", elapsed, totalMb/elapsed)
}

func main() {
	flag.Parse()
	// ??
	opt.transmit = opt.host != ""
	if opt.transmit == opt.receive {
		println("Either -r or -t must be specified.")
		return 
	}

	if opt.transmit {
		transmit()
	} else if opt.receive {
		receive()
	} else {
		panic("unknow")
	}
}