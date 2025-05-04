const express = require('express');
const http = require('http');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');

// Parse command line arguments
const args = process.argv.slice(2);
const MODE_PARAM = '--mode=';
let serverMode = 'auto'; // Default mode is auto

// Check if mode is specified
for (const arg of args) {
  if (arg.startsWith(MODE_PARAM)) {
    serverMode = arg.substring(MODE_PARAM.length);
    break;
  }
}

// Import services, models, and routes
const { initSocketIO } = require('./services/socketService');
const { initRedisPublisher, initRedisDBSubscriber, publishGoldPrices, initCache } = require('./services/redisService');
const goldPriceController = require('./controllers/goldPriceController');
const goldPriceRoutes = require('./routes/goldPriceRoutes');

// Initialize Express application
const app = express();
const server = http.createServer(app);

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Register routes
app.use(goldPriceRoutes);

// Theo dõi thời gian cập nhật cuối cùng
let lastUpdateTime = new Date();
let lastPublishedPrices = null;
let updateInterval = null;

// Initialize server
async function initServer() {
  try {
    // Connect to Redis publisher
    await initRedisPublisher();
    
    // Connect to Redis DB subscriber
    await initRedisDBSubscriber();
    
    // Initialize cache with initial data
    await initCache();
    
    // Initialize Socket.IO
    await initSocketIO(server);

    // Xử lý theo mode
    if (serverMode === 'auto') {
      console.log('Server starting in AUTO mode - Will sync data from API automatically');
      
      // Schedule periodic updates
      updateInterval = setInterval(async () => {
        try {
          // Fetch gold prices directly from API
          const goldPrices = await goldPriceController.fetchPrices();
          
          // Publish updated prices to Redis channels
          // DB update will happen via the DB subscriber
          if (goldPrices && goldPrices.length > 0) {
            const hasUpdated = await publishGoldPrices(goldPrices);
            
            if (hasUpdated) {
              // Cập nhật thời gian cập nhật cuối và dữ liệu đã publish
              lastUpdateTime = new Date();
              lastPublishedPrices = goldPrices;
              console.log(`Gold prices updated at ${lastUpdateTime.toLocaleTimeString()}`);
            } else {
              // Log thời gian từ lần cập nhật cuối cùng
              const timeSinceLastUpdate = Math.floor((new Date() - lastUpdateTime) / 1000);
              console.log(`No changes in gold prices for ${timeSinceLastUpdate} seconds`);
            }
          }
        } catch (error) {
          console.error('Failed to update gold prices:', error);
        }
      }, 5000); // Update every 5 seconds
    } else if (serverMode === 'manual') {
      console.log('Server starting in MANUAL mode - Data will NOT be synced from API');
      console.log('Use the /api/add endpoint to manually update gold prices');
      
      // Fetch initial data (one time) to ensure we have something to display
      try {
        const currentData = await goldPriceController.fetchPrices();
        if (currentData && currentData.length > 0) {
          await publishGoldPrices(currentData);
          console.log('Initial data loaded. Future updates must be done manually.');
        }
      } catch (error) {
        console.warn('Could not load initial data:', error.message);
        console.log('You must add data manually using the /api/add endpoint');
      }
    } else {
      console.warn(`Unknown mode: ${serverMode}. Valid modes are 'auto' or 'manual'. Defaulting to 'auto'`);
      serverMode = 'auto';
    }
    
    // Start the server
    const PORT = process.env.PORT || 3010;
    server.listen(PORT, () => {
      console.log(`Server running on port ${PORT} in ${serverMode.toUpperCase()} mode`);
    });
  } catch (error) {
    console.error('Failed to initialize server:', error);
    process.exit(1);
  }
}

// Handle server shutdown
function shutdownServer() {
  console.log('Shutting down server...');
  
  // Clear update interval if running
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  
  // Close server and exit
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  shutdownServer();
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  shutdownServer();
});

// Handle termination signals
process.on('SIGTERM', shutdownServer);
process.on('SIGINT', shutdownServer);

// Start the server
initServer(); 