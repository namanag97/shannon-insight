package util

import "example.com/m/config"

func Go() string {
	return "go:" + config.Name()
}
