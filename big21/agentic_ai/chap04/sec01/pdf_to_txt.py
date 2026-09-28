import os       # 파일 경로에서 파일명 추출
import pymupdf  # pdf 파일 읽는 라이브러리


# 1. pdf 파일 경로(위치) 저장: 절대 경로
pdf_file_path = 'C:/big21/agentic_ai/chap04/data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
# pdf_file_path = r'chap04\data\과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
# PDF 열어 Document 객체 생성
# 객체는 페이지 단위로 읽은 리스트를 가지고 있음.
doc = pymupdf.open(pdf_file_path)   # close 없음..

# 전체 텍스트 저장하는 변수 선언
full_text = ''  


# 2. doc : 문서,    문서 : [페이지,페이지,,,,]
for page in doc:    # Page 객체 생성
    text=page.get_text() # 페이지마다 텍스트 추출
    full_text += text


# print(full_text)  # 전체 텍스트 출력


# pdf_file_path 파일에서 파일명만 추출 : os.path
pdf_file_name = os.path.basename(pdf_file_path)     # 경로(path)에서 마지막 부분만 추출
# 과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf

pdf_file_name = os.path.splitext(pdf_file_name)[0]  # '.' 기준으로 나눔.
# 과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축
print(pdf_file_name)




# 3. txt 파일에 변환된 텍스트들을 저장
txt_file_path = f'chap04/output/{pdf_file_name}.txt'
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(full_text)  # 전체 텍스트를 해당 텍스트 파일에 저장.
