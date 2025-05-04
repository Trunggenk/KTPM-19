const { GoldPrice, sequelize } = require('../models');
const fetch = require('node-fetch');
const { getCachedPrices, publishGoldPrices, getCachedPriceById } = require('../services/redisService');

const API_URL = 'http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v';

// Sample JSON data for testing and fallback
const SAMPLE_JSON_DATA = {
  "DataList": {
    "Data": [
      {
        "@row": "1",
        "@n_1": "VÀNG MIẾNG VRTL (Vàng Rồng Thăng Long)",
        "@k_1": "24k",
        "@h_1": "999.9",
        "@pb_1": "11750000",
        "@ps_1": "12050000",
        "@pt_1": "0",
        "@d_1": "07/05/2025 15:35"
      },
      {
        "@row": "2",
        "@n_2": "QUÀ MỪNG BẢN VỊ VÀNG (Quà Mừng Bản Vị Vàng)",
        "@k_2": "24k",
        "@h_2": "999.9",
        "@pb_2": "11750000",
        "@ps_2": "12050000",
        "@pt_2": "0",
        "@d_2": "07/05/2025 15:35"
      },
      {
        "@row": "3",
        "@n_3": "TRANG SỨC BẰNG VÀNG RỒNG THĂNG LONG 99.9 (Vàng BTMC)",
        "@k_3": "24k",
        "@h_3": "99.9",
        "@pb_3": "11640000",
        "@ps_3": "12000000",
        "@pt_3": "0",
        "@d_3": "07/05/2025 15:35"
      },
      {
        "@row": "4",
        "@n_4": "NHẪN TRÒN TRƠN (Vàng Rồng Thăng Long)",
        "@k_4": "24k",
        "@h_4": "999.9",
        "@pb_4": "11750000",
        "@ps_4": "12050000",
        "@pt_4": "0",
        "@d_4": "07/05/2025 15:35"
      },
      {
        "@row": "5",
        "@n_5": "VÀNG NGUYÊN LIỆU (Vàng thị trường)",
        "@k_5": "24k",
        "@h_5": "999.9",
        "@pb_5": "11190000",
        "@ps_5": "0",
        "@pt_5": "0",
        "@d_5": "07/05/2025 15:35"
      },
      {
        "@row": "6",
        "@n_6": "TRANG SỨC BẰNG VÀNG RỒNG THĂNG LONG 999.9 (Vàng BTMC)",
        "@k_6": "24k",
        "@h_6": "999.9",
        "@pb_6": "11650000",
        "@ps_6": "12010000",
        "@pt_6": "0",
        "@d_6": "07/05/2025 15:35"
      },
      {
        "@row": "7",
        "@n_7": "VÀNG MIẾNG SJC (Vàng SJC)",
        "@k_7": "24k",
        "@h_7": "999.9",
        "@pb_7": "12020000",
        "@ps_7": "12220000",
        "@pt_7": "0",
        "@d_7": "07/05/2025 15:35"
      }
    ]
  }
};

// Helper function to parse JSON data format
const parseJsonData = (jsonData) => {
  try {
    // Check if the expected structure exists
    if (!jsonData.DataList || !jsonData.DataList.Data || !Array.isArray(jsonData.DataList.Data)) {
      throw new Error('Invalid JSON data structure');
    }
    
    const goldPrices = [];
    
    // Get first 7 items or all if less than 7
    const first7Items = jsonData.DataList.Data.slice(0, 7);
    
    for (const item of first7Items) {
      // Extract row number
      const row = item['@row'];
      if (!row) continue;
      
      goldPrices.push({
        type: `gold_${row}`,
        name: item[`@n_${row}`] || '',
        karat: item[`@k_${row}`] || '',
        purity: item[`@h_${row}`] || '',
        buy_price: parseInt(item[`@pb_${row}`]) || 0,
        sell_price: parseInt(item[`@ps_${row}`]) || 0,
        updated_at: item[`@d_${row}`] || ''
      });
    }
    
    // Nếu không tìm thấy dữ liệu nào, throw error
    if (goldPrices.length === 0) {
      throw new Error('No gold price data found in JSON');
    }
    
    console.log(`Parsed ${goldPrices.length} gold price items from JSON successfully`);
    return goldPrices;
  } catch (error) {
    console.error('Error parsing JSON data:', error);
    throw error;
  }
};

// Parse the sample data to use as fallback
const FALLBACK_GOLD_PRICES = (() => {
  try {
    return parseJsonData(SAMPLE_JSON_DATA);
  } catch (error) {
    console.error('Error parsing sample data:', error);
    // Return some hardcoded data as absolute fallback
    return [
      {
        type: 'gold_7',
        name: 'VÀNG MIẾNG SJC (Vàng SJC)',
        karat: '24k',
        purity: '999.9',
        buy_price: 12020000,
        sell_price: 12220000,
        updated_at: '07/05/2025 15:35'
      }
    ];
  }
})();

// Controller methods
const goldPriceController = {
  // Fetch latest prices from the API (without DB update)
  async fetchPrices() {
    try {
      console.log('Fetching data from API...');
      
      let goldPrices;
      try {
        // Fetch from the real API
        const response = await fetch(API_URL);
        
        // Parse as JSON
        const jsonData = await response.json();
        goldPrices = parseJsonData(jsonData);
      } catch (error) {
        console.error('Error fetching from API, using sample data instead:', error.message);
        goldPrices = FALLBACK_GOLD_PRICES;
      }
      
      console.log('Gold prices fetched successfully:', goldPrices.length);
      return goldPrices;
    } catch (error) {
      console.error('Error fetching gold prices:', error.message);
      throw error;
    }
  },
  
  // Legacy method for backwards compatibility
  async fetchAndUpdatePrices() {
    try {
      const goldPrices = await this.fetchPrices();
      
      // Save each gold price to the database (now handled by Redis subscriber)
      for (const goldPrice of goldPrices) {
        await GoldPrice.upsert(goldPrice, { 
          where: { type: goldPrice.type }
        });
      }
      
      console.log('Gold prices updated successfully in DB');
      return goldPrices;
    } catch (error) {
      console.error('Error updating gold prices in DB:', error.message);
      throw error;
    }
  },
  
  // Get all gold prices
  async getAllPrices(req, res) {
    try {
      // Cache-Aside pattern: getCachedPrices already implements the pattern
      const prices = await getCachedPrices();
      res.json(prices);
    } catch (error) {
      console.error('Error fetching gold prices:', error);
      res.status(500).json({ error: 'Failed to fetch gold prices' });
    }
  },
  
  // Get gold price by ID
  async getPriceById(req, res) {
    try {
      const { id } = req.params;
      
      // Cache-Aside pattern: Use getCachedPriceById
      const price = await getCachedPriceById(id);
      
      if (!price) {
        return res.status(404).json({ error: 'Gold price not found' });
      }
      
      res.json(price);
    } catch (error) {
      console.error('Error fetching gold price:', error);
      res.status(500).json({ error: 'Failed to fetch gold price' });
    }
  },
  
  // Add or update gold price manually
  async addOrUpdatePrice(req, res) {
    try {
      const goldPriceData = req.body;
      
      // Validate required fields
      if (!goldPriceData.type || !goldPriceData.name || 
          goldPriceData.buy_price === undefined || 
          goldPriceData.sell_price === undefined) {
        return res.status(400).json({ 
          error: 'Missing required fields. Required: type, name, buy_price, sell_price' 
        });
      }
      
      // If single object, convert to array
      const newItems = Array.isArray(goldPriceData) ? goldPriceData : [goldPriceData];
      
      // Add updated_at if not provided
      const now = new Date().toLocaleString('vi-VN');
      newItems.forEach(price => {
        if (!price.updated_at) {
          price.updated_at = now;
        }
        
        // Ensure type follows the format 'gold_X' if not already
        if (!price.type.startsWith('gold_')) {
          price.type = `gold_${price.type}`;
        }
      });
      
      // Lấy tất cả dữ liệu hiện tại từ database
      const allCurrentPrices = await GoldPrice.findAll();
      
      // Tạo map để dễ dàng cập nhật
      const pricesMap = new Map();
      allCurrentPrices.forEach(price => {
        pricesMap.set(price.type, {
          id: price.id,
          type: price.type,
          name: price.name,
          karat: price.karat,
          purity: price.purity,
          buy_price: price.buy_price,
          sell_price: price.sell_price,
          updated_at: price.updated_at
        });
      });
      
      // Cập nhật các mục được chỉnh sửa
      newItems.forEach(newItem => {
        pricesMap.set(newItem.type, {
          ...pricesMap.get(newItem.type),
          ...newItem
        });
      });
      
      // Chuyển map thành mảng để publish
      const allUpdatedPrices = Array.from(pricesMap.values());
      
      // Cache-Aside: Publish để cập nhật DB và làm mất hiệu lực cache
      const updated = await publishGoldPrices(allUpdatedPrices);
      
      if (updated) {
        return res.status(200).json({ 
          success: true, 
          message: 'Gold price(s) updated successfully and cache invalidated',
          data: newItems
        });
      } else {
        return res.status(200).json({ 
          success: true, 
          message: 'No changes detected, data remains the same',
          data: newItems
        });
      }
    } catch (error) {
      console.error('Error adding/updating gold price:', error);
      res.status(500).json({ error: 'Failed to add/update gold price' });
    }
  }
};

module.exports = goldPriceController; 