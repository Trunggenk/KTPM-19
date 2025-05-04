package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/api"
	"github.com/Trunggenk/goldpriceserver/internal/config"
	"github.com/Trunggenk/goldpriceserver/internal/database"
	"github.com/Trunggenk/goldpriceserver/internal/service"
	"github.com/Trunggenk/goldpriceserver/internal/store"
)

func main() {
	// Parse command line flags
	mode := flag.String("mode", "auto", "Server mode: auto or manual")
	port := flag.String("port", "8080", "Server port")
	flag.Parse()

	// Initialize context with cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Initialize config
	cfg := config.New(*mode)

	// Initialize database connection
	dbConfig := database.Config{
		Path: cfg.DatabasePath,
	}
	_, err := database.Connect(dbConfig)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Initialize Redis store
	redisStore, err := store.NewRedisStore(ctx, cfg.RedisConfig)
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	// Initialize cache
	cache := store.NewCache(redisStore)

	// Initialize gold price service with database support
	goldPriceService := service.NewGoldPriceService(ctx, cache, redisStore)

	// Initialize WebSocket service
	wsService := service.NewWebSocketService()

	// Start WebSocket service with Redis store
	wsService.Start(ctx, redisStore)

	// Create router and register handlers
	router := api.NewRouter(goldPriceService, wsService)

	// Create HTTP server
	server := &http.Server{
		Addr:    ":" + *port,
		Handler: router,
	}

	// Create channel for graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	// Start auto-update goroutine if in auto mode
	if cfg.Mode == "auto" {
		log.Println("Starting server in AUTO mode - Will sync data from API automatically")
		go goldPriceService.StartAutoUpdate(ctx, 5*time.Second)
	} else {
		log.Println("Starting server in MANUAL mode - Data will NOT be synced from API")
		// Load initial data
		if err := goldPriceService.FetchInitialData(ctx); err != nil {
			log.Printf("Warning: Failed to load initial data: %v", err)
		}
	}

	// Start server in a goroutine
	go func() {
		log.Printf("Server running on port %s in %s mode", *port, cfg.Mode)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for shutdown signal
	<-stop
	log.Println("Shutting down server...")

	// Create context with timeout for shutdown
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	// Shutdown server gracefully
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("Server shutdown failed: %v", err)
	}

	// Cancel the context to stop all operations
	cancel()
	log.Println("Server stopped gracefully")
}
