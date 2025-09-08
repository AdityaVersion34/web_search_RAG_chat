import streamlit as st
from app_langgraph import stream_graph_updates  # Adjust filename as needed
import io
import contextlib

st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Capture printed output from backend
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        stream_graph_updates(user_input)
    assistant_reply = buf.getvalue().strip()

    # If multiline, optionally only keep the last line if that is your convention
    # assistant_reply = assistant_reply.splitlines()[-1]  # Optional

    # Display assistant message
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
