from datetime import date
from fastapi import FastAPI, Query
from langchain_groq import ChatGroq
import yfinance as yf
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import os 

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")


llm = ChatGroq(
    api_key=api_key,
    model="llama-3.3-70b-versatile"  
)

app = FastAPI()

class AdviceRequest(BaseModel):
    user_prompt: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

def getShareTicker(share) -> str:
    response = llm.invoke(
        [
        SystemMessage(content="You are a well inform stock market analyst. Who has the information of all the stocks in across all exchanges in the world. Your job is to return only the ticker of the stock name asked for by the user. Give only the output of the ticker name. If supposed the ticker is not found for the provided stock name then return None. If you found multiple then return the most reliable and most used one. Note that the ticker should be such that it can be directly used to fetch the data from yfinance api. Do not return any other supporting text only the ticker code. Note if for regional exchages you find codes like ABC.NS then return that too. Do not retrun the name or any other details only the ticker code used in the exchange. Return None if a wierd or non existent share name is provided.")
        ,HumanMessage(content=f"What is the ticker of {share}")
        ],
    )

    ticker = response.content
    return ticker

def getSharePrice(share) -> str:
    ticker = getShareTicker(share)
    if ticker != "None":
        price,curr = get_price(ticker)
        if price != None and curr != None:
            return str(price)+ " "+ curr
        else:
            return "Insufficient Information found for the stock"
    else:
        print("Ticker not found")

@tool
def get_price(ticker) -> tuple[float | None ,str | None]:
    """Get the price of the stock from the ticker"""
    try:
        data = yf.Ticker(ticker)
        return (data.info["regularMarketPrice"], data.info["currency"])
    except:
        return (None,None)

@tool   
def get_price_history(ticker,start_date,end_date):
    """Get the price history of the stock from the ticker"""
    data = yf.Ticker(ticker)
    hist = data.history(start=start_date, end=end_date)
    hist = hist.reset_index()
    hist[ticker] = hist['Close']
    return hist[['Date', ticker]]

def getAdvice(user_prompt : str):

    messages = [SystemMessage("""
        You are a smart stock analyst who guides people over stock market decisions. Your job is to predict what would be the best decision sell/buy/hold using the data and the tools provided. Give explaination and facts to support your decision and reason why did you make the decision
    """), HumanMessage(user_prompt)]
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    for tool_call in response.tool_calls:
        selected_tool = {"get_price": get_price, "get_price_history": get_price_history}[tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])
        messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
        final_response = llm_with_tools.invoke(messages)
        return final_response.content


@app.get("/price/{share}")
def get_share_price(share: str):
    return getSharePrice(share)

@app.post("/advice")
def get_advice(request: AdviceRequest):
    user_prompt = request.user_prompt
    start_date = request.start_date or "1900-1-1"
    end_date = request.end_date or date.today().isoformat()
    user_prompt += f"\nConsider data from {start_date} to {end_date}"  
    return {"advice":getAdvice(user_prompt)}


tools = [get_price,get_price_history]
llm_with_tools = llm.bind_tools(tools)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Change 8080 to any port you want