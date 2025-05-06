package service

import (
	"context"
	"log"
	"sync"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/database"
	"github.com/Trunggenk/goldpriceserver/internal/models"
	"github.com/Trunggenk/goldpriceserver/internal/store"
	"github.com/Trunggenk/goldpriceserver/pkg/fetcher"
)

// GoldPriceService handles business logic for gold prices
type GoldPriceService struct {
	cache         *store.Cache
	redisStore    *store.RedisStore
	lastUpdate    time.Time
	lastPrices    []models.GoldPrice
	updateMutex   sync.RWMutex
	pricesFetcher *fetcher.GoldPriceFetcher
}

// NewGoldPriceService creates a new gold price service
func NewGoldPriceService(ctx context.Context, cache *store.Cache, redisStore *store.RedisStore) *GoldPriceService {
	return &GoldPriceService{
		cache:         cache,
		redisStore:    redisStore,
		lastUpdate:    time.Time{},
		pricesFetcher: fetcher.NewGoldPriceFetcher(),
	}
}

// FetchPrices fetches gold prices from the external API
func (s *GoldPriceService) FetchPrices(ctx context.Context) ([]models.GoldPrice, error) {
	// Use a context with timeout for the fetch operation
	fetchCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	return s.pricesFetcher.Fetch(fetchCtx)
}

// UpdatePrices updates gold prices and publishes them if changed
func (s *GoldPriceService) UpdatePrices(ctx context.Context) (bool, error) {
	s.updateMutex.Lock()
	defer s.updateMutex.Unlock()

	prices, err := s.FetchPrices(ctx)
	if err != nil {
		return false, err
	}

	if len(prices) == 0 {
		return false, nil
	}

	// Check if prices have changed
	if s.havePricesChanged(prices) {
		// Update cache
		if err := s.cache.SetGoldPrices(ctx, prices); err != nil {
			return false, err
		}

		// Publish to Redis for subscribers
		if err := s.redisStore.PublishGoldPrices(ctx, prices); err != nil {
			return false, err
		}

		// Database update will happen via Redis subscriber

		// Update internal state
		s.lastPrices = prices
		s.lastUpdate = time.Now()
		return true, nil
	}

	return false, nil
}

// StartAutoUpdate starts the automatic update process
func (s *GoldPriceService) StartAutoUpdate(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Auto update stopped")
			return
		case <-ticker.C:
			updated, err := s.UpdatePrices(ctx)
			if err != nil {
				log.Printf("Failed to update prices: %v", err)
				continue
			}

			if updated {
				log.Printf("Gold prices updated at %s", s.lastUpdate.Format("15:04:05"))
			} else {
				timeSince := time.Since(s.lastUpdate).Seconds()
				log.Printf("No changes in gold prices for %.0f seconds", timeSince)
			}
		}
	}
}

// FetchInitialData fetches initial data (for manual mode)
func (s *GoldPriceService) FetchInitialData(ctx context.Context) error {
	// Trước tiên, kiểm tra trong database
	dbPrices, err := database.FindAllGoldPrices()
	if err == nil && len(dbPrices) > 0 {
		log.Println("Loading initial data from database...")

		// Cập nhật cache với dữ liệu từ database
		if err := s.cache.SetGoldPrices(ctx, dbPrices); err != nil {
			return err
		}

		s.lastPrices = dbPrices
		s.lastUpdate = time.Now()
		log.Printf("Initial data loaded from database (%d items)", len(dbPrices))
		return nil
	}

	// Nếu database trống hoặc lỗi, thử lấy từ API
	prices, err := s.FetchPrices(ctx)
	if err != nil {
		return err
	}

	if len(prices) > 0 {
		if err := s.cache.SetGoldPrices(ctx, prices); err != nil {
			return err
		}
		if err := s.redisStore.PublishGoldPrices(ctx, prices); err != nil {
			return err
		}
		s.lastPrices = prices
		s.lastUpdate = time.Now()
		log.Println("Initial data loaded from API. Future updates must be done manually.")
	}
	return nil
}

// GetLatestPrices gets the latest gold prices from cache or database
func (s *GoldPriceService) GetLatestPrices(ctx context.Context) ([]models.GoldPrice, error) {
	return s.redisStore.GetGoldPrices(ctx)
}

// GetPriceById gets a specific gold price by ID
func (s *GoldPriceService) GetPriceById(ctx context.Context, id string) (*models.GoldPrice, error) {
	// Lấy từ cache trước
	prices, err := s.cache.GetGoldPrices(ctx)
	if err == nil && len(prices) > 0 {
		// Tìm trong cache
		for _, price := range prices {
			if price.ID == id || price.Type == id {
				priceCopy := price // Tạo bản sao để tránh vấn đề với con trỏ
				return &priceCopy, nil
			}
		}
	}

	// Không tìm thấy trong cache, thử tìm trong database
	dbPrice, err := database.FindGoldPriceByID(id)
	if err == nil && dbPrice != nil {
		return dbPrice, nil
	}

	return nil, nil // Không tìm thấy
}

// AddPricesManually adds gold prices manually (for manual mode)
func (s *GoldPriceService) AddPricesManually(ctx context.Context, prices []models.GoldPrice) error {
	s.updateMutex.Lock()
	defer s.updateMutex.Unlock()

	// Đảm bảo mỗi giá vàng có UpdatedAt
	for i := range prices {
		if prices[i].UpdatedAt.IsZero() {
			prices[i].UpdatedAt = time.Now()
		}
	}

	if err := s.cache.SetGoldPrices(ctx, prices); err != nil {
		return err
	}

	if err := s.redisStore.PublishGoldPrices(ctx, prices); err != nil {
		return err
	}

	s.lastPrices = prices
	s.lastUpdate = time.Now()
	return nil
}

// havePricesChanged checks if prices have changed since last update
func (s *GoldPriceService) havePricesChanged(newPrices []models.GoldPrice) bool {
	if len(s.lastPrices) != len(newPrices) {
		return true
	}

	// Simple check - in a real app, you'd want a more sophisticated comparison
	for i, newPrice := range newPrices {
		if i >= len(s.lastPrices) || newPrice != s.lastPrices[i] {
			return true
		}
	}
	return false
}
