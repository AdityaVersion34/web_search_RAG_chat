import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import logging

# This disables all logging messages at WARNING level and below (only critical errors will show, which is rare)
logging.basicConfig(level=logging.CRITICAL)


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

from langchain.agents import Tool
from typing import Annotated
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver

# Setup API keys and tools
# openai_api_key = os.environ["OPENAI_API_KEY"]
# cse_key = os.environ["GOOGLE_CSE_KEY"]
# cse_id = os.environ["GOOGLE_CSE_ID"]

openai_api_key = st.secrets["OPENAI_API_KEY"]
cse_key = st.secrets["GOOGLE_CSE_KEY"]
cse_id = st.secrets["GOOGLE_CSE_ID"]

def web_search_and_ingest(query):
    cse_url = 'https://www.googleapis.com/customsearch/v1'
    cse_params = {'q': query, 'key': cse_key, 'cx': cse_id}
    response = requests.get(cse_url, cse_params)
    cse_results = response.json()
    results = []
    if 'items' in cse_results:
        for result in cse_results['items']:
            results.append(result['link'])
            if len(results) >= 5:
                break
    # print("Search results:", results)
    return "\n".join(results)

web_search_tool = Tool(
    name="WebSearch",
    func=web_search_and_ingest,
    description="Use when current context is insufficient or up-to-date info is required."
)

tools = [web_search_tool]
# print(web_search_tool.invoke("What is runescape?"))

# Setup Chatbot Logic
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = init_chat_model("openai:gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

memory = InMemorySaver()

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config={"thread_id": 1}):
        for value in event.values():
            print("", value["messages"][-1].content)    # previously prepended "Assistant: "

def main():
    print("Chatbot is running. Type 'quit' or 'exit' to end.")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except EOFError:
            break

if __name__ == "__main__":
    main()
