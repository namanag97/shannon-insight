package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}

func complexFunction() {
    for i := 0; i < 10; i++ {
        if i%2 == 0 {
            fmt.Println(i)
        } else {
            fmt.Println("odd")
        }
    }
}
