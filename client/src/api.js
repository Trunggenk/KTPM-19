// API service for interacting with the gold price server

const API_URL = 'http://localhost:3010/api';

/**
 * Fetch all gold prices from the server
 * @returns {Promise<Object>} Object containing gold prices for different types
 */
async function fetchGoldPrices() {
    try {
        const response = await fetch(`${API_URL}/gold-prices`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch gold prices: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching gold prices:', error);
        throw error;
    }
}

/**
 * Update gold prices on the server
 * @param {Object} prices - Object containing gold prices to update
 * @returns {Promise<string>} Success message
 */
async function updateGoldPrices(prices) {
    try {
        const response = await fetch(`${API_URL}/update-gold`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prices }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update gold prices: ${response.statusText}`);
        }
        
        return await response.text();
    } catch (error) {
        console.error('Error updating gold prices:', error);
        throw error;
    }
}

/**
 * Get a specific value by key
 * @param {string} key - The key to fetch
 * @returns {Promise<string>} Value associated with the key
 */
async function getValueByKey(key) {
    try {
        const response = await fetch(`${API_URL}/get/${key}`);
        
        if (!response.ok) {
            throw new Error(`Failed to get value: ${response.statusText}`);
        }
        
        return await response.text();
    } catch (error) {
        console.error(`Error fetching key ${key}:`, error);
        throw error;
    }
}

/**
 * Add or update a key-value pair
 * @param {string} key - The key to add or update
 * @param {string} value - The value to store
 * @returns {Promise<string>} Success message
 */
async function addOrUpdateValue(key, value) {
    try {
        const response = await fetch(`${API_URL}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ key, value }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to add/update value: ${response.statusText}`);
        }
        
        return await response.text();
    } catch (error) {
        console.error('Error adding/updating value:', error);
        throw error;
    }
}

// Export the API functions
export {
    fetchGoldPrices,
    updateGoldPrices,
    getValueByKey,
    addOrUpdateValue
}; 