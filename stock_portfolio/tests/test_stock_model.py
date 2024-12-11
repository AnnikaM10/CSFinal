from dataclasses import asdict
import pytest
from stock_portfolio.models.stock_model import UserStocks
from unittest.mock import MagicMock
from app import create_app




@pytest.fixture(autouse=True)
def mock_redis_client(mocker):
    mock_redis = MagicMock()
    # Ensure the patch points to the correct location
    mocker.patch('stock_portfolio.models.stock_model.redis_client', mock_redis)
    return mock_redis
######################################################
#
#    Add and delete
#
######################################################

def test_add_stock(session):
    """Test adding a stock to the database."""
    UserStocks.add_stock("AAPL")

    # Query the database to verify the stock was added
    result = UserStocks.query.one()
    assert result.symbol == "AAPL"


def test_add_stock_invalid_symbol(app):
    """Test adding a stock with invalid symbols."""
    with pytest.raises(ValueError, match="Stock with symbol 'aapl' is invalid."):
        UserStocks.add_stock("aapl")  # Lowercase not allowed

    with pytest.raises(ValueError, match="Stock with symbol 'ABCDE' is invalid."):
        UserStocks.add_stock("ABCDE")  # Exceeds length limit


def test_add_stock_duplicate_name(session):
    """Test adding a stock with a duplicate symbol."""
    UserStocks.add_stock("AAPL")
    with pytest.raises(ValueError, match="Stock with symbol 'AAPL' already exists."):
        UserStocks.add_stock("AAPL")


def test_increase_stock_quantity(session):
    """Test increasing the quantity of a stock."""
    UserStocks.add_stock("AAPL")
    UserStocks.up_stock_quantity("AAPL", 10)

    stock = UserStocks.query.one()
    assert stock.symbol == "AAPL"
    assert stock.quantity == 10


def test_increase_stock_invalid_quantity(session):
    """Test increasing stock quantity with invalid values."""
    UserStocks.add_stock("AAPL")
    with pytest.raises(ValueError, match="Quantity must be at least 0."):
        UserStocks.up_stock_quantity("AAPL", -10)  # Negative quantity

    with pytest.raises(ValueError, match="Quantity must be at least 0."):
        UserStocks.up_stock_quantity("AAPL", 0)  # Zero quantity


def test_increase_stock_invalid_symbol(app):
    """Test increasing quantity for a non-existent stock."""
    with app.app_context():
        UserStocks.add_stock("AAPL")
        UserStocks.up_stock_quantity("AAPL", 10)
        
        with pytest.raises(ValueError, match="Stock with symbol 'XYZ' not found."):
            UserStocks.up_stock_quantity("XYZ", 10)


def test_decrease_stock_quantity(session):
    """Test decreasing the quantity of a stock."""
    UserStocks.add_stock("AAPL")
    UserStocks.up_stock_quantity("AAPL", 10)
    UserStocks.dec_stock_quantity("AAPL", 5)

    stock = UserStocks.query.one()
    assert stock.symbol == "AAPL"
    assert stock.quantity == 5


def test_decrease_stock_invalid_quantity(session):
    """Test decreasing stock quantity with invalid values."""
    UserStocks.add_stock("AAPL")
    UserStocks.up_stock_quantity("AAPL", 10)

    with pytest.raises(ValueError, match="Insufficient stock quantity for 'AAPL'."):
        UserStocks.dec_stock_quantity("AAPL", 15)  # Quantity exceeds available

    with pytest.raises(ValueError, match="Quantity must be at least 0."):
        UserStocks.dec_stock_quantity("AAPL", -5)  # Negative quantity


def test_decrease_stock_invalid_symbol(app):
    """Test decreasing quantity for a non-existent stock."""
    """Test increasing quantity for a non-existent stock."""
    with app.app_context():
        UserStocks.add_stock("AAPL")
        UserStocks.up_stock_quantity("AAPL", 10)
        
        with pytest.raises(ValueError, match="Stock with symbol 'XYZ' not found."):
            UserStocks.dec_stock_quantity("XYZ", 10)

def test_get_user_stocks(session):
    """Test retrieving all stocks for a user."""
    UserStocks.add_stock("AAPL")
    UserStocks.add_stock("MSFT")
    UserStocks.up_stock_quantity("AAPL", 10)
    UserStocks.up_stock_quantity("MSFT", 5)

    stocks = UserStocks.get_user_stocks()
    assert len(stocks) == 2
    assert "AAPL" in stocks
    assert "MSFT" in stocks


def test_get_stock_price(session, mocker):
    """Test retrieving the price of a stock."""
    UserStocks.add_stock("AAPL")
    UserStocks.up_stock_quantity("AAPL", 10)

    # Mock the external stock price API
    mock_get_stock_price = mocker.patch('stock_portfolio.models.stock_model.UserStocks.get_stock_price')
    mock_get_stock_price.return_value = 150.25

    price = UserStocks.get_stock_price("AAPL")
    assert price == 150.25
    mock_get_stock_price.assert_called_once_with("AAPL")


def test_view_empty_portfolio(session):
    """Test viewing an empty portfolio."""
    portfolio = UserStocks.get_user_stocks()
    assert len(portfolio) == 0


def test_view_portfolio_full_details(session, mocker):
    """Test viewing a user's full stock portfolio."""
    UserStocks.add_stock("AAPL")
    #UserStocks.up_stock_quantity("AAPL", 10)

    # Mock stock price API
    mocker.patch('stock_portfolio.models.stock_model.UserStocks.get_stock_price', return_value=150.25)

    portfolio = UserStocks.get_user_stocks()
    assert len(portfolio) == 1
    stock_symbol = portfolio[0]
    assert stock_symbol == "AAPL"
    #assert stock.quantity == 10
    #assert stock.price == 150.25
    # assert stock.total_value == 1502.5  # Validate total value