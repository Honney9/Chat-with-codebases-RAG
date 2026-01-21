from indexing.mongo_vector_store import get_mongo_vectorstore

def retrieve_documents(query: str, repo_id: str, k: int = 6):
    vectorstore = get_mongo_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": k,
            "pre_filter": {   # MongoDB Atlas requirement
                "repo_id": repo_id
            }
        }
    )

    # ✅ IMPORTANT: return DOCUMENTS, not retriever
    documents = retriever.invoke(query)
    return documents
