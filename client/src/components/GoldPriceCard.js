import React, { memo } from 'react';
import { Card, CardContent, Typography, Box, Divider } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';

// Sử dụng memo để chỉ re-render khi props thay đổi
const GoldPriceCard = memo(({ title, buy, sell, Icon }) => {
  // Format giá theo tiền Việt Nam
  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      maximumFractionDigits: 0
    }).format(price);
  };

  // Log khi component render lại
  console.log(`GoldPriceCard ${title} rendering - Buy: ${buy}, Sell: ${sell}`);

  return (
    <Card
      sx={{
        borderRadius: '16px',
        position: 'relative',
        overflow: 'visible',
        height: '100%',
        border: '1px solid',
        borderColor: 'primary.light',
        transition: 'transform 0.3s ease',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: '0 8px 24px rgba(212, 175, 55, 0.2)',
        }
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: '-20px',
          left: '20px',
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          bgcolor: 'primary.main',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
        }}
      >
        <MonetizationOnIcon />
      </Box>
      
      <CardContent sx={{ p: 3, pt: 4 }}>
        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
          {title}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Giá mua:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUpIcon 
              sx={{ 
                color: 'success.main',
                mr: 1
              }} 
            />
            <Typography variant="h5" fontWeight="bold" color="success.main">
              {formatPrice(buy)}
            </Typography>
          </Box>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box>
          <Typography variant="body2" color="text.secondary">
            Giá bán:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingDownIcon 
              sx={{ 
                color: 'secondary.main',
                mr: 1
              }} 
            />
            <Typography variant="h5" fontWeight="bold" color="secondary.main">
              {formatPrice(sell)}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
});

export default GoldPriceCard; 