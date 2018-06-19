package main 
/*
go run roundtrip.go -s

go run roundtrip.go -c 3
在没有启动server的时候，为啥client也会有read event呢?
*/

import (
	"encoding/gob"
	"bytes"
	"fmt"
	"flag"
	"time"
	"net"
)

const (
	PORT = ":8089"
)

type Message struct {
	Request, Response int64
}

func panicOnError(err error){
	if err != nil {
		panic(err)
	}
}

func getTs() int64 {
	return int64(time.Now().UnixNano()) / 1000  	
}

func client(count int, interval int) {
	//两个go 一个发送，一个接受，sleep就好
	addr, err:= net.ResolveUDPAddr("udp", PORT)
	panicOnError(err)
	fmt.Printf("client connect to %s, count %d, interval %d\n", PORT, count, interval)

	conn, err := net.DialUDP("udp", nil, addr)	
	panicOnError(err)	
	defer conn.Close()

	go func(){
		for i:=0; i<count; i++ {
			var msg Message	
			msg.Request = getTs() 
			//fmt.Printf("send %+v\n", msg)	

			var buffer bytes.Buffer
			encoder := gob.NewEncoder(&buffer)
			encoder.Encode(msg)
			conn.Write(buffer.Bytes())
			buffer.Reset()

			panicOnError(err)
			time.Sleep(time.Duration(interval) * time.Second)
		}
	}()

	for i:=0; i<count; i++ {
		var req Message
		inputBytes := make([]byte, 4096)
		//length, _, err:= conn.ReadFromUDP(inputBytes)
		length, err:= conn.Read(inputBytes)
		if err != nil {
			fmt.Println("get msg length", length, err)
			continue
		}
		buffer := bytes.NewBuffer(inputBytes[:length])
		decoder := gob.NewDecoder(buffer)
		decoder.Decode(&req)
		//fmt.Printf("get %+v\n", req)
		back := getTs() 
		mine := (back + req.Request) / 2
		//fmt.Println(back, req.Response, req.Request, mine)
		fmt.Printf("%d :now %d round trip %d clock error %d\n", 
			i, back, back - req.Request, req.Response - mine)
		//time.Sleep(time.Duration(interval) * time.Second)
	}
}

func server() {
	//收到请求，填充时间，然后发送回去
	addr, err:= net.ResolveUDPAddr("udp", PORT)
	panicOnError(err)
	conn, err:= net.ListenUDP("udp", addr)
	panicOnError(err)

	fmt.Println("server listen upd", conn.LocalAddr().String())
	defer conn.Close()

	for {
		var req Message
		inputBytes := make([]byte, 4096)
		length, addr, err:= conn.ReadFromUDP(inputBytes)
		if err != nil {
			fmt.Printf("error during read: %s", err)
		}

		buffer := bytes.NewBuffer(inputBytes[:length])
		//fmt.Println(buffer)
		decoder := gob.NewDecoder(buffer)
		decoder.Decode(&req)
		fmt.Printf("[%s] get %+v\n", addr, req)

		//time.Sleep(5 * time.Second)
		req.Response = getTs() 
		var buffer2 bytes.Buffer
		encoder2 := gob.NewEncoder(&buffer2)
		encoder2.Encode(req)
		conn.WriteToUDP(buffer2.Bytes(), addr)
		fmt.Printf("[%s] send %+v\n", addr, req)
		buffer2.Reset()
		fmt.Println("")
	}
}

func main() {
	isServer := flag.Bool("s", false, "is server")
	count := flag.Int("c", 10, "total count") 
	interval := flag.Int("i", 1, "send msg interval seconds")
	flag.Parse()

	if *isServer {
		server()
	} else {
		client(*count, *interval)
	}
}