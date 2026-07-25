from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

model = ChatOpenAI(model = "gpt-5.4-mini")

class chatstate(TypedDict):

    messages : Annotated[list[BaseMessage] , add_messages]

def chatnode(state: chatstate):
     
    messages = state["messages"]

    result = model.invoke(messages)

    return {"messages" : result}


checkpointer = MemorySaver()

graph = StateGraph(chatstate)

graph.add_node("chatnode", chatnode)

graph.add_edge(START, "chatnode") #graph.add_node()
graph.add_edge("chatnode",END)

workflow = graph.compile(checkpointer=checkpointer)


#initialstate ={
#    "messages": [ HumanMessage(content='What is the capital of india')]
#}
#
#finalstate = workflow.invoke(initialstate)["messages"][-1].content
#print(finalstate)

threadid = '1'
if __name__ == "__main__":

    while True:
     
        userquery = input("Ask here: ")

        print ("Human Message:" , userquery)

        if userquery.strip().lower() in ["bye" , "exit" , "stop"]:
            break
       #config
        config = {'configurable':{'thread_id': threadid}}


        opstate = workflow.invoke({"messages": HumanMessage(content= userquery)} , config=config)

        print("AI message:" , opstate["messages"][-1].content)

