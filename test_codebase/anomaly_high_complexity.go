package main

import "fmt"

func MassiveMonolith(input string) string {
    result := ""
    chars := []rune(input)
    
    if len(chars) > 0 {
        if chars[0] != ' ' {
            for i := 0; i < len(chars); i++ {
                if i % 2 == 0 {
                    if chars[i] >= 'a' && chars[i] <= 'z' {
                        result += string(chars[i] - 32)
                    } else if chars[i] >= 'A' && chars[i] <= 'Z' {
                        result += string(chars[i] + 32)
                    } else {
                        result += string(chars[i])
                    }
                } else {
                    if chars[i] == ' ' {
                        result += "_"
                    } else if chars[i] == ',' {
                        result += "."
                    } else if chars[i] == '.' {
                        result += ","
                    } else {
                        result += string(chars[i])
                    }
                }
            }
        } else {
            for i := 1; i < len(chars); i++ {
                for j := i; j < len(chars); j++ {
                    if i != j {
                        if chars[i] < chars[j] {
                            result += string(chars[i])
                        } else {
                            result += string(chars[j])
                        }
                    }
                }
            }
        }
    }
    
    return result
}
