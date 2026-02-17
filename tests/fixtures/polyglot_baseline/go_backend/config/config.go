package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port        string
	DatabaseURL string
	JWTSecret   string
	Environment string
	LogLevel    string
	MaxWorkers  int
}

func LoadConfig() (*Config, error) {
	cfg := &Config{
		Port:        getEnv("PORT", "8080"),
		DatabaseURL: getEnv("DATABASE_URL", "postgres://localhost/backend_db"),
		JWTSecret:   getEnv("JWT_SECRET", "your-secret-key"),
		Environment: getEnv("ENVIRONMENT", "development"),
		LogLevel:    getEnv("LOG_LEVEL", "info"),
		MaxWorkers:  getEnvInt("MAX_WORKERS", 10),
	}

	if err := cfg.Validate(); err != nil {
		return nil, err
	}

	return cfg, nil
}

func (c *Config) Validate() error {
	if c.Port == "" {
		return fmt.Errorf("PORT configuration is required")
	}

	if c.DatabaseURL == "" {
		return fmt.Errorf("DATABASE_URL configuration is required")
	}

	if c.JWTSecret == "" {
		return fmt.Errorf("JWT_SECRET configuration is required")
	}

	if c.MaxWorkers <= 0 {
		return fmt.Errorf("MAX_WORKERS must be greater than 0")
	}

	return nil
}

func (c *Config) IsDevelopment() bool {
	return c.Environment == "development"
}

func (c *Config) IsProduction() bool {
	return c.Environment == "production"
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvInt(key string, defaultValue int) int {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	intValue, err := strconv.Atoi(value)
	if err != nil {
		return defaultValue
	}

	return intValue
}
