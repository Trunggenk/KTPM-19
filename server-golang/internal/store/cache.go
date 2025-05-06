package store

import (
	"context"
	"sync"

	"github.com/Trunggenk/goldpriceserver/internal/models"
)

// Cache provides an in-memory cache with Redis backup
type Cache struct {
	store          *RedisStore
	goldPricesMu   sync.RWMutex
	goldPricesData []models.GoldPrice
}

// NewCache creates a new cache instance
func NewCache(store *RedisStore) *Cache {
	return &Cache{
		store:          store,
		goldPricesData: make([]models.GoldPrice, 0),
	}
}

// GetGoldPrices gets gold prices from cache, falling back to Redis if needed
func (c *Cache) GetGoldPrices(ctx context.Context) ([]models.GoldPrice, error) {
	// First try to get from memory cache
	c.goldPricesMu.RLock()
	if len(c.goldPricesData) > 0 {
		data := make([]models.GoldPrice, len(c.goldPricesData))
		copy(data, c.goldPricesData)
		c.goldPricesMu.RUnlock()
		return data, nil
	}
	c.goldPricesMu.RUnlock()

	// If not in memory, try to get from Redis
	prices, err := c.store.GetGoldPrices(ctx)
	if err != nil {
		return nil, err
	}

	// Update in-memory cache if we got data from Redis
	if len(prices) > 0 {
		c.SetGoldPrices(ctx, prices)
	}

	return prices, nil
}

// SetGoldPrices sets gold prices in the cache
func (c *Cache) SetGoldPrices(ctx context.Context, prices []models.GoldPrice) error {
	// Update in-memory cache
	c.goldPricesMu.Lock()
	c.goldPricesData = make([]models.GoldPrice, len(prices))
	copy(c.goldPricesData, prices)
	c.goldPricesMu.Unlock()

	return nil
}
