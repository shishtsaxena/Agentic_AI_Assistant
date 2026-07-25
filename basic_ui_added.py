import streamlit as st
from langchain_core.messages import HumanMessage
from chatbotinsides import workflow



# messagehistory = []

if "messagehistory" not in st.session_state:
    st.session_state["messagehistory"] =[]


for message in st.session_state['messagehistory']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

userinput = st.chat_input("Type here: ")

if userinput:

    st.session_state["messagehistory"].append({"role":"user",  "content":userinput})
    with st.chat_message('user'):
        st.text(userinput)

    config = {"configurable":{"thread_id":"1"}}

    outputstate = workflow.invoke({"messages": HumanMessage(content= userinput)} , config=config)
    aimessage = outputstate["messages"][-1].content

    st.session_state["messagehistory"].append({"role":"assistant",  "content":aimessage})
    with st.chat_message("assistant"):
        st.text(aimessage)