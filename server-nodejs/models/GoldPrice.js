const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const GoldPrice = sequelize.define('GoldPrice', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    type: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    karat: {
      type: DataTypes.STRING,
      allowNull: false
    },
    purity: {
      type: DataTypes.STRING,
      allowNull: false
    },
    buy_price: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    sell_price: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    updated_at: {
      type: DataTypes.STRING,
      allowNull: false
    }
  }, {
    tableName: 'gold_prices',
    timestamps: false
  });

  return GoldPrice;
}; 