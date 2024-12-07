# CSFinal

Purpose of Application:
-   Provide user verification through secured salted hash passwords.
-   Allow users to view, buy, and sell their stocks.
-   Allow users to view their stock portfolio
-   Calculate a user's portfolio value upon their request

## API Documentation

### Request Type: GET
**Purpose**: Allows user to view the stock value of a given stock via its symbol

### Request Body
- **symbol** (String): the symbol of the stock.

### Response Format: JSON
#### Success Response Example
- **Code**: 200  
- **Content**:  
  ```json
  {
    "message": "message": f"Stock {symbol} is at ${stock_price} today"
  }

### Example Request
  ```json
  {
    "symbol" = "IBM"
  }
  ```
### Example Response
  ```json
  {
    "message": "Stock IBM is at 234 today",
    "status": "200"
  }
  ```

