package utils

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/Trunggenk/goldpriceserver/internal/models"
)

// GetUniqueHash generates a deterministic unique hash for a gold price
func GetUniqueHash(price models.GoldPrice) string {
	// Create a unique string combining type and company
	uniqueStr := fmt.Sprintf("%s-%s-%f-%f-%s",
		price.Type,
		price.Company,
		price.BuyPrice,
		price.SellPrice,
		price.UpdatedAt.Format(time.RFC3339),
	)

	// Generate SHA-256 hash
	hash := sha256.Sum256([]byte(uniqueStr))
	return hex.EncodeToString(hash[:])
}

// FormatGoldPriceJSON formats a gold price as a readable JSON string
func FormatGoldPriceJSON(price models.GoldPrice) (string, error) {
	data, err := json.MarshalIndent(price, "", "  ")
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// FormatTimeDiff formats a time duration in a human-readable way
func FormatTimeDiff(since time.Time) string {
	duration := time.Since(since)

	seconds := int(duration.Seconds())
	if seconds < 60 {
		return fmt.Sprintf("%d seconds ago", seconds)
	}

	minutes := seconds / 60
	if minutes < 60 {
		return fmt.Sprintf("%d minutes ago", minutes)
	}

	hours := minutes / 60
	if hours < 24 {
		return fmt.Sprintf("%d hours ago", hours)
	}

	days := hours / 24
	return fmt.Sprintf("%d days ago", days)
}

// SanitizeInput sanitizes user input
func SanitizeInput(input string) string {
	// Basic sanitation example - in a real app, use a more robust approach
	sanitized := strings.TrimSpace(input)
	sanitized = strings.ReplaceAll(sanitized, "<", "&lt;")
	sanitized = strings.ReplaceAll(sanitized, ">", "&gt;")
	return sanitized
}
