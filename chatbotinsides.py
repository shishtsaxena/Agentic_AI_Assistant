from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3



load_dotenv()

model = ChatOpenAI(model = "gpt-5.4-mini")

class chatstate(TypedDict):

    messages : Annotated[list[BaseMessage] , add_messages]

def chatnode(state: chatstate):
     
    messages = state["messages"]

    result = model.invoke(messages)

    return {"messages" : result}

conn = sqlite3.connect (database = "chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(chatstate)

graph.add_node("chatnode", chatnode)

graph.add_edge(START, "chatnode") #graph.add_node()
graph.add_edge("chatnode",END)

workflow = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)







