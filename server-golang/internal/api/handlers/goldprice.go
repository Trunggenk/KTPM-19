package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/Trunggenk/goldpriceserver/internal/models"
	"github.com/Trunggenk/goldpriceserver/internal/service"
	"github.com/go-chi/chi/v5"
)

// GoldPriceHandler handles HTTP requests for gold prices
type GoldPriceHandler struct {
	service *service.GoldPriceService
}

// NewGoldPriceHandler creates a new gold price handler
func NewGoldPriceHandler(service *service.GoldPriceService) *GoldPriceHandler {
	return &GoldPriceHandler{
		service: service,
	}
}

// GetPrices handles GET requests for gold prices
func (h *GoldPriceHandler) GetPrices(w http.ResponseWriter, r *http.Request) {
	// Set headers
	w.Header().Set("Content-Type", "application/json")

	// Get latest prices from service
	prices, err := h.service.GetLatestPrices(r.Context())
	if err != nil {
		http.Error(w, "Failed to fetch gold prices", http.StatusInternalServerError)
		return
	}

	// If no prices found, return empty array
	if prices == nil {
		prices = []models.GoldPrice{}
	}

	// Encode and return JSON response
	if err := json.NewEncoder(w).Encode(prices); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
		return
	}
}

// GetPriceById handles GET requests to fetch a single gold price by ID
func (h *GoldPriceHandler) GetPriceById(w http.ResponseWriter, r *http.Request) {
	// Set headers
	w.Header().Set("Content-Type", "application/json")

	// Get ID from URL parameter
	id := chi.URLParam(r, "id")
	if id == "" {
		http.Error(w, "Missing ID parameter", http.StatusBadRequest)
		return
	}

	// Get gold price by ID
	price, err := h.service.GetPriceById(r.Context(), id)
	if err != nil {
		http.Error(w, "Failed to fetch gold price", http.StatusInternalServerError)
		return
	}

	// If no price found, return 404
	if price == nil {
		http.Error(w, "Gold price not found", http.StatusNotFound)
		return
	}

	// Encode and return JSON response
	if err := json.NewEncoder(w).Encode(price); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
		return
	}
}

// AddPrices handles POST requests to add gold prices manually
func (h *GoldPriceHandler) AddPrices(w http.ResponseWriter, r *http.Request) {
	// Set headers
	w.Header().Set("Content-Type", "application/json")

	// Decode request body
	var prices []models.GoldPrice
	if err := json.NewDecoder(r.Body).Decode(&prices); err != nil {
		// Try to decode as single object if array fails
		var price models.GoldPrice
		r.Body.Close()
		r.Body = http.MaxBytesReader(w, r.Body, 1048576)
		if err := json.NewDecoder(r.Body).Decode(&price); err != nil {
			http.Error(w, "Invalid request body", http.StatusBadRequest)
			return
		}
		prices = []models.GoldPrice{price}
	}

	// Validate request
	if len(prices) == 0 {
		http.Error(w, "No prices provided", http.StatusBadRequest)
		return
	}

	// Validate required fields for each price
	for _, price := range prices {
		if price.Type == "" || price.Name == "" {
			http.Error(w, "Missing required fields. Required: type, name, buy_price, sell_price", http.StatusBadRequest)
			return
		}
	}

	// Add prices to service
	if err := h.service.AddPricesManually(r.Context(), prices); err != nil {
		http.Error(w, "Failed to add prices", http.StatusInternalServerError)
		return
	}

	// Return success response
	w.WriteHeader(http.StatusCreated)
	response := map[string]interface{}{
		"message": "Prices added successfully",
		"count":   len(prices),
	}
	json.NewEncoder(w).Encode(response)
}
