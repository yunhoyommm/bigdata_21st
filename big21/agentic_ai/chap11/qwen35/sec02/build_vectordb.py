import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


# 경로는 이 파일 위치 기준 (chap11/qwen35/sec02 → ../../../chap09/data)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # 현재 디렉토리
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "..", "chap09", "data")) # agentic_ai/chap09/data 디렉토리.
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_store_qwen3emb")
PDF_FILES = ["OneNYC_2050_Strategic_Plan.pdf", "2040_seoul_plan.pdf"]
EMBED_MODEL = "qwen3-embedding:0.6b"   # 먼저: ollama pull qwen3-embedding:0.6b


# 이미 만든 DB에 또 넣으면 같은 문서가 두 번 저장되므로 멈춘다
if os.path.exists(PERSIST_DIR):
    raise SystemExit(f"이미 DB가 있습니다: {PERSIST_DIR}\n다시 만들려면 이 폴더를 지운 뒤 실행하세요.")


# 올라마 임베딩: 문서는 지시문 없이 그대로 숫자로 바꾼다 (질문만 지시문을 붙임 → retriever_qwen.py)
embedding = OllamaEmbeddings(model=EMBED_MODEL)


# 9장과 같은 크기로 자르기 (1000자, 겹침 100자)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = []
for name in PDF_FILES:
    pages = PyPDFLoader(os.path.join(DATA_DIR, name)).load()
    chunks = splitter.split_documents(pages)
    print(f"{name}: {len(pages)}쪽 → {len(chunks)}조각")
    splits.extend(chunks)


# 조각마다 임베딩을 계산해 새 폴더에 저장
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory=PERSIST_DIR,
)
print("저장 완료:", vectorstore._collection.count(), "조각 →", PERSIST_DIR)
 