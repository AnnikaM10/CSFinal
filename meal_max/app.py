from dotenv import load_dotenv
import os
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from meal_max.models.api_model import UserStock
from meal_max.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)
####################################################
#
# Healthchecks
#
####################################################


@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and meals table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if meals table exists...")
        check_table_exists("meals")
        app.logger.info("meals table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


##########################################################
#
# Stocks
#
##########################################################
#This is to first buy a stock and add to database
@app.route('/api/stock_price', methods=['GET'])
def view_stock() -> Response:

    app.logger.info('Finding stock price')

    #takes input via JSON data
    #  from request
    data = request.get_json()
    symbol = data["symbol"]
    quantity = data["quantity"]

    if not data or "symbol" not in data or "quantity" not in data:
        return jsonify({"error": "Stock symbol and quantity are required"}), 400
    
    # Validate stock symbol format
    if not symbol or not symbol.isalnum():
        return jsonify({"error": "Invalid stock symbol format"}), 400

    try:

        price = UserStock.get_stock_price(symbol)

    except request.RequestException as e:
        return jsonify({"error": f"Error fetching stock data: {str(e)}"}), 500
    
    try:
        #print out the stock symbol and its price 

        ## print_stock_price(symbol, stock_price)
        return jsonify({"message": f"Stock {symbol} is at ${price} today"}), 201
    except Exception as e:
        return jsonify({"error": f"Error adding stock to the database: {str(e)}"}), 500



@app.route('/api/add-stock', methods=['POST'])
def buy_stock() -> Response:
    """Route to add stock to the user's portfolio."""
    data = request.get_json()
    
    if not data or "symbol" not in data or "quantity" not in data:
        return jsonify({"error": "Stock symbol and quantity are required"}), 400
    
    symbol = data["symbol"]
    quantity = data["quantity"]

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    try:
        # Get stock price
        price = UserStock.get_stock_price(symbol)
        
        # Update stock quantity in the database (stub)
        UserStock.update_stock_quantity(symbol, quantity)
        
        return jsonify({"message": f"Successfully added {quantity} shares of {symbol} at {price} each"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-stock', methods=['POST'])
def sell_stock() -> Response:
    """Route to delete (sell) stock from the user's portfolio."""
    data = request.get_json()
    
    if not data or "symbol" not in data or "quantity" not in data:
        return jsonify({"error": "Stock symbol and quantity are required"}), 400
    
    symbol = data["symbol"]
    quantity = data["quantity"]

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    try:
        portfolio = UserStock.get_user_stocks()
        current_quantity = portfolio.get(symbol, 0)

        if current_quantity < quantity:
            return jsonify({"error": "Not enough stock to sell"}), 400

        # Update the stock quantity in the database (stub)
        if current_quantity == quantity:
            UserStock.remove_stock(symbol)
        else:
            UserStock.update_stock_quantity(symbol, current_quantity - quantity)

        return jsonify({"message": f"Successfully sold {quantity} shares of {symbol}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/view_port', methods=['GET'])
def view_portfolio() -> Response:
    """Route to view the user's stock portfolio."""
    try:
        portfolio = UserStock.get_user_stocks()
        if not portfolio:
            return jsonify({"error": "No stocks found in portfolio"}), 404
        return jsonify({"portfolio": portfolio}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calc_port', methods=['GET'])
def calc_portfolio() -> Response:
    """Route to calculate the user's portfolio value."""
    try:
        # Get the user's portfolio
        portfolio = UserStock.get_user_stocks()

        if not portfolio:
            return jsonify({"error": "No stocks found in portfolio"}), 404

        # Fetch stock prices for each symbol
        stock_prices = {}
        for symbol in portfolio.keys():
            stock_prices[symbol] = UserStock.get_stock_price(symbol)

        # Calculate the portfolio value
        portfolio_value = UserStock.calculate_portfolio_value(portfolio, stock_prices)

        return jsonify({"portfolio_value": portfolio_value}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)