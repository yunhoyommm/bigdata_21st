# 0. import
import os

from openai import OpenAI
from dotenv import load_dotenv

# 1. loading
load_dotenv()

# 2. client
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. 질문(message)하고 답변(message) 반환하는 함수 선언.
def get_ai_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.9,
        messages=messages,  # 대화 기록
    )
    return response.choices[0].message.content  # 답변 반환

# 4. 페르소나 지정
messages=[
    {"role":"system", "content":"너는 사용자를 도와주는 상담사야."}
]

# 5. 채팅 진행
while True:
    user_input=input("사용자: ")    # 질문 여기서 입력

    if user_input == "exit":
        break

    # 위의 페르소나에 질문 추가
    messages.append({"role":"user","content":user_input})   

    # 함수 호출하여 답변 반환
    ai_response=get_ai_response(messages=messages)

    # 답변 messages에 추가해야. messages에 계속 추가하는 게 "기억" 기능
    messages.append({"role":"assistant", "content":ai_response})

    print(f"AI: {ai_response}")     # 답변 여기서 출력