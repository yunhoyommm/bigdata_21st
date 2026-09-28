import os   # 환경변수 읽는 데 사용(getenv()). env 파일 처리

# LLM: OpenAI => chat
from openai import OpenAI
# env 파일 내용을 메모리 적재하는 함수 임포트
from dotenv import load_dotenv

# 메모리 적재
# .env 찾을 때까지 현재 폴더부터 위쪽으로 계속 읽는다.(sec02->chap04->agentic_ai)
# .env 여러 개일 수 있음.(필요에 따라 다른 env 사용.)
load_dotenv()

# api_key
api_key=os.getenv("OPENAI_API_KEY")

# 요약하는 함수 만들기
# 텍스트 파일을 받아 llm에 보내고, 요약을 답변으로 받아 반환하는 함수
# 매개변수 : text 파일
# return : 답변(text)
def summary_txt(file_path: str) -> str:    # 'file_path: str': 타입힌트. 없어도 에러는 안 남. 
                                           # '-> str': 반환(return)하는 데이터에 대한 힌트
    # 1. client 생성: 질문하고 답변을 받을 변수
    client=OpenAI(api_key=api_key)

    # 2. 파일 읽어서 LLM에 보내고 요약을 받는다.
    with open(file_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 요약을 위한 시스템 프롬프트(페르소나)를 생성
    # ''': 여러 줄 문자열 생성할 때 사용
    # txt: pdf에서 추출한 텍스트
    system_prompt = f'''
    너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 
    저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라.

    작성해야 하는 포멧은 다음과 같다.

    # 제목
    ## 저자의 문제 인식(15문장 이내)
    ## 저자의 해결 방법(15문장 이내)
    ## 저자 소개

    =============== 이하 텍스트 ===============

    {txt}
    '''

    # 3. LLM에 질문 보내고 답변 받기
    response = client.chat.completions.create(
        model="gpt-6-astra",
        # temperature=0.1,
        messages=[
            {"role":"system", "content":system_prompt}
        ]
    )

    return response.choices[0].message.content  # 답변 반환

# 4. 실행 -> 파일 경로 설정ㅇ
file_path=r"C:\big21\agentic_ai\chap04\output\과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축_with_preprocessing.txt"

# 5. 함수 호출 -> 요약 출력
summary = summary_txt(file_path)
print(summary)
