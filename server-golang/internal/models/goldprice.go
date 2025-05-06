package models

import "time"

// GoldPrice represents a gold price record
type GoldPrice struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	Type      string    `json:"type" gorm:"uniqueIndex;not null"`
	Name      string    `json:"name" gorm:"not null"`
	Karat     string    `json:"karat"`
	Purity    string    `json:"purity"`
	BuyPrice  float64   `json:"buy_price" gorm:"not null"`
	SellPrice float64   `json:"sell_price" gorm:"not null"`
	Company   string    `json:"company"`
	UpdatedAt time.Time `json:"updated_at" gorm:"index;not null"`
	CreatedAt time.Time `json:"created_at" gorm:"autoCreateTime;not null"`
}
