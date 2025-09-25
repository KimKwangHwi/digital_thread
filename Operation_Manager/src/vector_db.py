import json
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import pickle

print("여기까지 실행됨1")
# 데이터 로드
file_path = Path(__file__).parent / "torus_manual" / "api_category.json"
data = json.loads(file_path.read_text(encoding="utf-8"))

# Document 리스트 생성
docs = []
for item in data:
    # 1. 유사도 검색을 위해 의미 있는 모든 텍스트를 page_content로 결합합니다.
    # (레이블은 제외하고 실제 내용만 합칩니다.)
    page_content = (
        f"{item['category_name']}. "
        f"{item['description']} "
        f"{', '.join(item['keywords'])}. "
    )
    metadata = {
        "category_id": item["category_id"],
        "category_name": item["category_name"],
        "functions": item["functions"]
    }
    
    docs.append(Document(page_content=page_content, metadata=metadata))
    
print("여기까지 실행됨2")

# 임베딩 생성
embeddings = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask')

print("여기까지 실행됨3")
print(f"Document 개수: {len(docs)}")


# FAISS 벡터스토어 생성 및 저장
try:
    vectorstore = FAISS.from_documents(
        documents=docs[:],  # 필요시 전체 docs로 변경 가능
        embedding=embeddings
    )
    print("FAISS 벡터스토어 api category 생성 완료")

    # 디스크에 저장 (pickle 사용)
    with open("faiss_store_category.pkl", "wb") as f:
        pickle.dump(vectorstore, f)
    print("FAISS 벡터스토어 저장 완료 (faiss_store_category.pkl)")
except Exception as e:
    print(f"오류 발생: {e}")

print("여기까지 실행됨4")