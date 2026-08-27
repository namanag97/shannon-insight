package main

import (
	"fmt"
	"strings"
)

func Sum(nums []int) int {
	total := 0
	for _, n := range nums {
		if n%2 == 0 {
			total += n
		}
	}
	return total
}

func Greet(name string) string {
	if name == "" {
		name = "world"
	}
	return strings.ToUpper(fmt.Sprintf("hi %s", name))
}
