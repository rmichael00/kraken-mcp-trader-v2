# Kraken MCP Trader

A robust trading bot that integrates with Kraken exchange using Model Context Protocol (MCP) for Windows. This bot enables secure trading operations through Claude with comprehensive error handling and rate limiting.

## Features

- Secure API key management with environment variables
- Real-time market data monitoring with error handling
- Rate-limited API calls to prevent throttling
- Automated retry logic for failed operations
- Comprehensive logging system
- MCP integration for Claude with proper error handling
- Support for multiple trading pairs
- Limit order execution (buy/sell) with validation

## Prerequisites

- Python 3.8+
- Windows OS
- Kraken API credentials
- Claude Desktop with MCP support
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rmichael00/kraken-mcp-trader-v2.git
cd kraken-mcp-trader-v2
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your Kraken API credentials
- Configure MCP server settings

## Configuration

1. Trading Bot Settings (`config.json`):
- Trading pairs
- Order sizes
- Price precision
- Rate limiting parameters
- Retry settings

2. MCP Configuration:
- Server port
- API endpoints
- Authentication settings
- Rate limits

## Security Features

- Encrypted API key storage
- Rate limiting to prevent API abuse
- Input validation for all operations
- Secure error logging (no sensitive data)
- Connection encryption
- Session management

## Usage

1. Start the MCP server:
```bash
python mcp_server/server.py
```

2. Configure Claude Desktop:
- Add the MCP server configuration
- Test the connection

3. Common Commands:
```python
# Get account balance
/balance

# Place buy limit order
/buy pair=XBT/USD price=50000 volume=0.1

# Place sell limit order
/sell pair=XBT/USD price=55000 volume=0.1

# Check open orders
/orders

# Cancel order
/cancel order_id=ABCD-1234
```

## Error Handling

The bot implements comprehensive error handling:
- API connection issues
- Rate limiting
- Invalid input validation
- Order execution failures
- Network timeouts
- Data validation errors

## Logging

All operations are logged with appropriate detail levels:
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Operation failures
- DEBUG: Detailed debugging info

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Disclaimer

Trading cryptocurrencies carries risk. This bot is for educational purposes only.
