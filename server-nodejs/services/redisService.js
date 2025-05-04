const Redis = require('redis');
const { GoldPrice } = require('../models');
const { sequelize } = require('../models');

// Create Redis publisher and subscriber clients
let redisPublisher;
let redisDBSubscriber;

// Create Redis cache client
const redisCache = Redis.createClient({
  url: 'redis://localhost:6380'
});

const initRedisPublisher = async () => {
  try {
    redisPublisher = Redis.createClient({
      url: 'redis://localhost:6380'
    });
    
    await redisPublisher.connect();
    console.log('Redis publisher connected');
    
    return redisPublisher;
  } catch (error) {
    console.error('Failed to connect Redis publisher:', error);
    throw error;
  }
};

const initRedisDBSubscriber = async () => {
  try {
    redisDBSubscriber = Redis.createClient({
      url: 'redis://localhost:6380'
    });
    
    await redisDBSubscriber.connect();
    console.log('Redis DB subscriber connected');
    
    // Subscribe to the gold-prices-db channel
    await redisDBSubscriber.subscribe('gold-prices-db', async (message) => {
      try {
        const goldPrices = JSON.parse(message);
        console.log('Received update for database:', goldPrices.length, 'items');
        
        // Lấy dữ liệu hiện tại từ database để so sánh
        const existingPrices = await GoldPrice.findAll();
        const hasChanges = areGoldPricesChanged(goldPrices, existingPrices);
        
        if (hasChanges) {
          // Chỉ cập nhật database khi có thay đổi
          console.log('Changes detected, updating database...');
          
          // Save each gold price to the database
          for (const goldPrice of goldPrices) {
            await GoldPrice.upsert(goldPrice, { 
              where: { type: goldPrice.type }
            });
          }
          
          // Cache-Aside pattern: Invalidate cache instead of updating
          await invalidateCache();
          
          console.log('Database updated with new gold prices and cache invalidated');
        } else {
          console.log('No changes detected, skipping database update');
        }
      } catch (error) {
        console.error('Error updating database from Redis message:', error);
      }
    });
    
    return redisDBSubscriber;
  } catch (error) {
    console.error('Failed to connect Redis DB subscriber:', error);
    throw error;
  }
};

const publishGoldPrices = async (goldPrices) => {
  if (!redisPublisher) {
    throw new Error('Redis publisher not initialized');
  }
  
  try {
    // Kiểm tra xem dữ liệu có thay đổi không
    const existingPrices = await GoldPrice.findAll();
    const hasChanges = areGoldPricesChanged(goldPrices, existingPrices);
    
    if (hasChanges) {
      // Chỉ publish khi có thay đổi
      console.log('Publishing updated gold prices to Redis channels');
      
      // Publish to both channels
      await redisPublisher.publish('gold-prices', JSON.stringify(goldPrices));
      await redisPublisher.publish('gold-prices-db', JSON.stringify(goldPrices));
      
      // Cache-Aside pattern: Don't update cache here, 
      // it will be invalidated by the subscriber
      
      return true; // Có cập nhật
    } else {
      console.log('No changes in gold prices, skipping publish');
      return false; // Không có cập nhật
    }
  } catch (error) {
    console.error('Failed to publish gold prices:', error);
    throw error;
  }
};

// Initialize cache
const initCache = async () => {
  try {
    // Connect to Redis cache if not connected
    if (!redisCache.isOpen) {
      await redisCache.connect();
      console.log('Redis cache client connected');
    }
    
    // Load initial data from database into cache
    const goldPrices = await GoldPrice.findAll();
    if (goldPrices && goldPrices.length > 0) {
      await redisCache.set('gold-prices', JSON.stringify(goldPrices));
      console.log('Cache initialized with', goldPrices.length, 'gold price records');
    }
  } catch (error) {
    console.error('Failed to initialize cache:', error);
    throw error;
  }
};

// Get cached prices (with Cache-Aside pattern)
const getCachedPrices = async () => {
  try {
    // Try to get from cache
    const cachedData = await redisCache.get('gold-prices');
    if (cachedData) {
      return JSON.parse(cachedData);
    }
    
    // If not in cache, get from DB
    const goldPrices = await GoldPrice.findAll();
    
    // Update cache
    await redisCache.set('gold-prices', JSON.stringify(goldPrices));
    
    return goldPrices;
  } catch (error) {
    console.error('Error getting cached prices:', error);
    // Fall back to DB if cache fails
    return await GoldPrice.findAll();
  }
};

// Get cached price by ID
const getCachedPriceById = async (id) => {
  try {
    // Try to get all from cache first (smaller DB, so this is efficient enough)
    const cachedData = await redisCache.get('gold-prices');
    if (cachedData) {
      const prices = JSON.parse(cachedData);
      return prices.find(price => price.id == id || price.type === id);
    }
    
    // If not in cache, get from DB
    const price = await GoldPrice.findOne({
      where: sequelize.or(
        { id: id },
        { type: id }
      )
    });
    
    return price;
  } catch (error) {
    console.error('Error getting cached price by ID:', error);
    // Fall back to DB if cache fails
    return await GoldPrice.findOne({
      where: sequelize.or(
        { id: id },
        { type: id }
      )
    });
  }
};

// Invalidate cache
const invalidateCache = async () => {
  try {
    await redisCache.del('gold-prices');
    console.log('Gold prices cache invalidated');
  } catch (error) {
    console.error('Error invalidating cache:', error);
  }
};

// Helper to check if gold prices have changed
const areGoldPricesChanged = (newPrices, oldPrices) => {
  if (!newPrices || !oldPrices) return true;
  if (newPrices.length !== oldPrices.length) return true;
  
  // Convert old prices to a map for easier lookup
  const oldPricesMap = new Map();
  oldPrices.forEach(price => {
    oldPricesMap.set(price.type, price);
  });
  
  // Check if any price has changed
  for (const newPrice of newPrices) {
    const oldPrice = oldPricesMap.get(newPrice.type);
    if (!oldPrice) return true;
    
    if (
      newPrice.buy_price !== oldPrice.buy_price ||
      newPrice.sell_price !== oldPrice.sell_price ||
      newPrice.updated_at !== oldPrice.updated_at
    ) {
      return true;
    }
  }
  
  return false;
};

module.exports = {
  initRedisPublisher,
  initRedisDBSubscriber,
  publishGoldPrices,
  initCache,
  getCachedPrices,
  getCachedPriceById,
  invalidateCache,
  areGoldPricesChanged
}; 