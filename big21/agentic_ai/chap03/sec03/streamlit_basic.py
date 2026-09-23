# 0. import
import os

from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# key loading
load_dotenv()

# 키 추출, 저장
api_key=os.getenv("OPENAI_API_KEY")

# Streamlit setup
# 1. title
st.title('ChatBot')
# 2. 초기일 때(브라우저에 화면 처음 표시될 때): st.session_state(딕셔너리, 기억기능) 비어 있음.
# messages 생성하고 초기화
# session: http - 비연결 기능. 한 번 요청하고 응답하면 연결 끊어짐. 연결 유지가 안 됨.
#          session - 서버 쪽에 연결 유지를 위한 저장소
if 'message' not in st.session_state:   # True가 된다는 것은 "처음일 때"를 의미.
    # 원샷
    st.session_state["message"]=[{"role":"assistant","content":"How can I help you"}]

# 3. 대화(질문/답변) 기록 출력
for msg in st.session_state["message"]:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. 사용자 입력을 받아 기록에 추가하고 LLM에 보내고 응답 생성
# 질문: prompt
if prompt := st.chat_input():   # 사용자가 질문을 정상 입력했으면 True
    # 4.1. client 생성
    client=OpenAI(api_key=api_key)
    # 4.2. session에 질문 저장
    st.session_state["message"].append({"role":"user","content":prompt})
    # 4.3. 화면에 질문을 출력
    st.chat_message("user").write(prompt)
    # 4.4. LLM에 messages 보내고 답변 받는다.
    response=client.chat.completions.create(
        model='gpt-4o',
        messages=st.session_state["message"]
    )
    # 4.5. 답변 추출, 저장
    msg=response.choices[0].message.content
    # 4.6. 답변을 session에 저장
    st.session_state["message"].append({"role":"assistant","content":msg})
    # 웹 브라우저 화면에 답변 출력
    st.chat_message("assistant").write(msg)