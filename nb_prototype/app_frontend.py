import streamlit as st
from app_langgraph import stream_graph_updates
from threading import Thread
from queue import Queue, Empty
import time

# Assuming your existing chatbot and stream_graph_updates functions are imported and accessible:
# from your_existing_module import stream_graph_updates

st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

def enqueue_responses(user_input, queue):
    buffer = []
    def fake_print(*args):
        buffer.append(args[0])
    # Redefine print temporarily to capture stream_graph_updates prints
    import builtins
    original_print = builtins.print
    builtins.print = fake_print
    try:
        stream_graph_updates(user_input)
    finally:
        builtins.print = original_print
    # send all captured lines back to queue
    for msg in buffer:
        queue.put(msg)

def get_responses_stream(user_input):
    q = Queue()
    thread = Thread(target=enqueue_responses, args=(user_input, q))
    thread.start()
    collected = ""
    while thread.is_alive() or not q.empty():
        try:
            msg = q.get(timeout=0.1)
            collected += msg + "\n"
            yield collected
        except Empty:
            time.sleep(0.1)
    yield collected

# Input box
user_input = st.chat_input("Type your message")

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream assistant response from your backend function output
    response_container = st.empty()

    response_text = ""
    for partial_response in get_responses_stream(user_input):
        response_text = partial_response
        response_container.markdown(response_text.replace("\n", "  \n"))

    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Render past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
