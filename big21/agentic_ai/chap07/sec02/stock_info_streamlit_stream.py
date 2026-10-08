from gpt_functions import get_current_time, tools, get_yf_stock_info, get_yf_stock_history, get_yf_stock_recommendations
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import json
import streamlit as st


load_dotenv(override=True)


MODEL = "gpt-4o"      # 사용할 모델
MAX_ROUNDS = 5        # 질문 1개당 함수 호출 라운드 최대 횟수
MAX_TURNS = 10        # GPT에 보낼 최근 대화(질문) 수


# 함수 이름 → 실제 파이썬 함수 연결표
FUNCTIONS = {
    "get_current_time": get_current_time,
    "get_yf_stock_info": get_yf_stock_info,
    "get_yf_stock_history": get_yf_stock_history,
    "get_yf_stock_recommendations": get_yf_stock_recommendations,
}




class StreamIncomplete(Exception):
    """스트림이 끝 신호(finish_reason) 없이 끊긴 경우"""




@st.cache_resource
def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




# [스트림] 응답을 조각(chunk)으로 받아 글은 화면에 바로 쓰고, 요청서 조각은 모아서 돌려준다
def stream_ai_response(messages, placeholder, tool_choice=None):
    kwargs = {"model": MODEL, "messages": messages, "tools": tools, "stream": True}
    if tool_choice:
        kwargs["tool_choice"] = tool_choice


    content = ""          # 지금까지 받은 글
    calls = {}            # 요청서 조립함: {번호(index): 요청서 딕셔너리}
    finish_reason = None  # 마지막 조각에 오는 끝 신호


    for chunk in get_client().chat.completions.create(**kwargs):
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta          # 이번 조각에 새로 온 부분
        if chunk.choices[0].finish_reason:
            finish_reason = chunk.choices[0].finish_reason


        if delta.content:                       # ① 글 조각
            content += delta.content
            placeholder.markdown(content + "▌")  # 타이핑 효과


        for tc in delta.tool_calls or []:       # ② 요청서 조각
            call = calls.setdefault(tc.index, {
                "id": None, "type": "function",
                "function": {"name": "", "arguments": ""},
            })
            if tc.id:
                call["id"] = tc.id
            if tc.function and tc.function.name:
                call["function"]["name"] = tc.function.name
            if tc.function and tc.function.arguments:
                call["function"]["arguments"] += tc.function.arguments


    if finish_reason is None:                   # 끝 신호 없이 끊김 → 잘린 답변
        raise StreamIncomplete("응답이 중간에 끊겼습니다.")
    if content:
        placeholder.markdown(content)           # 커서(▌) 지우고 최종 글 표시
    return content, [calls[i] for i in sorted(calls)]




# [스트림] 요청서가 딕셔너리이므로 이름·인자 문자열을 직접 받도록 변경
def run_tool(tool_name, arguments_json):
    func = FUNCTIONS.get(tool_name)
    if func is None:
        return f"알 수 없는 함수입니다: {tool_name}"
    try:
        arguments = json.loads(arguments_json)
        return str(func(**arguments))
    except Exception as e:
        return f"{tool_name} 실행 오류: {type(e).__name__}: {e}"




def trim_history(messages, max_turns=MAX_TURNS):
    user_idx = [i for i, m in enumerate(messages) if m["role"] == "user"]
    if len(user_idx) <= max_turns:
        return messages
    start = user_idx[-max_turns]
    return messages[:1] + messages[start:]




st.title("💬 Chatbot")


try:
    get_client()
except OpenAIError as e:
    st.error(f"OpenAI 클라이언트를 만들 수 없습니다. .env의 OPENAI_API_KEY를 확인하세요. ({e})")
    st.stop()


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},
    ]


for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        st.chat_message(msg["role"]).write(msg["content"])


if user_input := st.chat_input():
    messages = st.session_state.messages
    turn_start = len(messages)
    messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)


    # [스트림] 답변 말풍선을 먼저 만들고, 그 안의 빈 자리(placeholder)를 계속 덮어쓴다
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("답변을 만드는 중...")
        try:
            content, calls = stream_ai_response(trim_history(messages), placeholder)
            rounds = 0
            while calls:
                messages.append({
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": calls,              # 이미 딕셔너리라 model_dump() 불필요
                })
                names = ", ".join(c["function"]["name"] for c in calls)
                placeholder.markdown(f"*도구 실행 중: {names}*")
                for call in calls:
                    func_result = run_tool(call["function"]["name"], call["function"]["arguments"])
                    print(f"[도구] {call['function']['name']}({call['function']['arguments']}) → {func_result[:80]}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": func_result,
                    })
                rounds += 1
                choice = "none" if rounds >= MAX_ROUNDS else None
                content, calls = stream_ai_response(trim_history(messages), placeholder, tool_choice=choice)
        except (OpenAIError, StreamIncomplete) as e:
            del messages[turn_start:]
            placeholder.empty()
            st.error(f"GPT 호출 중 오류가 발생했습니다. 다시 질문해 주세요. ({type(e).__name__})")
            st.stop()


        answer = content or "(응답이 비어 있습니다. 다시 질문해 주세요.)"
        placeholder.markdown(answer)


    messages.append({"role": "assistant", "content": answer})
    print(f"AI\t: {answer}")
