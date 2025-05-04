const express = require('express');
const router = express.Router();
const goldPriceController = require('../controllers/goldPriceController');

// Get all gold prices
router.get('/api/gold-prices', goldPriceController.getAllPrices);

// Get gold price by ID
router.get('/api/get/:id', goldPriceController.getPriceById);

// Add or update gold price(s)
router.post('/api/add', goldPriceController.addOrUpdatePrice);

module.exports = router; 