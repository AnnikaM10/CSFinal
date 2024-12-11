from dataclasses import asdict, dataclass
import logging
from typing import Any, List
import os
from dotenv import load_dotenv
import requests

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from stock_portfolio.clients.redis_client import redis_client
from stock_portfolio.db import db
from stock_portfolio.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)

load_dotenv()
api_key = os.getenv("API_KEY")
api_base = 'https://www.alphavantage.co/query?'

@dataclass
class UserStocks(db.Model):
    __tablename__ = 'stocks'

    id: int = db.Column(db.Integer, primary_key=True)
    symbol: str = db.Column(db.String(80), unique=True, nullable=False)
    price: float = db.Column(db.Float, nullable=False)
    quantity: int = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=False)

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.quantity < 0:
            raise ValueError("Quantity must be at least 0.")
    
    #called second
    @classmethod
    def get_stock_price(cls, symbol: str ) -> float:
        """
        Fetches the current closing price of a stock from an external API and updates the database.

        Args:
            symbol (str): The stock symbol to fetch the price for.

        Returns:
            float: The most recent closing price of the stock.

        Raises:
            ConnectionError: If there is an issue with fetching data from the external API.
            ValueError: If the API response format is invalid or the required data is missing.
            Exception: For any errors that occur during database operations.
            """
        try:
            # Construct API URL for the stock symbol
            full_url = f"{api_base}function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
            response = requests.get(full_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            stock_data = response.json()

            # if "Meta Data" not in stock_data or "Time Series (Daily)" not in stock_data:
            #     raise ValueError(f"Invalid API response format for symbol '{symbol}'. Response: {stock_data}")
        
            daily_data = stock_data["Time Series (Daily)"]
            # if not daily_data:
            #     raise ValueError(f"No daily data available for symbol '{symbol}'.")
            recent_date = max(daily_data.keys())  # Get the most recent date
            day_data = daily_data.get(recent_date)

            # if not day_data or "4. close" not in day_data:
            #     raise KeyError(f"Missing closing price for the most recent date '{recent_date}'.")
            
            close_price = float(day_data["4. close"])
        
            # Store the price in the memory (for quick access)
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching data from API: {str(e)}")
        
        try:
            # Check if the stock exists in the database
            stock = cls.query.filter_by(symbol=symbol).first()

            if stock:
                # Update the existing stock's price
                stock.price = close_price
                logger.info("Stock price updated: %s to %f", symbol, close_price)
                db.session.commit()
            

            # Commit the changes to the database
            
            return close_price

        except Exception as e:
            db.session.rollback()
            logger.error("Error updating or adding stock: %s", str(e))
            raise
    
    #called first
    @classmethod
    def add_stock(cls, symbol: str) -> None:
        """
        Adds a new stock entry (only the symbol) to the database.

        Args:
            symbol (str): The stock symbol to be added.

        Raises:
            ValueError: If the stock symbol already exists in the database.
            ValueError: If the stock symbol is not uppercase.
            ValueError: If the stock symbol exceeds four characters.
            Exception: For any errors that occur during database operations.
        """
        # Check if the stock symbol already exists
        stock = cls.query.filter_by(symbol=symbol).first()
        
        if stock:
            raise ValueError(f"Stock with symbol '{symbol}' already exists.")
        
        if not symbol.isupper():
            raise ValueError(f"Stock with symbol '{symbol}' is invalid.")
    
        if len(symbol) > 4:
            raise ValueError(f"Stock with symbol '{symbol}' is invalid.")

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
        """
        Increases the quantity of an existing stock.

        Args:
            symbol (str): The stock symbol whose quantity is to be increased.
            quantity (int): The quantity to add to the existing stock.

        Raises:
            ValueError: If the stock symbol does not exist in the database.
            ValueError: If the quantity is not greater than zero.
            Exception: For any errors that occur during database operations.
        """
        stock = cls.query.filter_by(symbol=symbol).first()
        if not stock:
            raise ValueError(f"Stock with symbol '{symbol}' not found.")
        if quantity <=0: 
            raise ValueError("Quantity must be at least 0.")
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
        """
        Decreases the quantity of an existing stock.

        Args:
            symbol (str): The stock symbol whose quantity is to be decreased.
            quantity (int): The quantity to subtract from the existing stock.

        Raises:
            ValueError: If the stock symbol does not exist in the database.
            ValueError: If the quantity to decrease exceeds the current stock quantity.
            ValueError: If the quantity is not greater than zero.
            Exception: For any errors that occur during database operations.
        """
        stock = cls.query.filter_by(symbol=symbol).first()
        if not stock:
            raise ValueError(f"Stock with symbol '{symbol}' not found.")
        
        if stock.quantity < quantity:
            raise ValueError(f"Insufficient stock quantity for '{symbol}'.")
        if quantity <=0: 
            raise ValueError("Quantity must be at least 0.")
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
        """
        Fetches all stock records for the user.

        Returns:
            list: A list of stock symbols representing all the stocks the user owns.

        Raises:
            Exception: If there is an error while fetching stocks from the database.
        """
        try:
            stocks = cls.query.all()
            return [stock.symbol for stock in stocks]
        except Exception as e:
            logger.error("Error fetching user stocks: %s", str(e))
            raise

def update_cache_for_stock(mapper, connection, target):
    """
    Update the Redis cache for a stock entry after an update or delete operation.

    This function is intended to be used as an SQLAlchemy event listener for the
    `after_update` and `after_delete` events on the User_Stocks model. When a stock is
    updated or deleted, this function will either update the corresponding Redis
    cache entry with the new stock details or remove the entry if the stock has
    been marked as deleted.

    Args:
        mapper (Mapper): The SQLAlchemy Mapper object, which provides information
                         about the model being updated (automatically passed by SQLAlchemy).
        connection (Connection): The SQLAlchemy Connection object used for the
                                 database operation (automatically passed by SQLAlchemy).
        target (UserStock): The instance of the User_Stocks model that was updated or deleted.
                        The `target` object contains the updated stock data.

    Side-effects:
        - If the stock is marked as deleted (`target.deleted` is True), the function
          removes the corresponding cache entry from Redis.
        - If the stock is not marked as deleted, the function updates the Redis cache
          entry with the latest stock data using the `hset` command.
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
event.listen(UserStocks, 'after_update', update_cache_for_stock)
event.listen(UserStocks, 'after_delete', update_cache_for_stock)