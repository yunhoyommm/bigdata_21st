# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


llm = ChatOllama(model="qwen3.5:4b")


messages = [
    SystemMessage("너는 사용자를 도와주는 상담사야. 한국어로만 답변해줘."),
]


while True:
    user_input = input("사용자: ")


    if user_input == "exit":
        break
   
    messages.append(
        HumanMessage(user_input)
    )  
   
    response = llm.stream(messages) # 실시간 처리, chunk 단위 출력
    #②
    ai_message = None
    for chunk in response:
        print(chunk.content, end="")    # 답변을 찍어준다.
        if ai_message is None:
            ai_message = chunk
        else:
            ai_message += chunk
    print('')
    #③
    # message_only = ai_message.content.strip()
    messages.append(AIMessage(ai_message.content))


    # print("AI: " + response.content)
 