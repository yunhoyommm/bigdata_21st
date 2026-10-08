import os
import json
import streamlit as st
from gpt_functions import get_current_time, get_yf_stock_info
from gpt_functions import get_yf_stock_history, get_yf_stock_recommendations, tools
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# 1. api_key memory에 적재
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. 아래 코드에서 사용할 정해진 값들 저장.
MODEL="gpt-4o"
MAX_ROUNDS=5    # 1개 질문당 함수 호출 라운드 최대 횟수
MAX_TURNS=10    # gpt에 보낼 최근 대화(질문) 수

# 3. 함수 이름 -> 실제 파이썬 함수 연결
# 변수명이 대문자면 상수처럼 처리
# 함수를 여기에 추가
FUNCTIONS={
    "get_current_time":get_current_time,    # get_current_time: 함수객체, 실행가능
    "get_yf_stock_info":get_yf_stock_info,
    "get_yf_stock_history":get_yf_stock_history,
    "get_yf_stock_recommendations":get_yf_stock_recommendations,
}

# streamlit 실행에 필요한 함수
# 1. get_client : OpenAI 오브젝트 반환 => 질문/답변 처리
@st.cache_resource  # 한 개 object만 생성돼서 재사용
def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. response 처리하는 함수: 질문/답변 처리
def get_ai_response(messages, tools=None, tool_choice=None):
    # kw:키워드(dict) args(매개변수)
    kwargs={"model":MODEL, "messages":messages, "tools":tools}

    # tool_choice 값 있으면 True, 없으면 False
    if tool_choice:     # True이면 kwargs 추가
        kwargs["tool_choice"] = tool_choice    # tool_choice key에 tool_choice 추가
    return get_client().chat.completions.create(**kwargs)
    # return create(model=MODEL, messages=messages, tools:tools)

# 3. LLM에서 특정 함수 실행을 문자열로 요청(tool_call)
# 요청받아 실행. => 실행 결과를 문자열로(LLM 보내야 해서.)
def run_tool(tool_call):    # tool_call: function name, arguments
    tool_name=tool_call.function.name       # 함수명 => 문자열
    func=FUNCTIONS.get(tool_name)       # 실행 가능한 함수 추출.
    # 1. name 확인. tool_call
    if func is None:    # 지정된 함수 이름이 아니다. LLM이 실수.
        return f"알 수 없는 함수입니다. : {tool_name}"
    # 2. argument 잘못된 경우, LLM 실수
    # 함수 실행 중 에러 발생: try except
    try:
        # 해당 함수 실행 전 argument 뽑아내야 함.
        args=json.loads(tool_call.function.argument)    # LLM이 만들어준 것.
        return str(func(**args))
    except Exception as e:  # func(**args)에서 실행 시 에러 발생
        # type(e).__name__ : 발생된 에러의 클래스
        return f"{tool_name} 실행 오류: {type(e).__name__}: {e}"
# 4. MAX_TURNS=10: 최신 10개의 대화만 저장.
def trim_history(messages, max_turns=MAX_TURNS):
    # user_idx: role == user 인 인덱스 추출
    # 턴 개수 확인에 사용.
    user_idx=[idx for idx, message in enumerate(messages) if message["role"]=="user"]
    
    # max_turns 비교
    if len(user_idx) <= max_turns :
        return messages     # max_turns 보다 작으면 자를 필요 없으니 그대로 return
    # 아래는 자르는 코드 있어야 함.
    # start : user_idx=[1,3,8,12]였다. max_turns=2라면 
    # start=-2, 즉 -max_turns
    start=user_idx[-max_turns]
    return messages[:1] + messages[start:]

# streamlit 처리
# 1. title
st.title("Chatbot")

# 2. client 생성
try:
    get_client()    # OpenAI() 생성 => 키 문제 발생
except OpenAIError as e:
    st.error(f"OpenAI 클라이언트를 생성하지 못 함. 키를 확인하세요. ({e})")
    st.stop()   # 실행 중지.

# 3. messages 생성 system 추가
if "messages" not in st.session_state:
    st.session_state["messages"]=[{
        "role":"system", "content":"너는 사용자를 도와주는 상담사야."
    }]

# 4. 대화 내용(messages)을 브라우저 화면에 출력
# role이 user or assistant 이고 content가 None이 아닐 때 출력
for message in st.session_state["messages"]:
    if message["role"] in ("user","assistant") and message.get("content"):
        st.chat_message(message["role"]).write(message["content"])

if user_input := st.chat_input():   # True라는 것은 질문 입력하고 엔터 or 클릭한 상태
    # 현재 메시지 추출
    messages=st.session_state.messages

    # turn 확인
    turn_start = len(messages)  # 턴의 개수 저장

    # messages에 현재 질문 추가
    messages.append({"role":"user","content":user_input})
    
    # 브라우저에 질문 표시
    st.chat_message("user").write(user_input)

    # LLM 보내고
    try:
        # 질문하고 답변을 받을 때까지 시간 걸림.
        with st.spinner("답변을 만드는 중"):
            # LLM에 보낸다.
            ai_message = get_ai_response(trim_history(messages), tools=tools).choices[0].message
            rounds=0    # 함수 호출 횟수 저장하는 변수 선언. 0으로 초기화

            # tool_calls에 값이 있다는 의미는 LLM에서 함수 요청이 있다는 뜻. 그러면 계속 반복
            while ai_message.tool_calls:    # 조건식 자리 tool_calls에 값이 있으면 True
                # 현재 요청서(함수 실행, LLM -> Client)를 messages에 추가
                messages.append({           # LLM => Client. ai_message에는 함수 요청이 들어있음.
                    "role":"assistant",     # LLM => Client
                    "content":ai_message.content,   # 일반적으로 None이다.
                    # tc.model_dump(): ChatCompletionMessageToolCall object => 딕셔너리 반환
                    # [{id, function.name, function.argument},{id, function.name, function.argument},{id, function.name, function.argument}]
                    "tool_calls":[tc.model_dump() for tc in ai_message.tool_calls]
                })
                # 함수 실행
                for tool_call in ai_message.tool_calls:
                    func_result = run_tool(tool_call=tool_call)     # 함수 한 번 실행, LLM에 보내려고
                    # LLM에 보내려면 messages에 append해야.
                    messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call.id,     # 꼭 id 필요(요청한 쪽으로 가야 함.)
                        "content":func_result
                    })
                rounds += 1
                choice = "none" if rounds >= MAX_ROUNDS else None
                # tool_choice : choice 가 사용된다.
                # LLM에 보내야. get_ai_response(messages, tools, tool_choice)
                ai_message = get_ai_response(   # response : 보내고 받는다.
                    trim_history(messages),
                    tools=tools,    # import tools
                    tool_choice=choice
                ).choices[0].message
            # end while
        # end with
    # end try
    except OpenAIError as e:    # except 들어왔다는 것은 에러 발생, 정상처리 되지 않음.
        # 위에서 append한 것들 다 삭제
        del messages[turn_start:]   # 턴 시작한 시점부터 삭제
        st.error(f"GPT 호출 중 오류 발생. 다시 질문하세요. ({type(e).__name__})")
        st.stop()
    # end except
    # 여기부터 코드 정상처리 상태 => 답변 정상 처리
    answer = ai_message.content or "(응답이 비어있습니다. 다시 질문해 주세요)"
    messages.append({"role":"assistant","content":answer})
    # 답변을 화면에 출력
    st.chat_message("assistant").write(answer)




    # 함수요청
    # 함수 실행
    # 다시 보내고
    # 답변
 