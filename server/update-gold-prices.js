const fetch = require('node-fetch');

// Initial gold prices (in VND)
const initialPrices = {
    'sjc': 72500000,      // SJC gold bar
    'sjc_nhan': 71800000, // SJC gold ring
    '24k': 71000000,      // 24K gold
    '18k': 53200000,      // 18K gold
    '14k': 41500000,      // 14K gold
    '9k': 26700000        // 9K gold
};

// Function to generate random price changes
function getRandomPriceChange() {
    // Determine if price goes up or down
    const direction = Math.random() > 0.5 ? 1 : -1;
    
    // Generate a random change between 10,000 and 100,000 VND
    const change = Math.floor(Math.random() * 90000 + 10000);
    
    return direction * change;
}

// Function to update prices with random changes
function updatePrices(currentPrices) {
    const newPrices = { ...currentPrices };
    
    // For each gold type, apply a random change
    for (const type of Object.keys(newPrices)) {
        // 70% chance of a price change
        if (Math.random() < 0.7) {
            const change = getRandomPriceChange();
            newPrices[type] = Math.max(newPrices[type] + change, 100000); // Ensure price doesn't go below 100,000 VND
        }
    }
    
    return newPrices;
}

// Function to send updated prices to the server
async function sendPricesToServer(prices) {
    try {
        const response = await fetch('http://localhost:3010/api/update-gold', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prices }),
        });
        
        if (response.ok) {
            console.log('Gold prices updated successfully');
            console.log(prices);
        } else {
            console.error('Failed to update gold prices');
        }
    } catch (error) {
        console.error('Error sending prices to server:', error);
    }
}

// Main function to start the simulation
async function startSimulation() {
    console.log('Starting gold price simulation...');
    
    // Initialize with the starting prices
    let currentPrices = { ...initialPrices };
    
    // Send initial prices
    await sendPricesToServer(currentPrices);
    
    // Update prices every 3 seconds
    setInterval(async () => {
        currentPrices = updatePrices(currentPrices);
        await sendPricesToServer(currentPrices);
    }, 3000);
}

// Start the simulation
startSimulation(); 