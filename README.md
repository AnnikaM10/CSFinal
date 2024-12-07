# CSFinal

Purpose of Application:
-   Provide user verification through secured salted hash passwords.
-   Allow users to view, buy, and sell their stocks.
-   Allow users to view their stock portfolio
-   Calculate a user's portfolio value upon their request


Route: /stock_price
● Request Type: GET
● Purpose: Allows user to view the stock value of a given stock via its symbol
● Request Body:
○ symbol (String): the symbol of the stock.
● Response Format: JSON
○ Success Response Example:
■ Code: 200
■ Content: { "message": f"Stock {symbol} is at ${stock_price} today" }
● Example Request:
{
"symbol" = "IBM"
}
● Example Response:
{
"message": "Stock IBM is at 234 today",
"status": "200"
}

