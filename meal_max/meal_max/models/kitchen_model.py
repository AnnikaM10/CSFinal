from dataclasses import asdict, dataclass
import logging
from typing import Any, List
import os
from dotenv import load_dotenv
import requests

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from meal_max.clients.redis_client import redis_client
from meal_max.db import db
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)

load_dotenv()
api_key = os.getenv("API_KEY")
api_base = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='

@dataclass
class UserStocks(db.Model):
    __tablename__ = 'stocks'

    id: int = db.Column(db.Integer, primary_key=True)
    symbol: str = db.Column(db.String(80), unique=True, nullable=False)
    price: float = db.Column(db.Float, nullable=False)
    quantity: int = db.Column(db.Integer, default=0)

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.quantity < 0:
            raise ValueError("Quantity must be at least 0.")
    
    @classmethod
    def get_stock_price(cls, symbol: str ) -> float:
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
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching data from API: {str(e)}")
        
        price_for_stock = cls(symbol=symbol, price=close_price)
        try:
            db.session.add(price_for_stock)
            db.session.commit()
            logger.info("Stock Price successfully added to the database: %s at %f", symbol, close_price)
            return close_price
        except ValueError as e:
            raise e
    
    @classmethod
    def add_stock(cls, symbol: str) -> None:
        """Adds a new stock entry (only the symbol) to the database."""
        # Check if the stock symbol already exists
        stock = cls.query.filter_by(symbol=symbol).first()
        
        if stock:
            raise ValueError(f"Stock with symbol '{symbol}' already exists.")
        
        # If stock does not exist, create a new entry with only the symbol
        try:
            new_stock = cls(symbol=symbol, price=0.0, quantity=0)  # Price and quantity default to 0
            db.session.add(new_stock)
            db.session.commit()
            logger.info("New stock symbol added: %s", symbol)
        except Exception as e:
            db.session.rollback()
            logger.error("Error adding new stock symbol: %s", str(e))
            raise

    @classmethod
    def up_stock_quantity(cls, symbol: str, quantity: int) -> None:
        """Increases the quantity of an existing stock."""
        stock = cls.query.filter_by(symbol=symbol).first()
        if not stock:
            raise ValueError(f"Stock with symbol '{symbol}' not found.")
        
        stock.quantity += quantity
        try:
            db.session.commit()
            logger.info("Stock quantity increased for: %s by %d", symbol, quantity)
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating stock quantity: %s", str(e))
            raise
    
    @classmethod
    def dec_stock_quantity(cls, symbol: str, quantity: int) -> None:
        """Decreases the quantity of an existing stock."""
        stock = cls.query.filter_by(symbol=symbol).first()
        if not stock:
            raise ValueError(f"Stock with symbol '{symbol}' not found.")
        
        if stock.quantity < quantity:
            raise ValueError(f"Insufficient stock quantity for '{symbol}'.")
        
        stock.quantity -= quantity
        try:
            db.session.commit()
            logger.info("Stock quantity decreased for: %s by %d", symbol, quantity)
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating stock quantity: %s", str(e))
            raise


    @classmethod
    def get_user_stocks(cls) -> list:
        """Fetches all stock records for the user."""
        try:
            stocks = cls.query.all()
            return [stock.symbol for stock in stocks]
        except Exception as e:
            logger.error("Error fetching user stocks: %s", str(e))
            raise

def update_cache_for_meal(mapper, connection, target):
    """
    Update the Redis cache for a meal entry after an update or delete operation.

    This function is intended to be used as an SQLAlchemy event listener for the
    `after_update` and `after_delete` events on the Meals model. When a meal is
    updated or deleted, this function will either update the corresponding Redis
    cache entry with the new meal details or remove the entry if the meal has
    been marked as deleted.

    Args:
        mapper (Mapper): The SQLAlchemy Mapper object, which provides information
                         about the model being updated (automatically passed by SQLAlchemy).
        connection (Connection): The SQLAlchemy Connection object used for the
                                 database operation (automatically passed by SQLAlchemy).
        target (Meals): The instance of the Meals model that was updated or deleted.
                        The `target` object contains the updated meal data.

    Side-effects:
        - If the meal is marked as deleted (`target.deleted` is True), the function
          removes the corresponding cache entry from Redis.
        - If the meal is not marked as deleted, the function updates the Redis cache
          entry with the latest meal data using the `hset` command.
    """
    cache_key = f"stock:{target.id}"
    if target.deleted:
        redis_client.delete(cache_key)
    else:
        redis_client.hset(
            cache_key,
            mapping={k.encode(): str(v).encode() for k, v in asdict(target).items()}
        )

# Register the listener for update and delete events
event.listen(UserStocks, 'after_update', update_cache_for_meal)
event.listen(UserStocks, 'after_delete', update_cache_for_meal)
