package main

import (
	"fmt"

	"example.com/m/config"
	"example.com/m/util"
)

func main() {
	fmt.Println(util.Go(), config.Name())
}
