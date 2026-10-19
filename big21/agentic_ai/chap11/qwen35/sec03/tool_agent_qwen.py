from datetime import datetime
from zoneinfo import ZoneInfo


from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama




@tool
def get_current_time(timezone: str = "Asia/Seoul") -> str:
    """지정한 시간대(IANA 이름, 예: Asia/Seoul, America/New_York)의 현재 날짜와 시각을 알려 준다."""
    now = datetime.now(ZoneInfo(timezone))
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")




@tool
def multiply(a: float, b: float) -> float:
    """두 수 a와 b를 곱한 값을 돌려준다."""
    return a * b




tools = [get_current_time, multiply]
tool_map = {t.name: t for t in tools}


# 딥시크-R1은 여기서 'does not support tools' 오류가 났지만 qwen3.5는 도구 호출을 지원한다
llm = ChatOllama(model="qwen3.5:4b", reasoning=False, temperature=0.7, top_p=0.8)
llm_with_tools = llm.bind_tools(tools)


MAX_STEPS = 5  # 도구 호출이 끝없이 반복되는 것을 막는 상한 (10장 교훈)


messages = [SystemMessage("너는 도구를 활용해 정확히 답하는 비서야. 한국어로 답해.")]


while True:
    user_input = input("사용자: ").strip()
    if user_input in ("exit", "quit", "q"):
        break
    messages.append(HumanMessage(user_input))


    for step in range(MAX_STEPS):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        if not ai_msg.tool_calls:          # 도구 요청이 없으면 최종 답
            print("AI:", ai_msg.content)
            break
        for call in ai_msg.tool_calls:     # 요청된 도구를 실행하고 결과를 돌려준다
            try:
                result = tool_map[call["name"]].invoke(call["args"])
            except Exception as e:         # 잘못된 인자 등 → 오류 내용을 모델에게 알려 줌
                result = f"도구 실행 오류: {e}"
            print(f"  [도구] {call['name']}({call['args']}) → {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    else:
        print("AI: 도구 호출이 너무 많아 중단했습니다.")
