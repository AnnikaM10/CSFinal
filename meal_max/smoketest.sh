#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  $(curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"')
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  
  echo "$response"

  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  echo "$response"
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to update the password of a user
update_password() {
  echo "Updating user password..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "old_password":"password123", "new_password":"newpassword123"}')

  echo "$response"

  if echo "$response" | grep -q '"message": "Password updated successfully for user: testuser"'; then
    echo "Password updated successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Update Password Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to update password."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}


##############################################
#
# Stocks
#
##############################################
# Function to add a stock 
create_stock() {
  echo "Adding a stock..."
  response=$(curl -s -X POST "$BASE_URL/add-stock" -H "Content-Type: application/json" \
    -d "{\"symbol\":\"IBM\", \"quantity\":0, \"price\":0.0}")
  echo "Response: $response"

  if echo "$response" | grep -q '"message": "Successfully added stock to portfolio"'; then
    echo "Stock retrieved successfully."
  else
    echo "Failed to add stock."
    exit 1
  fi
}

get_stock() {
  echo "Getting the stock price..."
  response=$(curl -s -X GET "$BASE_URL/stock-price"  -H "Content-Type: application/json" \
    -d '{"symbol":"IBM"}')
  echo "$response"
  # Check if the response contains stocks or an empty list
  if echo "$response" | grep -q '"message": "Success"'; then
    echo "Stock retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Portfolio JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get stock or no stock found."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error or empty response:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}


buy_stock() {
  echo "Buying a stock..."
  response=$(curl -s -X PUT "$BASE_URL/buy-stock" -H "Content-Type: application/json" \
    -d '{"symbol":"IBM", "quantity":5}' | grep -q '"message": "Successfully added 5 shares of IBM"')
  

  if [ $? -eq 0 ]; then
    echo "stock bought successfully."
  else
    echo "Failed to buy stock."
    exit 1
  fi
}

sell_stock() {
  echo "Selling a stock..."
  curl -s -X POST "$BASE_URL/delete-stock" -H "Content-Type: application/json" \
    -d '{"symbol":"IBM", "quantity":5}' | grep -q '"message": "Successfully sold 5 shares of IBM"'
  if [ $? -eq 0 ]; then
    echo "stock sold successfully."
  else
    echo "Failed to sell stock."
    exit 1
  fi
}




# Function to get the current list of stocks
get_portfolio() {
  echo "Getting the current portfolio..."
  response=$(curl -s -X GET "$BASE_URL/view-port")

  # Check if the response contains stocks or an empty list
  if echo "$response" | grep -q '"portfolio"'; then
    echo "Portfolio retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Portfolio JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get portfolio or no portfolio found."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error or empty response:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}


# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}



# Run all the steps in order
check_health
init_db
create_user
login_user
update_password


create_stock
get_stock
buy_stock
sell_stock
get_portfolio



echo "All tests passed successfully!"
