import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # 현재 파일이 존재하는 위치의 디렉토리를 의미.
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_store_qwen3emb")   # vectorDB 위치 지정
EMBED_MODEL = "qwen3-embedding:0.6b"    # 임베딩 모델 지정
LLM_MODEL = "qwen3.5:4b"        # LLM 모델 지정


# 질문에만 붙이는 지시문 (qwen3-embedding 모델 카드의 형식, 영어 권장)
QUERY_TASK = "Given a web search query, retrieve relevant passages that answer the query"




class QwenQueryEmbeddings(OllamaEmbeddings):
    """문서는 그대로, 질문은 'Instruct: …\\nQuery:질문' 형식으로 바꿔 임베딩"""


    def embed_query(self, text: str) -> list[float]:
        return super().embed_query(f"Instruct: {QUERY_TASK}\nQuery:{text}")




# 벡터 DB가 없으면 바로 멈춤 (빈 DB가 조용히 만들어지는 것 방지)
if not os.path.isdir(PERSIST_DIR):
    raise FileNotFoundError(f"벡터 DB가 없습니다: {PERSIST_DIR}\n먼저 build_vectordb.py를 실행하세요.")


embedding = QwenQueryEmbeddings(model=EMBED_MODEL)
print("Loading Chroma store:", PERSIST_DIR)
vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding)   # 설치된 벡터db 메모리에 적재.
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})    # 검색할 수 있는 것 생성


# RAG용 언어 모델: 생각 끄기(빠르게) + 비생각 모드 권장값 + 문서가 들어가도록 문맥 8K
llm = ChatOllama(model=LLM_MODEL, reasoning=False, temperature=0.7, top_p=0.8, num_ctx=8192)




def format_docs(docs):
    """문서 목록 → 본문 글만 빈 줄로 이어 붙인 문자열"""
    return "\n\n".join(doc.page_content for doc in docs)




# 답변 프롬프트: 지시 + 문서는 system, 그 뒤에 대화 기록
question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 문서에 기반해 답변하는 도시 정책 전문가야. "
                   "사용자의 질문에 대해 아래 context에 기반하여 한국어로 답변하라. "
                   "context에 없는 내용은 모른다고 답하라.\n\n{context}"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
document_chain = question_answering_prompt | llm | StrOutputParser()    # 질문과 검색 결과를 llm에 보낸다. 정상적 답변을 생성.


# 질의 확장 프롬프트: 지금 질문 이전 대화 + 마지막 사람 메시지에 지시와 질문
query_augmentation_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        ("human", "위 대화를 참고해 아래 질문의 의도를 파악하여 명료한 한 문장의 질문으로 변환하라. "
                  "대명사나 이, 저, 그와 같은 표현을 명확한 명사로 표현하라. 변환한 질문만 출력하라.\n\n"
                  "질문: {query}"),
    ]
)
query_augmentation_chain = query_augmentation_prompt | llm | StrOutputParser()  # 질문 증강.
