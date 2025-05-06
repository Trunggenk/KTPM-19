package service

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/store"
	"github.com/gorilla/websocket"
)

// WebSocketService handles WebSocket connections
type WebSocketService struct {
	redisStore   *store.RedisStore
	upgrader     websocket.Upgrader
	clients      map[*websocket.Conn]bool
	clientsMutex sync.RWMutex
	broadcast    chan []byte
}

// NewWebSocketService creates a new WebSocket service
func NewWebSocketService() *WebSocketService {
	return &WebSocketService{
		upgrader: websocket.Upgrader{
			ReadBufferSize:  1024,
			WriteBufferSize: 1024,
			CheckOrigin: func(r *http.Request) bool {
				return true // In production, implement proper origin checking
			},
		},
		clients:   make(map[*websocket.Conn]bool),
		broadcast: make(chan []byte, 256),
	}
}

// Start starts the WebSocket service
func (s *WebSocketService) Start(ctx context.Context, redisStore *store.RedisStore) {
	s.redisStore = redisStore

	// Start goroutine for broadcasting messages to all clients
	go s.broadcastMessages(ctx)

	// Start goroutine for subscribing to Redis updates
	go s.subscribeToRedisUpdates(ctx)
}

// HandleConnection handles a new WebSocket connection
func (s *WebSocketService) HandleConnection(w http.ResponseWriter, r *http.Request) {
	// Kiểm tra kết nối Socket.IO và chuyển hướng sang WebSocket thuần túy
	if strings.Contains(r.URL.Path, "/socket.io/") {
		// Trả về thông tin tương thích Socket.IO để client kết nối WebSocket
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"websocket":true,"path":"/ws"}`))
		return
	}

	// Upgrade HTTP connection to WebSocket
	conn, err := s.upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("Failed to upgrade connection: %v", err)
		return
	}

	// Register new client
	s.clientsMutex.Lock()
	s.clients[conn] = true
	s.clientsMutex.Unlock()

	// Start goroutine to handle connection read/write
	go s.handleClient(conn)
}

// handleClient handles client WebSocket communication
func (s *WebSocketService) handleClient(conn *websocket.Conn) {
	defer func() {
		// Unregister client when done
		s.clientsMutex.Lock()
		delete(s.clients, conn)
		s.clientsMutex.Unlock()
		conn.Close()
	}()

	// Set ping handler
	conn.SetPingHandler(func(data string) error {
		return conn.WriteControl(websocket.PongMessage, []byte(data), time.Now().Add(time.Second))
	})

	// Send current gold prices upon connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	prices, err := s.redisStore.GetGoldPrices(ctx)
	if err == nil && len(prices) > 0 {
		if data, err := json.Marshal(prices); err == nil {
			conn.WriteMessage(websocket.TextMessage, data)
		}
	}

	// Simple read loop - we don't expect client messages but need to keep connection alive
	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			// Client disconnected or error occurred
			break
		}
	}
}

// broadcastMessages broadcasts messages to all connected clients
func (s *WebSocketService) broadcastMessages(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		case message := <-s.broadcast:
			s.clientsMutex.RLock()
			for conn := range s.clients {
				go func(c *websocket.Conn, msg []byte) {
					if err := c.WriteMessage(websocket.TextMessage, msg); err != nil {
						// If write fails, close connection
						c.Close()
						s.clientsMutex.Lock()
						delete(s.clients, c)
						s.clientsMutex.Unlock()
					}
				}(conn, message)
			}
			s.clientsMutex.RUnlock()
		}
	}
}

// subscribeToRedisUpdates subscribes to Redis updates and forwards them to WebSocket clients
func (s *WebSocketService) subscribeToRedisUpdates(ctx context.Context) {
	prices, err := s.redisStore.SubscribeToGoldPrices(ctx)
	if err != nil {
		log.Printf("Failed to subscribe to Redis updates: %v", err)
		return
	}

	for {
		select {
		case <-ctx.Done():
			return
		case priceData, ok := <-prices:
			if !ok {
				return
			}
			// Marshal data for broadcast
			data, err := json.Marshal(priceData)
			if err != nil {
				continue
			}
			// Send to broadcast channel
			select {
			case s.broadcast <- data:
			default:
				// Drop message if channel buffer is full
			}
		}
	}
}
