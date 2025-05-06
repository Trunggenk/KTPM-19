package fetcher

import (
	"context"
	"net/http"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/models"
)

const (
	goldPriceAPIURL = "https://api.example.com/goldprices" // Replace with actual API URL
)

// GoldPriceFetcher fetches gold prices from external API
type GoldPriceFetcher struct {
	client *http.Client
}

// NewGoldPriceFetcher creates a new GoldPriceFetcher
func NewGoldPriceFetcher() *GoldPriceFetcher {
	return &GoldPriceFetcher{
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// Fetch fetches gold prices from the API
func (f *GoldPriceFetcher) Fetch(ctx context.Context) ([]models.GoldPrice, error) {
	// Sử dụng dữ liệu mock thay vì gọi API không tồn tại
	// Trong môi trường production, bạn sẽ bỏ đoạn code này và sử dụng API thật
	return f.MockFetch(), nil

	// Code gọi API thật - tạm thời comment lại
	/*
		// Create a new request
		req, err := http.NewRequestWithContext(ctx, http.MethodGet, goldPriceAPIURL, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create request: %w", err)
		}

		// Set headers
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Accept", "application/json")

		// Execute the request
		resp, err := f.client.Do(req)
		if err != nil {
			return nil, fmt.Errorf("failed to execute request: %w", err)
		}
		defer resp.Body.Close()

		// Check response status
		if resp.StatusCode != http.StatusOK {
			return nil, fmt.Errorf("API returned non-200 status: %d", resp.StatusCode)
		}

		// Read response body
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return nil, fmt.Errorf("failed to read response body: %w", err)
		}

		// Parse JSON response
		var prices []models.GoldPrice
		if err := json.Unmarshal(body, &prices); err != nil {
			return nil, fmt.Errorf("failed to parse response JSON: %w", err)
		}

		// Add timestamp and validate data
		for i := range prices {
			if prices[i].UpdatedAt.IsZero() {
				prices[i].UpdatedAt = time.Now()
			}
		}

		return prices, nil
	*/
}

// MockFetch is a mock implementation for testing or when API is unavailable
func (f *GoldPriceFetcher) MockFetch() []models.GoldPrice {
	now := time.Now()
	return []models.GoldPrice{
		{
			ID:        "1",
			Type:      "gold_1",
			Name:      "VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  11750000,
			SellPrice: 12050000,
			Company:   "Vàng Rồng Thăng Long",
			UpdatedAt: now,
		},
		{
			ID:        "2",
			Type:      "gold_2",
			Name:      "QUÀ MỪNG BẢN VỊ VÀNG (Quà Mừng Bản Vị Vàng)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  11750000,
			SellPrice: 12050000,
			Company:   "DOJI",
			UpdatedAt: now,
		},
		{
			ID:        "3",
			Type:      "gold_3",
			Name:      "TRANG SỨC BẰNG VÀNG RỒNG THĂNG LONG 99.9 (Vàng BTMC)",
			Karat:     "24k",
			Purity:    "99.9",
			BuyPrice:  11640000,
			SellPrice: 12000000,
			Company:   "BTMC",
			UpdatedAt: now,
		},
		{
			ID:        "4",
			Type:      "gold_4",
			Name:      "NHẪN TRÒN TRƠN (Vàng Rồng Thăng Long)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  11750000,
			SellPrice: 12050000,
			Company:   "Vàng Rồng Thăng Long",
			UpdatedAt: now,
		},
		{
			ID:        "5",
			Type:      "gold_5",
			Name:      "VÀNG NGUYÊN LIỆU (Vàng thị trường)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  11190000,
			SellPrice: 0,
			Company:   "Thị trường",
			UpdatedAt: now,
		},
		{
			ID:        "6",
			Type:      "gold_6",
			Name:      "TRANG SỨC BẰNG VÀNG RỒNG THĂNG LONG 999.9 (Vàng BTMC)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  11650000,
			SellPrice: 12010000,
			Company:   "BTMC",
			UpdatedAt: now,
		},
		{
			ID:        "7",
			Type:      "gold_7",
			Name:      "VÀNG MIẾNG SJC (Vàng SJC)",
			Karat:     "24k",
			Purity:    "999.9",
			BuyPrice:  12020000,
			SellPrice: 12220000,
			Company:   "SJC",
			UpdatedAt: now,
		},
	}
}
