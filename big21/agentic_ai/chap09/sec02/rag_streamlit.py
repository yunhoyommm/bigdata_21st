import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
import retriever
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(), override=True)


# LLM 모델 초기화
llm = ChatOpenAI(model='gpt-4o')


# 사용자의 메세지 처리하는 함수
def get_ai_response(messages, docs):
    response = retriever.document_chain.stream({
        'messages':messages,
        'context':docs
    })
    # for 루프가 돌면서 받아온 조각(chunk)을 하나씩 꺼내서 처리
    for chunk in response:
        # yield가 실행되면 현재의 chunk를 호출한 곳(streamlit)으로 바로 던져준다
        # 그리고 함수는 여기서 '일시정지' 상태가 된다
        # 호출한 쪽에서 처리가 끝나면 다시 깨어나서 다름 루프를 돕니다
        yield chunk


# Streamlit
st.title('GPT-40 Langchain Chat')


#
if 'messages' not in st.session_state:
    st.session_state['messages']=[
        SystemMessage('너는 문서에 기반해 답변하는 도시 정책 전문가야'), # 초기 메세지 설정
        AIMessage('How can I help you?')
    ]


# 화면에 질문(user)과 답변(ai) 메세지 출력
for message in st.session_state['messages']:
    if message.content:
        if isinstance(message, SystemMessage):
            st.chat_message('system').write(message.content)
        elif isinstance(message, AIMessage):
            st.chat_message('assistant').write(message.content)
        elif isinstance(message, HumanMessage):
            st.chat_message('user').write(message.content)


# 사용자 입력 처리
if prompt := st.chat_input(): # 입력하고 엔터, 클릭한 상태에서 실행된다
    st.chat_message('user').write(prompt)
    st.session_state['messages'].append(HumanMessage(prompt))


    augmented_query = retriever.query_augmentation_chain.invoke({
        'messages':st.session_state['messages'],
        'query':prompt,
    })
    print(f'Augmentation Qeury : {augmented_query}')


    # 벡터디비에서 검색(retriever)
    print('관련 문서 검색')
    docs = retriever.retriever.invoke(f'{prompt}\n{augmented_query}')


    if docs:
        with st.expander(f"**참조 문서 확인하기**"):
            for idx, doc in enumerate(docs,1):
                st.markdown(f"**문서{idx}: {doc.metadata.get('source','출처미상')}**")
                st.markdown(f"*Page : {doc.metadata.get('page','N/A')}*")
                st.text(doc.page_content)
                st.divider()


    with st.spinner(f'AI가 답변을 준비 중입니다...{augmented_query}'):
        chunk = get_ai_response(st.session_state['messages'], docs)
        result = st.chat_message('assistant').write_stream(chunk)


    st.session_state['messages'].append(AIMessage(result))