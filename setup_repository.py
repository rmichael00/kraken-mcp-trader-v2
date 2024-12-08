import base64
import time
import os
import json
import requests
from typing import Dict, Optional
import logging

class GitHubRepoSetup:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('github_setup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('GitHubSetup')

    def retry_request(self, method, url: str, max_retries: int = 3, **kwargs) -> Optional[requests.Response]:
        """Execute request with retry logic and exponential backoff."""
        for attempt in range(max_retries):
            try:
                response = method(url, headers=self.headers, **kwargs)
                if response.status_code == 409:  # Conflict
                    self.logger.warning(f"Conflict detected, retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def encode_content(self, content: str) -> str:
        """Encode content to base64."""
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')

    def create_file(self, path: str, content: str) -> bool:
        """Create a file in the repository with proper encoding and error handling."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        
        encoded_content = self.encode_content(content)
        data = {
            "message": f"Add {path}",
            "content": encoded_content,
            "branch": "main"
        }

        try:
            response = self.retry_request(requests.put, url, json=data)
            if response and response.status_code in (201, 200):
                self.logger.info(f"Successfully created file: {path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to create file {path}: {str(e)}")
            return False

    def create_project_structure(self):
        """Create the entire project structure with proper error handling."""
        project_files = {
            # Core configuration files
            "requirements.txt": """krakenex==2.1.0
ta-lib==0.4.24
python-dotenv==0.19.2
websockets==10.3
fastapi==0.68.1
uvicorn==0.15.0
pydantic==1.8.2
requests==2.26.0
tenacity==8.2.2""",

            ".env.example": """KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here
MCP_PORT=8080
DEBUG_MODE=false
GITHUB_TOKEN=your_github_token_here""",

            "config.json": """{
    "trading_pairs": ["XBT/USD", "ETH/USD"],
    "default_order_size": 0.01,
    "max_open_orders": 5,
    "price_precision": 2,
    "quantity_precision": 8,
    "rate_limit": {
        "requests_per_minute": 60,
        "retry_delay": 5
    }
}""",

            # Project structure files will be added here
        }

        # Add more files as needed
        project_files.update({
            "kraken_bot/__init__.py": "",
            "kraken_bot/trading_bot.py": self.get_trading_bot_content(),
            "mcp_server/__init__.py": "",
            "mcp_server/server.py": self.get_mcp_server_content(),
            "mcp_server/config.json": self.get_mcp_config_content()
        })

        # Create each file with proper delays to avoid rate limiting
        for path, content in project_files.items():
            self.logger.info(f"Creating file: {path}")
            
            # Create directories if they don't exist in the repository
            if '/' in path:
                dir_path = os.path.dirname(path)
                if dir_path:
                    self.create_directory_structure(dir_path)
            
            if not self.create_file(path, content):
                self.logger.error(f"Failed to create {path}")
                return False
            time.sleep(1)  # Delay to avoid rate limiting
        
        return True

    def create_directory_structure(self, path: str):
        """Create directory structure by adding a .gitkeep file."""
        self.create_file(f"{path}/.gitkeep", "")

    def get_trading_bot_content(self) -> str:
        """Return the content for trading_bot.py"""
        return '''import krakenex
from decimal import Decimal
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class KrakenTradingBot:
    def __init__(self):
        self.kraken = krakenex.API(
            key=os.getenv('KRAKEN_API_KEY'),
            secret=os.getenv('KRAKEN_API_SECRET')
        )
        self.load_config()
        self.setup_logging()

    def load_config(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('KrakenBot')

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_balance(self):
        """Get account balance with retry logic."""
        try:
            return self.kraken.query_private('Balance')
        except Exception as e:
            self.logger.error(f'Error getting balance: {str(e)}')
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def place_limit_buy_order(self, pair: str, price: float, volume: float):
        """Place a limit buy order with retry logic."""
        try:
            order = {
                'pair': pair,
                'type': 'buy',
                'ordertype': 'limit',
                'price': str(price),
                'volume': str(volume)
            }
            result = self.kraken.query_private('AddOrder', order)
            self.logger.info(f'Placed buy order: {result}')
            return result
        except Exception as e:
            self.logger.error(f'Error placing buy order: {str(e)}')
            raise

    # Add more trading methods here
'''

    def get_mcp_server_content(self) -> str:
        """Return the content for mcp_server.py"""
        return '''from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
import sys
import os
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Add parent directory to path to import trading_bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kraken_bot.trading_bot import KrakenTradingBot

app = FastAPI()
bot = KrakenTradingBot()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MCPServer')

class OrderRequest(BaseModel):
    pair: str
    price: float
    volume: float

class CancelRequest(BaseModel):
    order_id: str

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@app.get('/balance')
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_balance():
    try:
        balance = bot.get_balance()
        if balance is None:
            raise HTTPException(status_code=500, detail='Failed to get balance')
        return balance
    except Exception as e:
        logger.error(f'Error in balance endpoint: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/order/buy')
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def place_buy_order(order: OrderRequest):
    try:
        result = bot.place_limit_buy_order(order.pair, order.price, order.volume)
        if result is None:
            raise HTTPException(status_code=500, detail='Failed to place buy order')
        return result
    except Exception as e:
        logger.error(f'Error in buy order endpoint: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints here

def start_server():
    uvicorn.run(app, host='127.0.0.1', port=int(os.getenv('MCP_PORT', 8080)))

if __name__ == '__main__':
    start_server()
'''

    def get_mcp_config_content(self) -> str:
        """Return the content for mcp_server/config.json"""
        return '''{
  "name": "kraken-trader",
  "version": "1.0.0",
  "description": "MCP server for Kraken trading bot",
  "endpoints": {
    "health": {
      "method": "GET",
      "path": "/health",
      "description": "Check server health"
    },
    "balance": {
      "method": "GET",
      "path": "/balance",
      "description": "Get account balance"
    },
    "buy": {
      "method": "POST",
      "path": "/order/buy",
      "description": "Place a limit buy order"
    }
  },
  "rate_limiting": {
    "requests_per_minute": 60,
    "retry_delay": 5
  },
  "security": {
    "require_authentication": true,
    "log_level": "INFO"
  }
}'''

def main():
    # Replace these with your actual values
    token = os.getenv("GITHUB_TOKEN")
    owner = "rmichael00"
    repo = "kraken-mcp-trader-v2"

    if not token:
        raise ValueError("GitHub token not found in environment variables")

    setup = GitHubRepoSetup(token, owner, repo)
    if setup.create_project_structure():
        print("Repository setup completed successfully!")
    else:
        print("Repository setup failed. Check the logs for details.")

if __name__ == "__main__":
    main()