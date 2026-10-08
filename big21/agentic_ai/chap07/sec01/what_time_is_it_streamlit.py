import os
import json
import streamlit as st
from gpt_functions import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client=OpenAI(api_key=api_key)

def get_ai_response(messages, tools=None):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    return response

st.title("Chatbot")

# 처음 화면 실행 시
if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"system","content":"너는 사용자를 도와주는 상담사야."},
    ]

# 대화 내용을 화면에 출력
# {"role":"user","content":"지금 몇 시니?"}
# {"role":"assistant","content":"서울시"}
for message in st.session_state["messages"]:
    if message["role"]=="assistant" or message["role"]=="user":
        st.chat_message(message["role"]).write(message["content"])

if user_input := st.chat_input():   # 사용자 입력(질문) 받기, := 대입하고 비교까지 진행
    st.session_state["messages"].append({   # 런던, 파리, 베를린 몇 시니?
        "role":"user", "content":user_input     # 질문 메시지에 추가
    })
    st.chat_message("user").write(user_input)

    ai_response = get_ai_response(messages=st.session_state["messages"], tools=tools)
    # message만 추출, 대입 => content: 답변, tool_calls=[]
    ai_message = ai_response.choices[0].message     # content, tool_calls

    print(ai_message)   # 중간 결과 확인에 필요, 개발 완료 시 삭제해야.
    # tool_calls
    tool_calls = ai_message.tool_calls  # [런던, 파리, 베를린] 함수 호출

    if tool_calls:  # True 인 경우: 함수 호출이 있는 경우.
        # 함수 호출을 횟수만큼 반복해서 실행하고, 실행 결과를 messages에 추가.
        st.session_state["messages"].append(ai_message)
        for tool_call in tool_calls:
            # 함수명 추출
            tool_name = tool_call.function.name # get_current_time
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments) # 문자열을 dict(json)으로 바꿔주는 코드

            if tool_name=="get_current_time":
                st.session_state["messages"].append({
                    "role":"tool",  # "role":"function"은 예전 방식
                    "tool_call_id":tool_call_id,
                    "name":tool_name,
                    "content":get_current_time(timezone=arguments["timezone"]),
                })
        st.session_state["messages"].append({
            "role":"system",
            "content":"이제 주어진 결과를 바탕으로 답변할 차례다."
        })
        # response
        ai_response = get_ai_response(messages=st.session_state["messages"], tools=tools)
        ai_message = ai_response.choices[0].message

    # 최종 답변 저장
    st.session_state["messages"].append({
        "role":"assistant",
        "content": ai_message.content   # 답변
    })

    # 브라우저에 답변 출력
    st.chat_message("assistant").write(ai_message.content)
# end if user_input := st.chat