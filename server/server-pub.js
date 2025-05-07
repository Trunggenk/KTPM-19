const Redis = require('redis');
const fetch = require('node-fetch');

const redisClient = Redis.createClient();
redisClient.connect();

const API_URL = 'http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v'; // Thay bằng API thực tế

async function fetchGoldPrices() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        if (!data || !data.length) {
            console.error('No data received from API');
            return;
        }
        const prices = { pb_1: data[5].pb_1 };
        await redisClient.publish('gold-prices', JSON.stringify(prices));
        console.log('Published gold prices:', prices);
    } catch (error) {
        console.error('Error fetching gold prices:', error);
    }
}

// Fetch and publish prices every 5 seconds
setInterval(fetchGoldPrices, 5000);