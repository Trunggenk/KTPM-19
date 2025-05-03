import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Grid, Paper, Divider, Chip } from '@mui/material';
import { io } from 'socket.io-client';
import GoldPriceCard from './components/GoldPriceCard';
import GoldPriceTable from './components/GoldPriceTable';
import Header from './components/Header';

// Mapping cho các loại vàng
const goldTypeMapping = {
  gold_1: 'SJC1',
  gold_2: 'BTMC',
  gold_3: 'BTMC99',
  gold_4: 'Ring',
  gold_5: 'Raw',
  gold_6: 'Jewelry',
  gold_7: 'SJC7'
};

function App() {
  const [goldPrices, setGoldPrices] = useState({
    SJC1: { buy: 0, sell: 0, name: 'Vàng SJC 1L', date: '' },
    SJC7: { buy: 0, sell: 0, name: 'Vàng SJC 5c, 2c, 1c', date: '' },
    BTMC: { buy: 0, sell: 0, name: 'Vàng BTMC', date: '' },
    BTMC99: { buy: 0, sell: 0, name: 'Vàng BTMC 99.9', date: '' },
    Ring: { buy: 0, sell: 0, name: 'Nhẫn trơn', date: '' },
    Raw: { buy: 0, sell: 0, name: 'Vàng nguyên liệu', date: '' },
    Jewelry: { buy: 0, sell: 0, name: 'Trang sức', date: '' }
  });
  
  const [lastUpdate, setLastUpdate] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [dataReceived, setDataReceived] = useState(false);
  const [updateCount, setUpdateCount] = useState(0); // Thêm một counter để theo dõi cập nhật

  useEffect(() => {
    // Khởi tạo kết nối socket
    const socket = io('http://localhost:3010');
    
    // Xử lý sự kiện kết nối
    socket.on('connect', () => {
      setConnectionStatus('Kết nối thành công');
      console.log('Connected to server');
    });
    
    // Xử lý sự kiện ngắt kết nối
    socket.on('disconnect', () => {
      setConnectionStatus('Mất kết nối');
      console.log('Disconnected from server');
    });
    
    // Nhận cập nhật giá vàng theo thời gian thực
    socket.on('gold-prices-updated', (data) => {
      console.log('Received gold prices from server:', data);
      updatePrices(data);
      setDataReceived(true);
      setUpdateCount(prev => prev + 1); // Tăng counter mỗi khi nhận được dữ liệu mới
    });
    
    // Bổ sung timeout để phát hiện nếu không nhận được dữ liệu ban đầu
    const initialDataTimeout = setTimeout(() => {
      if (!dataReceived) {
        setConnectionStatus('Không nhận được dữ liệu ban đầu');
        console.warn('No initial data received from WebSocket after timeout');
      }
    }, 5000);
    
    // Dọn dẹp khi component unmount
    return () => {
      socket.disconnect();
      clearTimeout(initialDataTimeout);
    };
  }, [dataReceived]);
  
  // Cập nhật dữ liệu giá vàng - luôn cập nhật mà không cần so sánh
  const updatePrices = (data) => {
    if (Array.isArray(data) && data.length > 0) {
      console.log(`App - Updating prices with ${data.length} items (update #${updateCount + 1})`);
      
      // Tạo một đối tượng mới hoàn toàn để đảm bảo React phát hiện thay đổi
      const updatedPrices = { ...goldPrices };
      
      // Reset tất cả các giá trị về 0 trước khi cập nhật - đảm bảo dữ liệu mới sẽ ghi đè
      Object.keys(updatedPrices).forEach(key => {
        updatedPrices[key] = { 
          buy: 0, 
          sell: 0, 
          name: updatedPrices[key].name, 
          date: '' 
        };
      });
      
      // Xử lý từng mục giá vàng từ dữ liệu mới
      data.forEach(item => {
        // Log thông tin về loại vàng để debug
        console.log(`Processing item: type=${item.type}, name=${item.name}, buy=${item.buy_price}, sell=${item.sell_price}`);
        
        // Map loại vàng từ server sang client
        const clientType = goldTypeMapping[item.type] || 'SJC1';
        console.log(`Mapped to client type: ${clientType}`);
        
        // Cập nhật giá cho loại vàng này
        updatedPrices[clientType] = {
          buy: item.buy_price,
          sell: item.sell_price,
          name: item.name,
          date: item.updated_at
        };
      });
      
      // Force cập nhật state bằng một đối tượng hoàn toàn mới
      setGoldPrices({ ...updatedPrices });
      
      // Cập nhật thời gian cập nhật cuối
      if (data[0] && data[0].updated_at) {
        setLastUpdate(data[0].updated_at);
      }
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', pb: 6 }}>
      <Header />
      
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Paper 
          elevation={0}
          sx={{ 
            p: 2, 
            mb: 4, 
            borderRadius: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: 'primary.light',
            color: 'primary.dark'
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            Giá Vàng Việt Nam
          </Typography>
          <Box>
            <Chip 
              label={dataReceived ? `Cập nhật: ${lastUpdate} (${updateCount})` : 'Đang chờ dữ liệu...'}
              size="small"
              sx={{ mr: 1, fontWeight: 500 }}
            />
            <Chip 
              label={connectionStatus}
              color={connectionStatus === 'Kết nối thành công' ? 'success' : 'warning'}
              size="small"
              sx={{ fontWeight: 500 }}
            />
          </Box>
        </Paper>
        
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="Vàng SJC 1L"
              buy={goldPrices.SJC1.buy}
              sell={goldPrices.SJC1.sell}
              Icon="SJC"
              key={`SJC1-${updateCount}`}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="SJC 5c, 2c, 1c"
              buy={goldPrices.SJC7.buy}
              sell={goldPrices.SJC7.sell}
              Icon="SJC"
              key={`SJC7-${updateCount}`}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="Vàng BTMC"
              buy={goldPrices.BTMC.buy}
              sell={goldPrices.BTMC.sell}
              Icon="BTMC"
              key={`BTMC-${updateCount}`}
            />
          </Grid>
        </Grid>
        
        {/* Row 2 */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="Nhẫn trơn"
              buy={goldPrices.Ring.buy}
              sell={goldPrices.Ring.sell}
              Icon="Ring"
              key={`Ring-${updateCount}`}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="Vàng nguyên liệu"
              buy={goldPrices.Raw.buy}
              sell={goldPrices.Raw.sell}
              Icon="Raw"
              key={`Raw-${updateCount}`}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <GoldPriceCard 
              title="BTMC 99.9"
              buy={goldPrices.BTMC99.buy}
              sell={goldPrices.BTMC99.sell}
              Icon="BTMC"
              key={`BTMC99-${updateCount}`}
            />
          </Grid>
        </Grid>
        
        <GoldPriceTable 
          goldPrices={goldPrices} 
          updateCount={updateCount}
        />
      </Container>
    </Box>
  );
}

export default App; 