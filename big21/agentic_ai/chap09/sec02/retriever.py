from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma


load_dotenv(find_dotenv(), override=True)


# 임베딩 모델 객체 생성
embedding = OpenAIEmbeddings(model='text-embedding-3-large')


# LLM 모델 객체 생성
llm = ChatOpenAI(model='gpt-4o')


# Chroma Loading
persist_directory = r'C:\big21\agentic_ai\chap09\chroma_store'
vectorStore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding
)


# Retriever Create
retriever = vectorStore.as_retriever(k=3)


# Document Chain create
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


qustion_answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            '사용자의 질문에 대해 아래 context에 기반하여 답변하라. : \n\n{context}'
        ),
        MessagesPlaceholder(variable_name='messages'),
    ]
)


document_chain = create_stuff_documents_chain(llm, qustion_answer_prompt) | StrOutputParser()


# query augmentation chain
query_augmentation_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name='messages'), # 기존 대화 내용
    (
        'system',
        '기존의 대화 내용을 활용하여 사용자의 아래 질문의 의도를 파악하여 명료한 한 문장의 질문으로 변환하라 : \n\n{query}',
    )
])


query_augmentation_chain = query_augmentation_prompt | llm | StrOutputParser()
