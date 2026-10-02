import os
from openai import OpenAI
from dotenv import load_dotenv
import pymupdf

# 1. 키를 메모리 적재
load_dotenv()

# text 받아서 LLM에 보내고 요약 text 반환
def summerize_txt(file_path:str)->str:
    api_key=os.getenv("OPENAI_API_KEY")
    client=OpenAI(api_key=api_key)

    # text 파일 읽기
    with open(file_path,"r",encoding="utf-8") as f:
        txt = f.read()

    # 요약을 위한 system prompt 생성
    system_prompt = f'''
    너는 다음 글을 요약하는 봇이다.
    아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고,
    주요 내용을 요약하라.

    작성해야 하는 포멧은 다음과 같다.

    # 제목
    ## 저자의 문제 인식(15문장 이내)
    ## 저자의 해결 방법(15문장 이내)
    ## 저자 소개

    ===================== 아래 글 =====================
    {txt}
    '''

    # 요약 진행
    response=client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        messages=[
            {"role":"system", "content":system_prompt}
        ]
    )
    return response.choices[0].message.content
# end summerize_txt

# PDF 파일 읽어서 본문 text만 추출
# 매개변수: 함수 실행에 필요한 재료 지정
#   - pdf_file_path (PDF 파일 저장 위치)
def pdf_to_text(pdf_file_path:str)->str:
    # 1. document 추출
    document=pymupdf.open(pdf_file_path)

    header_height=80
    footer_height=80

    full_text=""

    for page in document:
        rect=page.rect
        text=page.get_text(clip=(
            0,header_height,rect.width,rect.height-footer_height
        ))
        full_text += text + "\n-------------------------------\n"
    # 파일명 추출
    pdf_file_name=os.path.basename(pdf_file_path)
    pdf_file_name=os.path.splitext(pdf_file_name)[0]

    txt_file_path=f"chap04/output/{pdf_file_name}_01.txt"
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    return txt_file_path    # 텍스트가 저장된 파일명 반환
# end pdf_to_text

# 위 두 함수를 실행하는 함수 선언
# 순서: 1. pdf_to_text(pdf_file) 호출 -> 2. summarize_txt(text_file)
# def summarize_pdf(pdf 파일 경로, 최종 파일 경로)
def summarize_pdf(pdf_file_path:str, output_file_path: str):
    # 1. pdf -> txt : pdf_to_text(pdf_file_path)
    summary = summerize_txt(pdf_to_text(pdf_file_path)) # pdf_to_text() -> summarize_txt() 실행.

    # 2. summary 파일에 저장
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(summary)
# end summarize_pdf

if __name__ == "__main__":
    pdf_file_path = r"C:\big21\agentic_ai\chap04\data\과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf"
    summarize_pdf(pdf_file_path, "chap04/output/crop_model_summary2.txt")