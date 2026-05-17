from retrieval.config import SEMANTIC_TOP_K



def build_semantic_retriever(vector_store):

    retriever = vector_store.as_retriever(

        search_kwargs={
            "k": SEMANTIC_TOP_K
        }
    )

    return retriever