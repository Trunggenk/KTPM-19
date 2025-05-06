package store

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/database"
	"github.com/Trunggenk/goldpriceserver/internal/models"
	"github.com/go-redis/redis/v8"
)

const (
	goldPricesCacheKey = "goldprices:latest"
	goldPricesChannel  = "goldprices:updates"
	dbChannel          = "gold-prices-db" // Channel dành riêng cho DB updates
)

// RedisConfig contains Redis configuration
type RedisConfig struct {
	Address  string
	Password string
	DB       int
}

// RedisStore handles Redis operations
type RedisStore struct {
	client *redis.Client
}

// NewRedisStore creates a new Redis store
func NewRedisStore(ctx context.Context, config RedisConfig) (*RedisStore, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     config.Address,
		Password: config.Password,
		DB:       config.DB,
	})

	// Check connection
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, err
	}

	store := &RedisStore{
		client: client,
	}

	// Subscribe to DB channel for database updates
	go store.subscribeToDBChannel(ctx)

	return store, nil
}

// PublishGoldPrices publishes gold prices to Redis
func (s *RedisStore) PublishGoldPrices(ctx context.Context, prices []models.GoldPrice) error {
	// Kiểm tra giá trị nil để tránh panic
	if prices == nil {
		return errors.New("prices cannot be nil")
	}

	data, err := json.Marshal(prices)
	if err != nil {
		return err
	}

	// Publish to channel for real-time updates
	if err := s.client.Publish(ctx, goldPricesChannel, data).Err(); err != nil {
		return err
	}

	// Publish to DB channel for database updates
	if err := s.client.Publish(ctx, dbChannel, data).Err(); err != nil {
		return err
	}

	// Set in cache with expiration
	return s.client.Set(ctx, goldPricesCacheKey, data, 24*time.Hour).Err()
}

// subscribeToDBChannel subscribes to database update channel
func (s *RedisStore) subscribeToDBChannel(ctx context.Context) {
	pubsub := s.client.Subscribe(ctx, dbChannel)
	defer pubsub.Close()

	// Process messages in a separate goroutine
	ch := pubsub.Channel()

	for {
		select {
		case msg, ok := <-ch:
			if !ok {
				return
			}

			var prices []models.GoldPrice
			if err := json.Unmarshal([]byte(msg.Payload), &prices); err != nil {
				log.Printf("Error unmarshaling DB message: %v", err)
				continue
			}

			// Update database
			if err := database.UpsertGoldPrices(prices); err != nil {
				log.Printf("Error updating database: %v", err)
			} else {
				log.Printf("Successfully updated database with %d prices", len(prices))
			}

		case <-ctx.Done():
			return
		}
	}
}

// SubscribeToGoldPrices subscribes to gold price updates
func (s *RedisStore) SubscribeToGoldPrices(ctx context.Context) (<-chan []models.GoldPrice, error) {
	pubsub := s.client.Subscribe(ctx, goldPricesChannel)

	// Verify subscription
	_, err := pubsub.Receive(ctx)
	if err != nil {
		return nil, err
	}

	// Create output channel for processed messages
	out := make(chan []models.GoldPrice, 100)

	// Process messages in a separate goroutine
	go func() {
		defer pubsub.Close()
		defer close(out)

		ch := pubsub.Channel()

		for {
			select {
			case msg, ok := <-ch:
				if !ok {
					return
				}

				var prices []models.GoldPrice
				if err := json.Unmarshal([]byte(msg.Payload), &prices); err != nil {
					continue
				}

				// Send to output channel, but don't block if buffer is full
				select {
				case out <- prices:
				default:
					// Drop message if channel buffer is full
				}

			case <-ctx.Done():
				return
			}
		}
	}()

	return out, nil
}

// GetGoldPrices gets gold prices from Redis cache, falling back to database
func (s *RedisStore) GetGoldPrices(ctx context.Context) ([]models.GoldPrice, error) {
	// Try to get from Redis cache first
	data, err := s.client.Get(ctx, goldPricesCacheKey).Bytes()
	if err == nil {
		// Cache hit
		var prices []models.GoldPrice
		if err := json.Unmarshal(data, &prices); err != nil {
			return nil, err
		}
		return prices, nil
	}

	// If Redis error is not "key not found", return the error
	if err != redis.Nil {
		return nil, err
	}

	// Cache miss, get from database
	prices, err := database.FindAllGoldPrices()
	if err != nil {
		return nil, err
	}

	// If we found prices in the database, update the cache
	if len(prices) > 0 {
		data, err := json.Marshal(prices)
		if err == nil {
			// Set in cache with expiration (ignore errors)
			_ = s.client.Set(ctx, goldPricesCacheKey, data, 24*time.Hour).Err()
		}
	}

	return prices, nil
}

// Close closes the Redis connection
func (s *RedisStore) Close() error {
	return s.client.Close()
}
