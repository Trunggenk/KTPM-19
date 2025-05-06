package database

import (
	"log"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/models"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var (
	DB *gorm.DB
)

// Config chứa cấu hình cho database
type Config struct {
	Path string
}

// Connect kết nối đến cơ sở dữ liệu SQLite
func Connect(config Config) (*gorm.DB, error) {
	// Cấu hình logger
	newLogger := logger.New(
		log.New(log.Writer(), "\r\n", log.LstdFlags),
		logger.Config{
			SlowThreshold:             time.Second,
			LogLevel:                  logger.Info,
			IgnoreRecordNotFoundError: true,
			Colorful:                  true,
		},
	)

	// Kết nối đến DB
	db, err := gorm.Open(sqlite.Open(config.Path), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		return nil, err
	}

	// Set biến toàn cục
	DB = db

	// Migrate schema
	err = DB.AutoMigrate(&models.GoldPrice{})
	if err != nil {
		return nil, err
	}

	log.Printf("Connected to database: %s", config.Path)
	return DB, nil
}

// GetDB returns the DB instance
func GetDB() *gorm.DB {
	return DB
}

// FindAllGoldPrices lấy tất cả giá vàng từ DB
func FindAllGoldPrices() ([]models.GoldPrice, error) {
	var prices []models.GoldPrice
	result := DB.Order("updated_at desc").Find(&prices)
	return prices, result.Error
}

// FindGoldPriceByID lấy giá vàng theo ID
func FindGoldPriceByID(id string) (*models.GoldPrice, error) {
	var price models.GoldPrice
	result := DB.Where("id = ? OR type = ?", id, id).First(&price)
	if result.Error != nil {
		return nil, result.Error
	}
	return &price, nil
}

// UpsertGoldPrices cập nhật hoặc thêm mới giá vàng
func UpsertGoldPrices(prices []models.GoldPrice) error {
	// Sử dụng transaction để đảm bảo tính toàn vẹn
	return DB.Transaction(func(tx *gorm.DB) error {
		for _, price := range prices {
			// Tìm theo type hoặc id
			var existingPrice models.GoldPrice
			result := tx.Where("type = ?", price.Type).First(&existingPrice)

			if result.Error == nil {
				// Nếu tìm thấy, cập nhật
				price.ID = existingPrice.ID // Giữ ID cũ
				tx.Model(&existingPrice).Updates(price)
			} else {
				// Nếu không tìm thấy, tạo mới
				tx.Create(&price)
			}
		}
		return nil
	})
}
 