# Stockify: Market Analysis API
This API provides stock market analysis and advice using FastAPI, LangChain, and Groq's LLM.
This API is also deployed at:

## Features:

### Get Stock Price: 
Retrieve the current price of a stock.

### Get Investment Advice: 
Receive personalized investment advice based on stock data and user prompts.

## Endpoints
> GET /price/{share}  

Get the current price of a specified stock.

Parameters:
- share (path parameter): The name or symbol of the stock.

Example:
> GET /price/AAPL

Response:
>"150.25 USD"

> POST /advice  

Get personalized investment advice.

Request Body:

```
{
  "user_prompt": "Should I invest in Tesla?",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```

Parameters:

- user_prompt (required): The user's question or request for advice.

- start_date (optional): The start date for historical data analysis (default: "1900-1-1").

- end_date (optional): The end date for historical data analysis (default: current date).

Response:

```
{
  "advice": "Based on the analysis of Tesla's stock performance..."
}
```

## Setup
1) Clone the repository:  

    `git clone https://github.com/kunalvirwal/Stockify_API.git`  

2) Install dependencies:

    `pip install -r requirements.txt`  

3) Create a .env file in the project root and add your Groq API key:  

    `GROQ_API_KEY=your_api_key_here`

4) Run `python main.py` and access port 8080
