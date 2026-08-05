import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from ragbackend import workflow, ingest_pdf,retrieve_all_threads,thread_document_metadata
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
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_thread(st.session_state["thread_id"])

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["chat_threads"][::-1]
selected_thread = None



# ============================ Sidebar ============================

st.sidebar.title("LangGraph PDF Chatbot")
st.sidebar.markdown(f"**Thread ID:** `{thread_key}`")

# New Chat
if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()

# Upload PDF
uploaded_pdf = st.sidebar.file_uploader(
    "Upload a PDF for this chat",
    type=["pdf"]
)

if uploaded_pdf:
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(
            f"`{uploaded_pdf.name}` already processed for this chat."
        )
    else:
        with st.sidebar.status("Indexing PDF...", expanded=True) as status_box:

            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )

            thread_docs[uploaded_pdf.name] = summary

            status_box.update(
                label="✅ PDF indexed",
                state="complete",
                expanded=False,
            )

# ===================== Past Conversations ======================

st.sidebar.subheader("Past Conversations")

if not threads:
    st.sidebar.write("No past conversations yet.")

else:
    for thread_id in threads:

        if st.sidebar.button(
            str(thread_id),
            key=f"side-thread-{thread_id}"
        ):

            # Current thread change
            st.session_state["thread_id"] = thread_id

            # Load conversation
            messages = load_convo(thread_id)

            # Convert LangChain Messages → Dictionary
            temp_messages = []

            for message in messages:

                if isinstance(message, HumanMessage):
                    role = "user"
                else:
                    role = "assistant"

                temp_messages.append(
                    {
                        "role": role,
                        "content": message.content,
                    }
                )

            # Store in Session State
            st.session_state["messagehistory"] = temp_messages

            # Create document entry if not present
            st.session_state["ingested_docs"].setdefault(
                str(thread_id),
                {}
            )

            # Refresh UI
            st.rerun()

#**********************************main ui*************************************************
for message in st.session_state['messagehistory']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

userinput = st.chat_input("Type here: ")

if userinput:

    st.session_state["messagehistory"].append({"role":"user",  "content":userinput})
    with st.chat_message('user'):
        st.text(userinput)
        

    config = {"configurable":{"thread_id":st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    with st.chat_message("assistant"):
# this part is change inly just beacuse toolmessage is also there so we intruct
# heree only show aimessage
        def aionlystream():
            for message_chunk ,metadata in workflow.stream(
                {"messages": HumanMessage(content= userinput)} ,
                  config=config,
                  stream_mode= "messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        aimessage = st.write_stream(aionlystream())            
        

    st.session_state["messagehistory"].append({"role":"assistant",  "content":aimessage})

