import streamlit as st
from langchain_core.messages import HumanMessage
from chatbotinsides import workflow , retrieve_all_threads
import uuid
#*********************************utility function*******************************************
def genreate_thread_id():
    thread_id = uuid.uuid4()    # dynamic thread id
    return thread_id

def reset_chat():
    thread_id = genreate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state['messagehistory'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id) 

def load_convo(thread_id):
    return workflow.get_state(config= {'configurable':{'thread_id': thread_id}}).values.get("messages", [])


#*********************************session setup*******************************************
# messagehistory = []

if "messagehistory" not in st.session_state:
    st.session_state["messagehistory"] =[]

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = genreate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = [retrieve_all_threads] 

add_thread(st.session_state["thread_id"])


#*********************************sidebar ui**********************************************

st.sidebar.title("Langraph Chatbot") 

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversation")

for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id   #thread id ko session me store krna pdega
        messages = load_convo(thread_id)

        temp_messages = []

        for message in messages :                    #format chnge krre hai bss list se dict me lare hai bss
            if isinstance(message, HumanMessage):
                role ="user"
            else:    
                role = "assistant"
            temp_messages.append({"role" : role , "content" : message.content})

        st.session_state["messagehistory"] = temp_messages


#**********************************main ui*************************************************
for message in st.session_state['messagehistory']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

userinput = st.chat_input("Type here: ")

if userinput:

    st.session_state["messagehistory"].append({"role":"user",  "content":userinput})
    with st.chat_message('user'):
        st.text(userinput)

    config = {"configurable":{"thread_id":st.session_state["thread_id"]}}

    with st.chat_message("assistant"):

        aimessage = st.write_stream(
            message_chunk.content for message_chunk ,metadata in workflow.stream(
                {"messages": HumanMessage(content= userinput)} ,
                  config=config,
                  stream_mode= "messages"
            )
        )

    st.session_state["messagehistory"].append({"role":"assistant",  "content":aimessage})