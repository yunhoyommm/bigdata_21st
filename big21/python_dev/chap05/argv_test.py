import sys

print(sys.argv)     # argument value  리스트로 저장
                    # ['chap05\\argv_test.py'] 현재 실행한 파일 출력

print(sys.argv[1])  # python .\chap05\argv_test.py aaa bbb ccc
print(sys.argv[2])  # ['.\\chap05\\argv_test.py', 'aaa', 'bbb', 'ccc'] \n aaa\n bbb \nccc
print(sys.argv[3])  # aaa bbb ccc는 argv_test.py 실행에 필요한 값이 됨.