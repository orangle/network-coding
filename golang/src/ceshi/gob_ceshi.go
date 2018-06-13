package main

import (
	"fmt"
	"encoding/gob"
	"bytes"
)

// struct 的属性如果不是首字母大写，gob就不好使
type message struct {
	Response int32
	Request  int32
}


func main() {
	var msg message
	msg.Request = 20
	msg.Response = 50
	fmt.Println(msg)
	//fmt.Printf("%+v\n", msg)

	var network bytes.Buffer
	enc := gob.NewEncoder(&network)
	err := enc.Encode(msg)
	if err != nil {
		panic(err)
	}
	fmt.Println(network)

	var dmsg message
	dec := gob.NewDecoder(&network)
	err = dec.Decode(&dmsg) 
	fmt.Println(dmsg)
}