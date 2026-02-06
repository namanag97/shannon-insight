// Sample Go file for testing tree-sitter parsing.
package sample

import (
	"fmt"
	"os"
)

// Greeter interface for greeting behavior.
type Greeter interface {
	Greet(name string) string
}

// HelloGreeter implements Greeter.
type HelloGreeter struct {
	Prefix string
}

// Greet returns a greeting message.
func (h *HelloGreeter) Greet(name string) string {
	return fmt.Sprintf("%s, %s!", h.Prefix, name)
}

// standalone function
func ProcessData(data []int) int {
	sum := 0
	for _, v := range data {
		if v > 0 {
			for i := 0; i < v; i++ {
				sum += i
			}
		}
	}
	return sum
}

func main() {
	g := &HelloGreeter{Prefix: "Hello"}
	fmt.Println(g.Greet("World"))
	os.Exit(0)
}
