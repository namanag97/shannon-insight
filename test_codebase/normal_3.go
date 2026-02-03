package main

import "fmt"

type Data struct {
    Value int
}

func (d Data) Process() {
    fmt.Println(d.Value)
}
