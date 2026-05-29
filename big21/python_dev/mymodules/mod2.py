# 변수 선언
PI = 3.141592

# 클래스 선언
class Math:
    def solv(self,r):
        return PI * (r **2)

# 함수 선언
def sum(a,b):
    return a+b

if __name__ == "__main__":
    print(PI)
    a = Math()
    print(a.solv(2))
    print(sum(PI, 4.4))