from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# qwen3.5:4b — 4비트 약 3.3GB, 6GB GPU에 다 올라감 (먼저: ollama pull qwen3.5:4b)
# reasoning=True : 생각은 additional_kwargs["reasoning_content"]로, 답은 content로 따로 받음
llm = ChatOllama(model="qwen3.5:4b", reasoning=False)


messages = [
    SystemMessage("너는 사용자를 도와주는 상담사야. 한국어로만 답변해줘."),
]


while True:
    user_input = input("사용자: ").strip()


    if user_input in ("exit", "quit", "q"):
        print("Goodbye!")
        break


    messages.append(HumanMessage(user_input))


    ai_message = None
    answer_started = False
    print("[생각] ", end="", flush=True)
    for chunk in llm.stream(messages):
        thinking = chunk.additional_kwargs.get("reasoning_content", "")
        if thinking:
            print(thinking, end="", flush=True)
        if chunk.content and not answer_started:
            print("\n[답변] ", end="", flush=True)
            answer_started = True
        print(chunk.content, end="", flush=True)
        ai_message = chunk if ai_message is None else ai_message + chunk
    print()


    # content에는 답만 들어 있으므로 그대로 기록 (생각을 떼어 낼 필요 없음)
    messages.append(AIMessage(ai_message.content))
