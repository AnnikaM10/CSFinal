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
- `quantity` (int): The number of stock to buy.

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


## Route: `/api/sell-stock`

- **Request Type:** `POST`
- **Purpose:** Allows the user to sell stock via its input symbol and the quantity of the stock.

### Request Body:
- `symbol` (String): The symbol of the stock.
- `quantity` (int): The number of stock to buy.

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
      "message": "Successfully sold 10 shares of IBM"
    }
    ```

  
## Route: `/api/view_port`

- **Request Type:** `GET`
- **Purpose:** Allows the user to view a list of each stock and their quantity that user owns

### Request Body:
- `TBD`

### Example Request:
```json
{
  "TBD"
}
```

### Response Format:
- **Success Response Example:**
  - **Code:** `200`
  - **Content:**
    ```json
    {
      "TBD"
    }
    ```

## Route: `/api/calc_port`

- **Request Type:** `GET`
- **Purpose:** Allows the user to view the total of what all their stock is worth

### Request Body:
- `TBD`

### Example Request:
```json
{
  "TBD"
}
```

### Response Format:
- **Success Response Example:**
  - **Code:** `200`
  - **Content:**
    ```json
    {
      "TBD"
    }
    ```



