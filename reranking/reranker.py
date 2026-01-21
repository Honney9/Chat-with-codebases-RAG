from indexing.embedder import get_embedding_model
import numpy as np

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )

def rerank_documents(query: str, documents):

    embedder = get_embedding_model()

    query_embedding = embedder.embed_query(query)

    scored_docs=[]

    for doc in documents:
        doc_embedding = embedder.embed_query(doc.page_content)
        score = cosine_similarity(query_embedding, doc_embedding)
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse= True)

    return [doc for _, doc in scored_docs]