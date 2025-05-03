import React from 'react';
import { Paper, Typography, Box, Divider } from '@mui/material';

const GoldPriceChart = ({ goldPrices }) => {
  // Tạo dữ liệu giả lập cho biểu đồ
  const sjcPrice = goldPrices.SJC.sell || 12000000;
  
  // Tạo một đồ thị giả lập với các giá trị ngẫu nhiên quanh SJC
  const generateChartPoints = () => {
    const basePrice = sjcPrice;
    const points = [];
    
    // Tạo 7 điểm với độ dao động ±3%
    for (let i = 0; i < 7; i++) {
      const variation = (Math.random() * 0.06 - 0.03); // -3% to +3%
      points.push({
        x: i,
        y: basePrice * (1 + variation)
      });
    }
    
    return points;
  };
  
  const chartPoints = generateChartPoints();
  
  // Tính các giá trị lớn nhất, nhỏ nhất
  const maxPrice = Math.max(...chartPoints.map(p => p.y));
  const minPrice = Math.min(...chartPoints.map(p => p.y));
  
  // Format giá
  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      maximumFractionDigits: 0
    }).format(price);
  };
  
  // Tạo đường đồ thị từ các điểm
  const chartPath = () => {
    // Quy đổi các điểm sang tọa độ SVG
    const width = 300;
    const height = 180;
    const padding = 20;
    
    const xScale = (index) => padding + (index * ((width - 2 * padding) / (chartPoints.length - 1)));
    const yScale = (value) => {
      const range = maxPrice - minPrice;
      return height - padding - ((value - minPrice) / range) * (height - 2 * padding);
    };
    
    // Tạo đường dẫn SVG
    const pathPoints = chartPoints.map((point, index) => {
      const x = xScale(index);
      const y = yScale(point.y);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    });
    
    // Thêm vùng màu gradient
    const firstX = xScale(0);
    const lastX = xScale(chartPoints.length - 1);
    const baseY = height - padding;
    
    const fillPath = [
      ...pathPoints,
      `L ${lastX} ${baseY}`,
      `L ${firstX} ${baseY}`,
      'Z'
    ];
    
    return {
      line: pathPoints.join(' '),
      fill: fillPath.join(' ')
    };
  };
  
  const { line, fill } = chartPath();
  
  return (
    <Paper 
      sx={{ 
        p: 3, 
        borderRadius: '16px',
        height: '100%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
        Biểu đồ giá vàng SJC
      </Typography>
      
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <svg width="100%" height="200" viewBox="0 0 300 200">
          <defs>
            <linearGradient id="goldGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(212, 175, 55, 0.6)" />
              <stop offset="100%" stopColor="rgba(212, 175, 55, 0)" />
            </linearGradient>
          </defs>
          
          {/* Vùng đổ màu */}
          <path d={fill} fill="url(#goldGradient)" />
          
          {/* Đường biểu đồ */}
          <path
            d={line}
            fill="none"
            stroke="#D4AF37"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* Các điểm trên biểu đồ */}
          {chartPoints.map((point, index) => (
            <circle
              key={index}
              cx={20 + (index * 40)}
              cy={200 - ((point.y - minPrice) / (maxPrice - minPrice) * 160) - 20}
              r="4"
              fill="#fff"
              stroke="#D4AF37"
              strokeWidth="2"
            />
          ))}
        </svg>
        
        <Box sx={{ mt: 2 }}>
          <Divider sx={{ mb: 2 }} />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Giá cao nhất:
            </Typography>
            <Typography variant="body2" fontWeight="bold" color="success.main">
              {formatPrice(maxPrice)}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Giá thấp nhất:
            </Typography>
            <Typography variant="body2" fontWeight="bold" color="secondary.main">
              {formatPrice(minPrice)}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Giá hiện tại:
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {formatPrice(sjcPrice)}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default GoldPriceChart; 