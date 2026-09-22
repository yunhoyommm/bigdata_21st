from openai import OpenAI
from dotenv import  load_dotenv
import os

# .env 파일을 읽어서 메모리(운영체제 관리)에 올려놓음(적재).
load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")

# client 생성: 질문할 곳 생성
client=OpenAI(api_key=api_key)

# 질문하고 답변 받는다
# 1. temperature: 답변의 창의성 조절
#   0.1: 사실적으로 답변 => 코딩할 때.
#   0.8 ~ : 창의적 작업을 할 때 => 소설, 영화, 아이디어 생성 등.
# 2. message: 대화 내용을 담은 리스트, {role, content}
# 2-1. role: system, user, assistant
#   - system: 페르소나(성격)나 행동 지침을 설정
#   - user: 사용자가 입력하는 질문이나 명령 설정
#   - assistant: llm이 과거에 했던 답변
response=client.chat.completions.create(
    model='gpt-4o',     # OpenAI에서 답변할 모델 지정.
    temperature=0.1,    # 답변 생성할 때 무작위성을 조정할 때 사용. 0에 가까울 때 안정. 1에 가까울 때 창의적(불안정...)
    messages=[
        {"role":"system", "content":"You are a helpful assistant"},
        {"role":"user", "content":"2022년 월드컵 우승 팀 어디야?"}
    ]
)
print(response)     # 전체 출력.
print("=======================")
print(response.choices[0].message.content)  # 메시지만 출력.
# response.choices[0].message.content
# response: 전체 응답 객체
# choises[0]: 응답 후보들 리스트 중 0번째 
# message: 응답 메시지 객체
# content: 메시지 안의 실제 응답