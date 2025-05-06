// Frontend application logic for Gold Price Tracker
const api = require('./api');

/**
 * Initialize gold price data
 * @returns {Promise<void>}
 */
async function initGoldPrices() {
    try {
        const prices = await api.fetchGoldPrices();
        return prices;
    } catch (error) {
        console.error('Error initializing gold prices:', error);
        throw error;
    }
}

/**
 * Update gold prices
 * @param {Object} prices - The prices to update
 * @returns {Promise<string>} - Success message
 */
async function updateGoldPrices(prices) {
    try {
        const result = await api.updateGoldPrices(prices);
        return result;
    } catch (error) {
        console.error('Error updating gold prices:', error);
        throw error;
    }
}

/**
 * Get value for specific key
 * @param {string} key - The key to fetch
 * @returns {Promise<string>} - The value
 */
async function getValue(key) {
    try {
        const value = await api.getValueByKey(key);
        return value;
    } catch (error) {
        console.error(`Error getting value for key ${key}:`, error);
        throw error;
    }
}

/**
 * Set value for specific key
 * @param {string} key - The key to update
 * @param {string} value - The value to set
 * @returns {Promise<string>} - Success message
 */
async function setValue(key, value) {
    try {
        const result = await api.addOrUpdateValue(key, value);
        return result;
    } catch (error) {
        console.error(`Error setting value for key ${key}:`, error);
        throw error;
    }
}

// Export the application functions
module.exports = {
    initGoldPrices,
    updateGoldPrices,
    getValue,
    setValue
}; 