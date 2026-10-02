from datetime import datetime

# 파이썬은 객체지향 언어. 모든 변수는 클래스에서 만들어진 오브젝트. 
# 파이썬의 최상위는 클래스는 object(), 이 클래스 안에 __str__() 존재
# 파이썬에 있는 모든 오브젝트는 object()를 상속. 
# 상속: 가져다 쓴다.

def get_current_time(): # 매개변수X
    # now = datetime.now()  # 2026-10-02 17:10:12.880311
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 2026-10-02 17:21:40
    print(now.__str__())  # test용. 테스트 끝나면 주석 처리
    # print(문자열) : 화면 출력
    # now는 숫자. now 오브젝트 안에 __str__() 메소드가 숫자를 "연월일 시분초:microsec" 문자열로 변환
    return now

if __name__ == "__main__":  # 직접 실행할 때 True, import할 때는 False
    get_current_time()