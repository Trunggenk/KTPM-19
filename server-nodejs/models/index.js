const { Sequelize } = require('sequelize');
const path = require('path');

// Configure the database connection
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: path.join(__dirname, '../db/app.db'),
  logging: false
});

// Initialize models
const GoldPrice = require('./GoldPrice')(sequelize);

// Sync all models with the database
(async () => {
  try {
    await sequelize.sync();
    console.log('Database synchronized successfully.');
  } catch (error) {
    console.error('Failed to sync database:', error);
  }
})();

module.exports = {
  sequelize,
  GoldPrice
}; 