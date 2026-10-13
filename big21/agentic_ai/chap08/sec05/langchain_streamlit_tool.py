from dotenv import load_dotenv

import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def get_ai_response(messages):
    response = llm.stream(messages)

    for chunk in response:
        yield chunk

st.title("GPT-4o Langchain Chat")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        
    ]