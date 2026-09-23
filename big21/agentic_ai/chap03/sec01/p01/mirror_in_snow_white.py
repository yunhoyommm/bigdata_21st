# 백설공주에 나오는 마법 거울 페르소나 부여 챗

import os                   # 운영체제 관련 모듈
from openai import OpenAI   # OpenAI 회사 서버에 연결 처리하는 API
from dotenv import load_dotenv  # .env 파일을 읽어서 메모리에 적재

# api_key memory loading
load_dotenv()

# 2. OpenAI 오브젝트 생성 => 메소드 사용 가능, 키 필요
# api_key = os.getenv("OPENAI_API_KEY")
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. 채팅 가능
# 3.1. 너는 백설공주 이야기 속의 마법 거울이야. 그 이야기의 캐릭터에 부합하게 답변해줘.
# 질문(request) => server(LLM): 답변 생성 => server(LLM) 반환(response) => 받는 곳.
response=client.chat.completions.create(
    model="gpt-4o",     # 답변 생성할 LLM 선택
    temperature=0.9,    # 창조적 답변 가능
    messages=[
        {"role":"system", "content":"너는 배트맨에 나오는 조커야. 조커의 악당 캐릭터에 맞게 답변해 줘."},
        {"role":"user", "content":"세상에서 누가 제일 아름답니?"}
    ]
)

# 4. 답변 출력
print(response.choices[0].message.content)