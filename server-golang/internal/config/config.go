package config

import (
	"github.com/Trunggenk/goldpriceserver/internal/store"
)

// Config represents application configuration
type Config struct {
	Mode         string
	RedisConfig  store.RedisConfig
	DatabasePath string
}

// New creates a new configuration with the specified mode
func New(mode string) *Config {
	// Set default Redis configuration
	redisConfig := store.RedisConfig{
		Address:  "localhost:6379",
		Password: "", // No password by default
		DB:       0,  // Default DB
	}

	return &Config{
		Mode:         mode,
		RedisConfig:  redisConfig,
		DatabasePath: "goldprices.db", // SQLite database path
	}
}
