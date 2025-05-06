const express = require('express');
const path = require('path');
const app = require('./app');

const server = express();
const port = 3005;

// Serve static files from the public directory
server.use(express.static(path.join(__dirname, '../public')));

// API routes
server.get('/api/gold-prices', async (req, res) => {
    try {
        const prices = await app.initGoldPrices();
        res.json(prices);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

server.post('/api/update-gold', express.json(), async (req, res) => {
    try {
        const { prices } = req.body;
        const result = await app.updateGoldPrices(prices);
        res.send(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

server.get('/api/get/:key', async (req, res) => {
    try {
        const key = req.params.key;
        const value = await app.getValue(key);
        res.send(value);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

server.post('/api/add', express.json(), async (req, res) => {
    try {
        const { key, value } = req.body;
        const result = await app.setValue(key, value);
        res.send(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve the main page
server.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Start the server
server.listen(port, () => {
    console.log(`Client application running on port ${port}`);
    console.log(`Open http://localhost:${port} in your browser to view gold prices`);
}); 