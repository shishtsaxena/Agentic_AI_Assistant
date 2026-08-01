from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool 
import requests
import os


load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
model = ChatOpenAI(model = "gpt-4o-mini")

search_tool = DuckDuckGoSearchRun()

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool 
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha Vantage.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"

    response = requests.get(url)
    return response.json()

tools = [search_tool, get_stock_price, calculator]
llm_with_tools = model.bind_tools(tools)



class chatstate(TypedDict):

    messages : Annotated[list[BaseMessage] , add_messages]

def chatnode(state: chatstate):
     
    
    messages = state["messages"]
    result = llm_with_tools.invoke(messages)
   
    return {"messages" : result}

toolnode = ToolNode(tools)

conn = sqlite3.connect (database = "chatbot2.db", check_same_thread=False)

#cursor = conn.cursor()
#cursor.execute("DELETE FROM checkpoints")
#conn.commit()

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(chatstate)

graph.add_node("chatnode", chatnode)
graph.add_node("tools", toolnode)

graph.add_edge(START, "chatnode") 
graph.add_conditional_edges("chatnode",tools_condition)  #either toolnode or end
graph.add_edge("tools","chatnode")


workflow = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

