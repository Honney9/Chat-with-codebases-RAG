from indexing.mongo_vector_store import get_mongo_vectorstore

def index_documents(documents, repo_id: str, force: bool = False):
    vectorstore = get_mongo_vectorstore()

    if force:
        vectorstore._collection.delete_many(
            {"metadata.repo_id": repo_id}
        )

    vectorstore.add_documents(documents)
