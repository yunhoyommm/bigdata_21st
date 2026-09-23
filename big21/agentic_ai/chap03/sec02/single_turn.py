# 0. import
import os       # 외장 모듈이 위에 있어야 함.

from openai import OpenAI
from dotenv import load_dotenv

# 1. loading
load_dotenv()

# 2. client 생성
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. 대화 반복
while True: # 무한 반복 대화
    # 3.1. 질문 생성: 터미널에서 처리
    user_input=input("사용자: ")   # 키보드로 입력 받겠다. => 질문

    if user_input == 'exit':
        break   # while 종료 => 채팅 종료, while문 실행 x

    # 3.2. 질문 보내고 답변 받아 출력
    response=client.chat.completions.create(
        model='gpt-4o',
        temperature=0.9,
        messages=[
            {"role":"system", "content":"너는 사용자를 도와주는 상담사야."},
            {"role":"user", "content":user_input}   # exit 아니면 질문
        ]
    )
    # 3.3 답변 출력. 현재 while 문에서 출력
    print(f"AI: {response.choices[0].message.content}")
    # while end
print("프로그램(채팅) 종료")