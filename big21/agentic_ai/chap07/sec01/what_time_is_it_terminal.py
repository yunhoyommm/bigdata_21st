import os
from gpt_functions import get_current_time, tools
from openai import OpenAI
from dotenv import load_dotenv
import json

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


messages = [
    {"role":"system", "content":"너는 사용자를 도와주는 상담사야."},    # 초기 시스템의 역할부여
]

while True:
    user_input = input("사용자\t: ")    # 사용자 키보드 입력한 텍스트 저장 => LLM 보내기 위해

    if user_input == "exit":
        break

    # user_input = 지금 뉴욕은 몇 시니?
    messages.append({"role":"user", "content":user_input})

    # 어떤 함수를 호출할지 명시
    ai_response = get_ai_response(messages, tools=tools)
    ai_message = ai_response.choices[0].message
    print(ai_message)   # 답변뿐만 아니라, 호출할 함수, 다양한 정보 있음.

    # 지금부터
    # 1. 질문(질문, tool) => LLM => response(답변, 함수 내용(tool_calls))

    tool_calls = ai_message.tool_calls
    if tool_calls:  # if 조건자리 : Boolean(True, False), 리스트는 값이 있으면 True
        tool_name = tool_calls[0].function.name     # LLM이 실행해 달라고 선택한 함수
        tool_call_id = tool_calls[0].id

        arguments = json.loads(tool_calls[0].function.arguments)    # LLM으로 보낼 때는 dict 안 됨. json으로 바꿔줘야 함.

        if tool_name == "get_current_time":     # 함수 호출해서 결과를 다시 LLM에 보내야.
            messages.append({
                "role":"function",
                "tool_call_id":tool_call_id,    # 메시지를 LLM에 보낼 때 해당 Session 보내기 위해 사용
                "name":tool_name,
                "content":get_current_time(timezone=arguments["timezone"]),   # 함수 실행 결과를 질문으로 넣었다.
            })
        # if 여러 개일 수 있음. 현재는 get_current_time 함수 1개만 있음. 
        # LLM에 보낸다.
        ai_response = get_ai_response(messages=messages, tools=tools)   # system, user, tool 실행 결과
        ai_message = ai_response.choices[0].message     # system(너는 상담사야), user(지금 몇 시니?),tool(현재시간 함수 실행 결과),답변(현재시간)

    messages.append(ai_message)
    # 터미널에 출력.
    print(f"AI\t: {ai_message.content}")
    # end while

print("프로그램 종료")
