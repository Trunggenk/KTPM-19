const { Server } = require('socket.io');
const Redis = require('redis');
const { getCachedPrices, areGoldPricesChanged } = require('./redisService');

// Create Redis subscriber client for socket
const redisSocketSubscriber = Redis.createClient({
  url: 'redis://localhost:6380'
});

// Create Redis cache client
const redisCache = Redis.createClient({
  url: 'redis://localhost:6380'
});

// Initialize Socket.IO
let io;
// In-memory cache for latest gold prices
let goldPricesCache = [];

const initSocketIO = async (server) => {
  try {
    // Set up Socket.IO with CORS
    io = new Server(server, {
      cors: {
        origin: '*',
        methods: ['GET', 'POST']
      }
    });

    // Connect to Redis
    await redisSocketSubscriber.connect();
    console.log('Redis socket subscriber connected');
    
    // Connect to Redis cache
    await redisCache.connect();
    console.log('Redis cache connected');
    
    // Load initial gold prices into memory using Cache-Aside pattern
    try {
      goldPricesCache = await getCachedPrices();
      console.log('Loaded gold prices into socket memory cache:', goldPricesCache.length, 'items');
    } catch (error) {
      console.error('Error loading initial gold prices:', error);
    }

    // Handle new socket connections
    io.on('connection', async (socket) => {
      console.log('New client connected:', socket.id);
      
      // Send cached gold prices to new client immediately
      if (goldPricesCache.length > 0) {
        socket.emit('gold-prices-updated', goldPricesCache);
        console.log('Sent cached gold prices to new client:', socket.id);
      } else {
        // If in-memory cache is empty, try to fetch from Redis/DB using Cache-Aside
        try {
          const prices = await getCachedPrices();
          if (prices && prices.length > 0) {
            goldPricesCache = prices;
            socket.emit('gold-prices-updated', prices);
            console.log('Sent newly fetched gold prices to client:', socket.id);
          }
        } catch (error) {
          console.error('Failed to fetch prices for new client:', error);
        }
      }

      socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
      });
    });

    // Subscribe to the gold-prices channel (only for socket broadcasting)
    await redisSocketSubscriber.subscribe('gold-prices', async (message) => {
      try {
        const prices = JSON.parse(message);
        
        // Kiểm tra xem dữ liệu có thay đổi không
        const hasChanges = areGoldPricesChanged(prices, goldPricesCache);
        
        if (hasChanges) {
          console.log('Changes detected, updating in-memory cache and broadcasting...');
          
          // Update in-memory cache
          goldPricesCache = prices;
          
          // Broadcast to all clients
          io.emit('gold-prices-updated', prices);
          console.log('Broadcasted updated gold prices to clients');
        } else {
          console.log('No changes in prices, skipping broadcast to clients');
        }
      } catch (error) {
        console.error('Error broadcasting gold prices:', error);
      }
    });

    console.log('Socket.IO server initialized');
    return io;
  } catch (error) {
    console.error('Failed to initialize Socket.IO server:', error);
    throw error;
  }
};

const getIO = () => {
  if (!io) {
    throw new Error('Socket.IO has not been initialized');
  }
  return io;
};

module.exports = {
  initSocketIO,
  getIO
}; 