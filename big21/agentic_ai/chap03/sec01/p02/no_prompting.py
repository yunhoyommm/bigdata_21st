import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 키 적재
load_dotenv()

# 2. client 생성
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. no shot
response=client.chat.completions.create(
    model='gpt-4o',
    temperature=0.9,
    messages=[
        {"role":"system", "content":"너는 유치원생이야. 유치원생처럼 답변해 줘."},
        {"role":"user","content":"참새"},    # role: user = 질문.
        {"role":"assistant","content":"짹짹"},
        {"role":"user","content":"말"},
        {"role":"assistant","content":"히이잉"},
        {"role":"user","content":"개구리"},
        {"role":"assistant","content":"개굴개굴"},
        {"role":"user", "content":"병아리"}
    ]
)

# 4. 답변 출력
print(response.choices[0].message.content)