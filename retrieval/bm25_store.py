from langchain_community.retrievers import (
    BM25Retriever,
)

from retrieval.vector_store import (
    get_vector_store,
)

_bm25 = None


def get_bm25_retriever():

    global _bm25

    if _bm25 is None:

        vector_store = get_vector_store()

        docs = vector_store.similarity_search(
            "assessment",
            k=200
        )

        _bm25 = BM25Retriever.from_documents(
            docs
        )

        _bm25.k = 10

    return _bm25