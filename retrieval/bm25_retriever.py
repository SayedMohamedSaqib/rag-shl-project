from langchain_community.retrievers import BM25Retriever



def build_bm25_retriever(documents):

    retriever = BM25Retriever.from_documents(
        documents
    )

    retriever.k = 20

    return retriever