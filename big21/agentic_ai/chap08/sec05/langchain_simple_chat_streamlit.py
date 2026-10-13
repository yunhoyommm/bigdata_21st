import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = InMemoryChatMessageHistory()
    return st.session_state["store"][session_id]

st.title('ChatBot')

if 'messages' not in st.session_state:
    st.session_state["messages"]=[
        SystemMessage(content="너는 사용자의 질문에 친절히 답하는 AI 챗봇이다.")
    ]

if "store" not in st.session_state:
    st.session_state["store"] = {}

llm = ChatOpenAI(model="gpt-4o-mini")
with_message_history = RunnableWithMessageHistory(llm, get_session_history=get_session_history)

config = {"configurable":{"session_id":"abc2"}}

for msg in st.session_state.messages:
    if msg:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)

if prompt := st.chat_input():
    print("user:", prompt)
    st.session_state.messages.append(HumanMessage(prompt))
    st.chat_message("user").write(prompt)


    response = with_message_history.invoke([HumanMessage(prompt)], config=config)

    ai_response_bucket = None
    with st.chat_message("assistant").empty():
        if ai_response_bucket is None:
            ai_response_bucket = response
        else:
            ai_response_bucket += response
        print(response.content, end="")
        st.markdown(ai_response_bucket.content)
                
    msg = ai_response_bucket.content
    st.session_state.messages.append(ai_response_bucket)
    print("assistant:", msg)
