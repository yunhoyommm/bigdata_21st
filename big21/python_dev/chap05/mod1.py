def sum(a, b):
    return a + b

def safe_sum(a,b):
    if type(a) != type(b):
        return "더할 수 있는 값 x"
    else:
        return sum(a,b)
    
if __name__=="__main__":    # mod1.py 직접 실행했을 때
    print(safe_sum('a',1))  # 에러 발생 테스트
    print(safe_sum(1,4))    # 정상 작동 테스트
    print(safe_sum(10,10.4))
    print(sum(10,10.4))     