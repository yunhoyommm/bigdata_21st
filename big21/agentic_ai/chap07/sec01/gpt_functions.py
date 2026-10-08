from datetime import datetime

import pytz     # 파이썬에서 타임존을 다루는 lib


# 파이썬은 객체지향 언어. 모든 변수는 클래스에서 만들어진 오브젝트. 
# 파이썬의 최상위는 클래스는 object(), 이 클래스 안에 __str__() 존재
# 파이썬에 있는 모든 오브젝트는 object()를 상속. 
# 상속: 가져다 쓴다.

# def get_current_time(): # 매개변수X
# 질문 : 지금 뉴욕은 몇 시야? => LLM => get_current_time() 호출해줘. 
# 이 매개변수(timezone:뉴욕) 값을 LLM이 만들어 보내줌. => 꺼내고 함수에 넣어 실행 => LLM에 보냄.
def get_current_time(timezone:str="Asia/Seoul"): # 매개변수로 timezone : str="Asia/Seoul"
    # 타임존 설정: default = Seoul
    tz = pytz.timezone(timezone)    # timezone 설정
    # now = datetime.now()  # 2026-10-02 17:10:12.880311
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")  # 2026-10-02 17:21:40
    print(now.__str__())  # test용. 테스트 끝나면 주석 처리
    # print(문자열) : 화면 출력
    # now는 숫자. now 오브젝트 안에 __str__() 메소드가 숫자를 "연월일 시분초:microsec" 문자열로 변환
    return now

tools = [
    {
        "type":"function",
        "function": {
            "name":"get_current_time",
            "description":"현재 날짜와 시간을 반환합니다.",
            "parameters":{
                "type":"object",
                "properties":{
                    "timezone":{
                        "type":"string",
                        "description":"현재 날짜와 시간을 반환할 타임존을 입력하세요.(예: 'Asia/Seoul')",
                    },
                },
                "required":["timezone"],
            },
        }
    },
]

if __name__ == "__main__":  # 직접 실행할 때 True, import할 때는 False
    get_current_time()