# # ###working but gives irrelivent doc content
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from langchain_chroma import Chroma
# from config.settings import GEMINI_API_KEY
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# # from langchain_community.vectorstores import Chroma
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter


# # Paths
# POLICY_FOLDER = "data/policies"
# CHROMA_DB_DIR = "retriever/chroma_db"


# # ✅ Embedding model
# embedding = GoogleGenerativeAIEmbeddings(
#     model="models/embedding-001",
#     google_api_key=GEMINI_API_KEY
# )


# # ✅ Load and split ALL .txt documents from /data/policies
# def load_and_split_documents():
#     docs = []
#     splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

#     for file in os.listdir(POLICY_FOLDER):
#         if file.endswith(".txt"):
#             file_path = os.path.join(POLICY_FOLDER, file)
#             print(f"📄 Loading file: {file}")
#             loader = TextLoader(file_path, encoding="utf-8")
#             text_docs = loader.load()
#             split_docs = splitter.split_documents(text_docs)
#             docs.extend(split_docs)

#     print(f"✅ Loaded {len(docs)} chunks from {len(os.listdir(POLICY_FOLDER))} files.")
#     return docs


# # ✅ Build vector DB
# def get_vector_store():
#     os.makedirs(CHROMA_DB_DIR, exist_ok=True)
#     docs = load_and_split_documents()
#     vectordb = Chroma.from_documents(
#         documents=docs,
#         embedding=embedding,
#         persist_directory=CHROMA_DB_DIR
#     )
#     print("✅ Vector DB persisted successfully.")
#     return vectordb


# # ✅ Search helper (test via CLI)
# def search_similar_documents(query, k=4):
#     vectordb = Chroma(
#         persist_directory=CHROMA_DB_DIR,
#         embedding_function=embedding
#     )
#     results = vectordb.similarity_search(query, k=k)
#     print(f"\n🔍 Search Results for: {query}")
#     for r in results:
#         print("•", r.page_content[:200])
#     return [doc.page_content for doc in results]


# # ✅ CLI Test Entry Point
# if __name__ == "__main__":
#     store = get_vector_store()
#     print("\n🎉 Vector Store is ready for all your company policies.")

#     # # Test queries
#     # search_similar_documents("What are the holidays in 2025?")
#     # search_similar_documents("What is the dress code?")
#     # search_similar_documents("What is the leave policy?")
# # ###working but gives irrelivent doc content

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import GEMINI_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Constants
POLICY_FOLDER = "data/policies"
CHROMA_DB_DIR = "retriever/chroma_db"

# ✅ Embedding model
embedding = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

# ✅ Load and split only policy files
def load_and_split_documents():
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    for file in os.listdir(POLICY_FOLDER):
        if file.endswith(".txt") and "policy" in file.lower():  # load only policy files
            file_path = os.path.join(POLICY_FOLDER, file)
            loader = TextLoader(file_path, encoding="utf-8")
            text_docs = loader.load()
            split_docs = splitter.split_documents(text_docs)
            docs.extend(split_docs)

    return docs

# ✅ Create vector store & persist
def get_vector_store():
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    docs = load_and_split_documents()

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=CHROMA_DB_DIR
    )
    vectordb.persist()  # ✅ persist the DB
    return vectordb

# ✅ Search similar documents
# def search_similar_documents(query, k=4):
#     vectordb = Chroma(
#         persist_directory=CHROMA_DB_DIR,
#         embedding_function=embedding
#     )
#     results = vectordb.similarity_search(query, k=k)

#     # 🧪 Debug print
#     print(f"\n[DEBUG] Retrieved {len(results)} document chunks for query: '{query}'\n")
#     for i, doc in enumerate(results):
#         print(f"[{i+1}] {doc.page_content[:300]}...\n")  # Preview first 300 chars

#     return [doc.page_content for doc in results]
def search_similar_documents(query, k=4):
    vectordb = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding)
    results = vectordb.similarity_search(query, k=k)
    # print(f"\n🔍 RAG Search Results for: {query}")
    # for r in results:
        # print("•", r.page_content[:200])
    return [doc.page_content for doc in results]


# ✅ CLI Test
if __name__ == "__main__":
    store = get_vector_store()
    print("✅ Vector store created and persisted successfully!")