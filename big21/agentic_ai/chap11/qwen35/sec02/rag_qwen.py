import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import retrieval_qwen as rt  # import할 때 임베딩·DB·LLM 객체를 한 번 만듦 (서버당 1회)




# 답변을 조각 단위로 내보내는 제너레이터
def get_ai_response(messages, docs):
    response = rt.document_chain.stream({
        "messages": messages,
        "context": rt.format_docs(docs),
    })
    for chunk in response:
        yield chunk




st.title("💬 Qwen3.5-4B 로컬 RAG Chat")


# 대화 기록: 지시(system)는 retriever_qwen의 프롬프트에 있으므로 여기에는 넣지 않는다
if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage("How can I help you?")]


for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)


if prompt := st.chat_input():
    st.chat_message("user").write(prompt)


    # 1) 질의 확장: 지금 질문 이전 기록 + 질문 (생각 모드를 껐으므로 결과는 질문 한 문장)
    with st.spinner("질문을 검색하기 좋은 문장으로 바꾸는 중..."):
        augmented_query = rt.query_augmentation_chain.invoke({
            "messages": st.session_state["messages"],
            "query": prompt,
        })
    print("augmented_query\t", augmented_query)
    st.session_state.messages.append(HumanMessage(prompt))


    # 2) 검색: 원래 질문 + 확장 질문 (질문용 지시문은 임베딩 클래스가 붙임)
    docs = rt.retriever.invoke(f"{prompt}\n{augmented_query}")
    for doc in docs:
        source = os.path.basename(doc.metadata.get("source", "알 수 없음"))  # 파일 이름만
        with st.expander(f"**문서:** {source}"):
            st.write(f"**page:** {doc.metadata.get('page', '')}")
            st.text(doc.page_content)


    # 3) 답변: 흘려보내며 화면에 쓰고, 끝나면 기록에 저장
    with st.spinner(f"AI가 답변을 준비 중입니다... '{augmented_query}'"):
        result = st.chat_message("assistant").write_stream(
            get_ai_response(st.session_state["messages"], docs))
    st.session_state["messages"].append(AIMessage(result))
