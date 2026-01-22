import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from indexing.embedder import get_embedding_model

from pymongo import MongoClient
import certifi
import streamlit as st

MONGODB_URI = os.getenv("MONGODB_URI") or st.secrets.get("MONGODB_URI")
DB_NAME = "code_rag"
COLLECTION_NAME = "embeddings"
INDEX_NAME = "vector_index"


def get_mongo_vectorstore():
    """
    Returns MongoDB vector store connection.
    """
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI not found in environment variables")

    client = MongoClient(
        MONGODB_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000
    )
    
    collection = client[DB_NAME][COLLECTION_NAME]

    embeddings = get_embedding_model()

    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=INDEX_NAME,
    )

def delete_repo_embeddings(repo_id: str, commit_hash: str):
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["code_rag"]
    collection = db["embeddings"]

    result = collection.delete_many({
        "repo_id": repo_id,
        "commit_hash": commit_hash
    })

    print(f"[DEBUG] Deleted {result.deleted_count} embeddings")