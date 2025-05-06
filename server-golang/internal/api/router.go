package api

import (
	"net/http"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/api/handlers"
	custommiddleware "github.com/Trunggenk/goldpriceserver/internal/api/middleware"
	"github.com/Trunggenk/goldpriceserver/internal/service"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

// NewRouter creates a new router with all routes
func NewRouter(goldService *service.GoldPriceService, wsService *service.WebSocketService) http.Handler {
	r := chi.NewRouter()

	// Standard Chi middleware
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))

	// Custom middleware
	r.Use(custommiddleware.CORS)

	// Create handlers
	goldHandler := handlers.NewGoldPriceHandler(goldService)

	// API routes
	// Endpoints phù hợp với server.js
	r.Get("/api/gold-prices", goldHandler.GetPrices)
	r.Get("/api/get/{id}", goldHandler.GetPriceById)
	r.Post("/api/add", goldHandler.AddPrices)

	// WebSocket endpoint
	r.Get("/ws", wsService.HandleConnection)

	// Socket.IO endpoint (cho tương thích với client Socket.IO)
	r.Get("/socket.io/*", wsService.HandleConnection)

	// Serve static files
	fileServer := http.FileServer(http.Dir("./static"))
	r.Handle("/*", fileServer)

	return r
}
