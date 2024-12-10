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

##############################################
#
# Meals
#
##############################################

get_stock() {
  echo "Getting the stock..."
  response=$(curl -s -X GET "$BASE_URL/stock-price?symbol=IBM")
  echo "$response"
  # Check if the response contains combatants or an empty list
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


# Function to add a meal (combatant)
create_stock() {
  echo "Adding a stock..."
  response=$(curl -s -X POST "$BASE_URL/add-stock" -H "Content-Type: application/json" \
    -d '{"symbol":"IBM", "quantity":0, "price":0.0}' | grep -q '"message": "Successfully added IBM to stock portfolio"')
  
  echo "$response"
  if [ $? -eq 0 ]; then
    echo "stock added successfully."
  else
    echo "Failed to add stock."
    exit 1
  fi
}

buy_stock() {
  echo "Buying a stock..."
  response=$(curl -s -X PUT "$BASE_URL/buy-stock" -H "Content-Type: application/json" \
    -d '{"symbol":"IBM", "quantity":"5"}' | grep -q '"message": "Successfully added 5 shares of IBM"')
  
  echo "$response"
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
    -d '{"symbol":"IBM", "quantity":"5"}' | grep -q '"message": "Successfully sold 5 shares of IBM"'
  if [ $? -eq 0 ]; then
    echo "stock sold successfully."
  else
    echo "Failed to sell stock."
    exit 1
  fi
}


# # Function to delete a meal by ID (1)
# sell_stock() {
#   echo "Selling stock..."
#   response=$(curl -s -X PUT "$BASE_URL/delete-meal/1")
#   if echo "$response" | grep -q '"message": "meal deleted"'; then
#     echo "Meal deleted successfully by ID (1)."
#   else
#     echo "Failed to delete meal by ID (1)."
#     exit 1
#   fi
# }

# # Function to get a meal by ID (1)
# get_meal_by_id() {
#   echo "Getting meal by ID (1)..."
#   response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/1")
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Meal retrieved successfully by ID (1)."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Meal JSON (ID 1):"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Failed to get meal by ID (1)."
#     exit 1
#   fi
# }

# # Function to get a meal by name
# get_meal_by_name() {
#   echo "Getting meal by name (Spaghetti)..."
#   response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/Spaghetti")
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Meal retrieved successfully by name (Spaghetti)."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Meal JSON (Spaghetti):"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Failed to get meal by name (Spaghetti)."
#     exit 1
#   fi
# }

############################################
#
# Battle
#
############################################

# Function to clear the combatants
# clear_combatants() {
#   echo "Clearing combatants..."
#   curl -s -X POST "$BASE_URL/clear-combatants" -H "Content-Type: application/json" | grep -q '"status": "combatants cleared"'
#   if [ $? -eq 0 ]; then
#     echo "Combatants cleared successfully."
#   else
#     echo "Failed to clear combatants."
#     exit 1
#   fi
# }

# Function to get the current list of combatants
get_portfolio() {
  echo "Getting the current portfolio..."
  response=$(curl -s -X GET "$BASE_URL/view-port")

  # Check if the response contains combatants or an empty list
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

# # Function to prepare a combatant for battle
# prep_combatant() {
#   echo "Preparing combatant for battle..."
#   curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
#     -d '{"meal":"Spaghetti"}' | grep -q '"status": "combatant prepared"'
#   if [ $? -eq 0 ]; then
#     echo "Combatant prepared successfully."
#   else
#     echo "Failed to prepare combatant."
#     exit 1
#   fi
# }

# # Function to run a battle
# run_battle() {
#   echo "Running a battle..."
#   curl -s -X GET "$BASE_URL/battle" | grep -q '"status": "battle complete"'
#   if [ $? -eq 0 ]; then
#     echo "Battle completed successfully."
#   else
#     echo "Failed to complete battle."
#     exit 1
#   fi
# }

######################################################
#
# Leaderboard
#
######################################################

# # Function to get the leaderboard sorted by wins
# get_leaderboard_wins() {
#   echo "Getting leaderboard sorted by wins..."
#   response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Leaderboard by wins retrieved successfully."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Leaderboard JSON (sorted by wins):"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Failed to get leaderboard by wins."
#     exit 1
#   fi
# }

# Function to get the leaderboard sorted by win percentage
# get_leaderboard_win_pct() {
#   echo "Getting leaderboard sorted by win percentage..."
#   response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=win_pct")
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Leaderboard by win percentage retrieved successfully."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Leaderboard JSON (sorted by win percentage):"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Failed to get leaderboard by win percentage."
#     exit 1
#   fi
# }

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
# create_user
# login_user
# logout_user

get_stock
create_stock
buy_stock
sell_stock
get_portfolio

# prep_combatant
# prep_combatant
# get_combatants
# run_battle
# prep_combatant
# run_battle
# prep_combatant
# run_battle
# get_leaderboard_wins
# get_leaderboard_win_pct
# logout_user
# get_meal_by_name
# get_meal_by_id
# delete_meal_by_id

echo "All tests passed successfully!"