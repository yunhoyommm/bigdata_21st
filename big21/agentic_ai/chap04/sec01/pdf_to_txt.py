import os
import pymupdf


# 1. pdf 파일 경로(위치) 저장
pdf_file_path = 'chap04/data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf'
doc = pymupdf.open(pdf_file_path)


full_text = ''


# 2. doc : 문서, 문서 : [장,장,,,,]
for page in doc:
    text=page.get_text() # 페이지마다 텍스트 추출
    full_text += text


# print(full_text)


# pdf_file_path 파일에서 파일명만 추출
pdf_file_name = os.path.basename(pdf_file_path)
pdf_file_name = os.path.splitext(pdf_file_name)[0]
print(pdf_file_name)
# 과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf


# 3. txt 파일에 변환된 텍스트들을 저장
txt_file_path = f'chap04/output/{pdf_file_name}.txt'
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(full_text)
