from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from stock_portfolio.db import db
from stock_portfolio.models.stock_model import UserStocks
from stock_portfolio.models.mongo_session_model import login_user, logout_user
from stock_portfolio.models.user_model import Users
import logging

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    user_stock = UserStocks()

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

    ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, user_stock)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, user_stock)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500
        
    
    @app.route('/api/update-password', methods=['POST'])
    def update_password():
        """
        Route to update a user's password.

        Expected JSON Input:
            - username (str): The username of the user.
            - old_password (str): The user's current password for authentication.
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating success or failure.

        Raises:
            400 error if input validation fails.
            401 error if authentication of the old password fails.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'old_password' not in data or 'new_password' not in data:
            app.logger.error("Invalid request payload for updating password.")
            raise BadRequest("Invalid request payload. 'username', 'old_password', and 'new_password' are required.")

        username = data['username']
        old_password = data['old_password']
        new_password = data['new_password']

        try:
            # Validate user credentials
            if not Users.check_password(username, old_password):
                app.logger.warning("Password update failed due to invalid old password for username: %s", username)
                raise Unauthorized("Invalid username or old password.")

            # Update password
            Users.update_password(username, new_password)

            app.logger.info("Password updated successfully for user: %s", username)
            return jsonify({"message": f"Password updated successfully for user: {username}"}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except ValueError as e:
            app.logger.error("Error updating password for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Unexpected error during password update for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    ##########################################################
    #
    # Stocks
    #
    ##########################################################

    #This is to first buy a stock and add to database
    @app.route('/api/stock-price', methods=['GET'])
    def view_stock() -> Response:
        """
        Fetches and returns the stock price for the given stock symbol.

        This route receives a stock symbol in the request body as JSON, validates its format, 
        and fetches the current stock price using the `get_stock_price` method. If successful, 
        it returns a success message; otherwise, it returns an error message with appropriate 
        status codes.

        Request:
            - JSON body containing the stock symbol (`symbol`).

        Returns:
            Response: 
                - If successful: A JSON response with a success message and HTTP status 201.
                - If validation or fetching fails: A JSON response with an error message and the corresponding HTTP status code (400 for invalid symbol format, 500 for server errors).

        Logs:
            Logs the process of fetching the stock price, including success or failure.
        """

        app.logger.info('Finding stock price')

        #takes input via JSON data
        #  from request
        data = request.get_json()
        symbol = data["symbol"]

        # Validate stock symbol format
        if not symbol or not symbol.isalnum():
            return jsonify({"error": "Invalid stock symbol format"}), 400

        try:
            #print out the stock symbol and its price
            price = user_stock.get_stock_price(symbol)
            ## print_stock_price(symbol, stock_price)
            return jsonify({"message": "Success"}), 201
        except Exception as e:
            return jsonify({"error": f"Error adding stock to the database: {str(e)}"}), 500
        
    @app.route('/api/add-stock', methods=['POST'])
    def add_stock() -> Response:
        """
        Adds a stock symbol to the user's portfolio.

        This route receives a stock symbol and quantity in the request body as JSON, 
        and adds the stock to the user's portfolio. If the stock is successfully added, 
        it returns a success message. If any required fields are missing or if there 
        is an error in adding the stock, an error message is returned with the appropriate status code.

        Request:
            - JSON body containing the stock symbol (`symbol`) and quantity (`quantity`).

        Returns:
            Response: 
                - If successful: A JSON response with a success message and HTTP status 201.
                - If validation fails (missing required fields): A JSON response with an error message and HTTP status 400.
                - If an error occurs while adding the stock: A JSON response with an error message and HTTP status 500.

        Logs:
            Logs the process of adding a stock to the portfolio, including any errors that occur.
        """
        """Route to add stock to the user's portfolio."""
        data = request.get_json()
        
        if not data or "symbol" not in data or "quantity" not in data:
            return jsonify({"error": "Stock symbol and quantity are required"}), 400
        
        symbol = data["symbol"]

        try:
            user_stock.add_stock(symbol)
            # Update stock quantity in the database (stub)
            
            return jsonify({"message": "Successfully added stock to portfolio"}), 201
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/api/buy-stock', methods=['PUT'])
    def buy_stock() -> Response:
        """
        Adds a specified quantity of stock to the user's portfolio.

        This route receives a stock symbol and quantity in the request body as JSON, 
        and adds the specified quantity of the stock to the user's portfolio. The route 
        validates that the quantity is a positive integer. If successful, it returns a 
        success message with the stock symbol and quantity. If any validation fails or 
        an error occurs, an appropriate error message is returned.

        Request:
            - JSON body containing the stock symbol (`symbol`) and quantity (`quantity`).

        Returns:
            Response: 
                - If successful: A JSON response with a success message and HTTP status 201.
                - If validation fails (missing required fields or invalid quantity): A JSON response 
                with an error message and HTTP status 400.
                - If an error occurs while updating the stock quantity: A JSON response with an error 
                message and HTTP status 500.

        Logs:
            Logs the process of adding stock to the portfolio, including validation and any errors that occur.
        """
        """Route to add stock to the user's portfolio."""
        data = request.get_json()
        
        if not data or "symbol" not in data or "quantity" not in data:
            return jsonify({"error": "Stock symbol and quantity are required"}), 400
        
        symbol = data["symbol"]
        quantity = data["quantity"]

        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400

        try:
            # Update stock quantity in the database (stub)
            user_stock.up_stock_quantity(symbol, quantity)
            
            return jsonify({"message": f"Successfully added {quantity} shares of {symbol}"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/delete-stock', methods=['POST'])
    def sell_stock() -> Response:
        """
        Removes a specified quantity of stock from the user's portfolio.

        This route receives a stock symbol and quantity in the request body as JSON, 
        and removes the specified quantity of the stock from the user's portfolio. 
        The route validates that the quantity is a positive integer. If successful, 
        it returns a success message with the stock symbol and quantity. If any 
        validation fails or an error occurs, an appropriate error message is returned.

        Request:
            - JSON body containing the stock symbol (`symbol`) and quantity (`quantity`).

        Returns:
            Response: 
                - If successful: A JSON response with a success message and HTTP status 200.
                - If validation fails (missing required fields or invalid quantity): A JSON response 
                with an error message and HTTP status 400.
                - If an error occurs while updating the stock quantity: A JSON response with an error 
                message and HTTP status 500.

        Logs:
            Logs the process of removing stock from the portfolio, including validation and any errors that occur.
        """
        """Route to delete (sell) stock from the user's portfolio."""
        data = request.get_json()
        
        if not data or "symbol" not in data or "quantity" not in data:
            return jsonify({"error": "Stock symbol and quantity are required"}), 400
        
        symbol = data["symbol"]
        quantity = data["quantity"]

        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400

        try:
            user_stock.dec_stock_quantity(symbol, quantity)

            return jsonify({"message": f"Successfully sold {quantity} shares of {symbol}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/view-port', methods=['GET'])
    def view_portfolio() -> Response:
        """
        Retrieves and displays the user's stock portfolio.

        This route fetches the user's current stock portfolio and returns it in a JSON format.
        If the portfolio is empty or there is an error in fetching the data, an appropriate 
        error message is returned. The portfolio is retrieved using the `get_user_stocks` method.

        Returns:
            Response: 
                - If successful: A JSON response containing the user's portfolio and HTTP status 200.
                - If no stocks are found: A JSON response with an error message and HTTP status 404.
                - If an error occurs while fetching the portfolio: A JSON response with an error message and HTTP status 500.

        Logs:
            Logs the process of fetching the user's portfolio, including any errors that occur.
        """
        """Route to view the user's stock portfolio."""
        try:
            portfolio = user_stock.get_user_stocks()

            if not portfolio:
                return jsonify({"error": "No stocks found in portfolio"}), 404
            return jsonify({"portfolio": portfolio}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500

    
    return app


    


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)