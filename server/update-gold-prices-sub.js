const Redis = require('redis');
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const redisClient = Redis.createClient();
redisClient.connect();

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = 3011;

// Lắng nghe kết nối từ client
io.on('connection', (socket) => {
    console.log('Client connected');
    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

// Subscribe to Redis channel
(async () => {
    await redisClient.subscribe('gold-prices', (message) => {
        const prices = JSON.parse(message);
        console.log('Received prices:', prices);

        // Emit prices to all connected clients
        io.emit('gold-prices-updated', prices);
    });
})();

server.listen(PORT, () => {
    console.log(`Subscriber 1 running on port ${PORT}`);
});