import React, { useState, useEffect } from 'react';
import { 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Typography,
  Box,
  Tooltip
} from '@mui/material';
import ArrowDropUpIcon from '@mui/icons-material/ArrowDropUp';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import InfoIcon from '@mui/icons-material/Info';

const GoldPriceTable = ({ goldPrices, updateCount }) => {
  // Format giá theo tiền Việt Nam
  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      maximumFractionDigits: 0
    }).format(price);
  };

  // Log khi nhận dữ liệu mới
  useEffect(() => {
    console.log(`GoldPriceTable - Rendering update #${updateCount}`, goldPrices);
  }, [goldPrices, updateCount]);

  return (
    <Paper 
      sx={{ 
        overflow: 'hidden',
        borderRadius: '16px',
        height: '100%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
      }}
    >
      <Box
        sx={{
          p: 2,
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          borderBottom: '1px solid',
          borderColor: 'primary.light',
        }}
      >
        <Typography variant="h6" fontWeight="bold">
          Bảng giá vàng (Cập nhật #{updateCount})
        </Typography>
      </Box>
      
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Loại vàng</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Giá mua</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Giá bán</TableCell>
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Chênh lệch</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(goldPrices).map(([key, value]) => {
              // Bỏ qua các mục không có dữ liệu
              if (!value.name) return null;
              
              const difference = value.sell - value.buy;
              
              return (
                <TableRow 
                  key={`${key}-${updateCount}`} // Đảm bảo force re-render khi dữ liệu mới đến
                  sx={{ 
                    '&:last-child td, &:last-child th': { border: 0 },
                    '&:hover': { bgcolor: 'rgba(212, 175, 55, 0.05)' }
                  }}
                >
                  <TableCell component="th" scope="row">
                    <Box display="flex" alignItems="center">
                      <Typography fontWeight="medium">{value.name}</Typography>
                      <Tooltip title={`Key: ${key}`}>
                        <InfoIcon fontSize="small" sx={{ ml: 1, color: 'action.disabled', fontSize: '16px' }} />
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell 
                    align="right"
                    sx={{
                      color: 'success.main',
                      fontWeight: 'medium',
                      position: 'relative'
                    }}
                  >
                    {formatPrice(value.buy)}
                  </TableCell>
                  <TableCell 
                    align="right"
                    sx={{
                      color: 'secondary.main',
                      fontWeight: 'medium',
                      position: 'relative'
                    }}
                  >
                    {formatPrice(value.sell)}
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      fontWeight="medium"
                      sx={{ color: 'text.secondary' }}
                    >
                      {formatPrice(difference)}
                    </Typography>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default GoldPriceTable; 