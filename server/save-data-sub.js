const Redis = require('redis');
const { write } = require('./utils'); // Hàm `write` từ utils.js

const redisClient = Redis.createClient();
redisClient.connect();

// Subscribe to Redis channel
(async () => {
    await redisClient.subscribe('gold-prices', async (message) => {
        const prices = JSON.parse(message);
        console.log('Received prices for database:', prices);

        // Ghi từng loại giá vàng vào cơ sở dữ liệu
        for (const [type, price] of Object.entries(prices)) {
            await write(`gold_${type}`, price);
        }
        console.log('Prices saved to database');
    });
})();