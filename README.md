# CSFinal

Purpose of Application:
-   Provide user verification through secured salted hash passwords.
-   Allow users to view, buy, and sell their stocks.
-   Allow users to view their stock portfolio
-   Calculate a user's portfolio value upon their request

## API Documentation

## Route: `/api/stock_price`

- **Request Type:** `GET`
- **Purpose:** Allows the user to view the stock value of a given stock via its symbol.

### Request Body:
- `symbol` (String): The symbol of the stock.

### Example Request:
```json
{
  "symbol": "IBM"
}
```

### Response Format:
- **Success Response Example:**
  - **Code:** `200`
  - **Content:**
    ```json
    {
      "message": "Stock IBM is at $234 today"
    }
    ```

## Route: `/api/add-stock`

- **Request Type:** `POST`
- **Purpose:** Allows the user to buy a stock via its input symbol and the quantity of the stock.

### Request Body:
- `symbol` (String): The symbol of the stock.

### Example Request:
```json
{
  "symbol": "IBM"
  "quantity": 10
}
```

### Response Format:
- **Success Response Example:**
  - **Code:** `200`
  - **Content:**
    ```json
    {
      "message": "Successfully added 10 shares of IBM"
    }
    ```


## Route: `/api/delete-stock`
## Route: `/api/view_port`
## Route: `/api/calc_port`



