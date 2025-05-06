// Frontend application code for Gold Price Tracker

// API URL for frontend requests
const API_URL = '/api';

// Store previous prices to calculate changes
let previousPrices = {};

// Gold type definitions and labels
const goldTypes = {
    'sjc': 'Vàng SJC',
    'sjc_nhan': 'Nhẫn SJC',
    '24k': 'Vàng 24K',
    '18k': 'Vàng 18K',
    '14k': 'Vàng 14K',
    '9k': 'Vàng 9K'
};

// Format price with commas as thousand separators
function formatPrice(price) {
    return parseInt(price).toLocaleString('vi-VN') + ' VND';
}

// Create a card for each gold type
function createPriceCards() {
    const container = document.getElementById('gold-prices-container');
    container.innerHTML = '';
    
    for (const [key, label] of Object.entries(goldTypes)) {
        const card = document.createElement('div');
        card.className = 'price-card';
        card.id = `card-${key}`;
        
        card.innerHTML = `
            <h2>${label}</h2>
            <div class="price-value" id="price-${key}">Đang tải...</div>
            <div class="price-change" id="change-${key}"></div>
        `;
        
        container.appendChild(card);
    }
}

// Update the prices with the latest data
function updatePrices(prices) {
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleString('vi-VN');
    
    for (const [key, price] of Object.entries(prices)) {
        const priceElement = document.getElementById(`price-${key}`);
        if (!priceElement) continue;
        
        const formattedPrice = formatPrice(price);
        priceElement.textContent = formattedPrice;
        
        // Add highlight animation on price change
        const card = document.getElementById(`card-${key}`);
        card.classList.remove('highlight');
        void card.offsetWidth; // Trigger reflow to restart animation
        card.classList.add('highlight');
        
        // Calculate and display price change
        const changeElement = document.getElementById(`change-${key}`);
        if (previousPrices[key]) {
            const diff = parseInt(price) - parseInt(previousPrices[key]);
            if (diff !== 0) {
                const sign = diff > 0 ? '+' : '';
                const changeClass = diff > 0 ? 'up' : 'down';
                changeElement.textContent = `${sign}${diff.toLocaleString('vi-VN')} VND`;
                changeElement.className = `price-change ${changeClass}`;
            }
        }
    }
    
    // Store current prices for next comparison
    previousPrices = {...prices};
}

// Fetch the latest gold prices
async function fetchGoldPrices() {
    try {
        const response = await fetch(`${API_URL}/gold-prices`);
        if (response.ok) {
            const data = await response.json();
            updatePrices(data);
        } else {
            console.error('Failed to fetch gold prices');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Initialize the page
function init() {
    createPriceCards();
    fetchGoldPrices();
    
    // Fetch new prices every 2 seconds
    setInterval(fetchGoldPrices, 2000);
}

// Start the application
window.onload = init; 