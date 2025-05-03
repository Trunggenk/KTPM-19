import React from 'react';
import { AppBar, Toolbar, Typography, Box, Container } from '@mui/material';
import CurrencyExchangeIcon from '@mui/icons-material/CurrencyExchange';

const Header = () => {
  return (
    <AppBar position="static" elevation={0} sx={{ bgcolor: '#fff', color: 'primary.main' }}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <CurrencyExchangeIcon fontSize="large" sx={{ mr: 1 }} />
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              mr: 2,
              display: 'flex',
              fontWeight: 700,
              letterSpacing: '.05rem',
              color: 'primary.dark',
            }}
          >
            GOLDPRICE.VN
          </Typography>
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 500,
                color: 'secondary.main'
              }}
            >
              Cập nhật giá vàng trực tiếp
            </Typography>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 