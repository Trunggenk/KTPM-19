const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const lib = require('./utils');

const app = express();
const port = 3010;

// Middleware
app.use(bodyParser.json());
app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Add new record or update existing record
app.post('/api/add', async (req, res) => {
    try {
        const { key, value } = req.body;
        await lib.write(key, value);
        res.send("Insert a new record successfully!");
    } catch (err) {
        res.status(500).send(err.toString());
    }
});

// Get value by key ID
app.get('/api/get/:id', async (req, res) => {
    try {
        const id = req.params.id;
        const value = await lib.view(id);
        res.status(200).send(value);
    } catch (err) {
        res.status(500).send(err.toString());
    }
});

// Endpoint to update gold prices
app.post('/api/update-gold', async (req, res) => {
    try {
        const { prices } = req.body;
        
        // Store each type of gold with its price
        for (const [type, price] of Object.entries(prices)) {
            await lib.write(`gold_${type}`, price);
        }
        
        res.send("Updated gold prices successfully!");
    } catch (err) {
        res.status(500).send(err.toString());
    }
});

// Get all gold prices
app.get('/api/gold-prices', async (req, res) => {
    try {
        const types = ['sjc', 'sjc_nhan', '24k', '18k', '14k', '9k'];
        const prices = {};
        
        for (const type of types) {
            prices[type] = await lib.view(`gold_${type}`) || "0";
        }
        
        res.json(prices);
    } catch (err) {
        res.status(500).send(err.toString());
    }
});

// Admin interface for managing gold prices
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
}); 