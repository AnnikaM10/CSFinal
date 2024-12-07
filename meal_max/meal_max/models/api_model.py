from dataclasses import dataclass
import logging
import os
from dotenv import load_dotenv
import sqlite3
from typing import Any
import requests

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger

load_dotenv()
api_key = os.getenv("API_KEY")
# Initialize the BattleModel

api_base = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='

@dataclass
class UserStock:
    id: int
    symbol: str
    quantity: int
    user_id: int #relation database

    def __post_init__(self):

        if self.quantity < 0:
            raise ValueError("Quantity must be a positive value.")
        
def get_stock_price(symbol: str) -> float:
    """Fetches the current closing price of a stock from the external API."""
    try:
        # Construct API URL for the stock symbol
        full_url = f"{api_base}function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        stock_data = response.json()

        if "Time Series (Daily)" not in stock_data:
            raise ValueError(f"Stock symbol '{symbol}' data not found.")
        
        daily_data = stock_data["Time Series (Daily)"]
        recent_date = max(daily_data.keys())  # Get the most recent date
        close_price = float(daily_data[recent_date]["4. close"])  # Get closing price
        
        # Store the price in the memory (for quick access)
        stock_prices[symbol] = close_price ##### NEED TO FIGURE OUT HOW TO STORE TO DB
        return close_price

    except requests.RequestException as e:
        raise ConnectionError(f"Error fetching data from API: {str(e)}")
    except ValueError as e:
        raise e

def get_user_stocks() -> dict:
    """Fetches the user's stock portfolio from the database."""
    # Stubbed example - replace with actual database query logic
    return {"AAPL": 5, "TSLA": 3}

def calculate_portfolio_value(portfolio: dict, stock_prices: dict) -> float:
    """Calculates the total value of the user's portfolio."""
    total_value = 0
    for symbol, quantity in portfolio.items():
        if symbol in stock_prices:
            total_value += quantity * stock_prices[symbol]
    return total_value

def update_stock_quantity(symbol: str, quantity: int):
    """Updates the user's stock quantity in the database."""
    # Stubbed logic to update stock quantity in the database
    pass

def remove_stock(symbol: str):
    """Removes a stock from the user's portfolio in the database."""
    # Stubbed logic to remove stock from the database
    pass

    
