import os
import pymupdf

# 읽을 pdf 파일 위치, 파일명 저장
# pdf_file_path = "chap04/data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf"
pdf_file_path = r"C:\big21\agentic_ai\chap04\data\과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf"

# open() => Document object 생성 => 그 안에 리스트 있음. Page object 담고 있는 리스트
# 마지막 줄에 document.close() 해줘야 함.
document = pymupdf.open(pdf_file_path)

full_text=""
# header와 footer 크기 지정하는 변수 선언
header_height=80
footer_height=80

# 페이지 읽고 클립 처리 후 해당 추출
for page in document:   # 페이지 하나씩 꺼내서 page 변수에 전달하고 반복
    # 페이지의 전체 크기를 가지고 있는 rect 변수 => Rect object 추출
    # 페이지 전체 크기를 사각형(x0,y0,x1,y1)으로 Rect object 추출
    # rect.width, rect.height를 사용할 수도 있다.
    rect=page.rect  # 페이지 전체 크기 사각형(x0,y0,x1,y1)

    # 헤더 영역 텍스트 추출
    # clip: 이 사각형 안의 글자만 뽑아라
    header = page.get_text(clip=(0,0,rect.width, header_height))
    # print(header) 해당 페이지 안의 header 텍스트 출력
    footer = page.get_text(clip=(0, rect.height - footer_height, rect.width, rect.height))
    # print(footer) 해당 페이지 안의 footer text 출력

    # 본문 영역 텍스트 추출
    text=page.get_text(clip=(
        0,  # x0
        header_height,  # y0
        rect.width,     # x1
        rect.height-footer_height   # y1
    ))

    # 본문을 누적하고, 페이지마다 구분선을 넣는다. 나중에 페이지 경계를 알아보기 쉽게 하려고 한다.(청킹과 연결)
    full_text += text + "\n-------------------------\n"
# for end: 본문 추출 완료

# 파일명 추출
pdf_file_name=os.path.basename(pdf_file_path)       # 파일명, 확장자 추출
pdf_file_name=os.path.splitext(pdf_file_name)[0]    # 파일명만 추출

# 저장할 파일명 지정
txt_file_path=f"chap04/output/{pdf_file_name}_with_preprocessing.txt"

with open(txt_file_path, "w", encoding="utf-8") as f:
    f.write(full_text)