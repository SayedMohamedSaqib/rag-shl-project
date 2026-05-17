import sys
import os

from pathlib import Path

from huggingface_hub import login

login(token=os.getenv("HF_TOKEN"))

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from retrieval.embeddings import (
    load_embeddings
)

from retrieval.vector_store import (
    load_vector_store
)

from retrieval.semantic_retriever import (
    build_semantic_retriever
)

from retrieval.retrieval_pipeline import (
    RetrievalPipeline
)

from langchain_community.retrievers import (
    BM25Retriever
)


# ============================================================
# LOAD DOCS FROM CHROMA
# ============================================================

def load_docs(vector_store):

    collection = vector_store._collection

    data = collection.get()

    docs = []

    from langchain_core.documents import (
        Document
    )

    for doc, metadata in zip(

        data["documents"],

        data["metadatas"]
    ):

        docs.append(

            Document(

                page_content=doc,

                metadata=metadata
            )
        )

    return docs


# ============================================================
# MAIN
# ============================================================

def main():

    print("\nLoading embeddings...")

    embeddings = load_embeddings()

    print("Embeddings loaded")

    # ========================================================
    # VECTOR STORE
    # ========================================================

    print("\nLoading vector store...")

    vector_store = load_vector_store(
        embeddings
    )

    print("Vector store loaded")

    # ========================================================
    # SEMANTIC RETRIEVER
    # ========================================================

    semantic_retriever = (
        build_semantic_retriever(
            vector_store
        )
    )

    # ========================================================
    # LOAD DOCS
    # ========================================================

    print("\nLoading docs from Chroma...")

    docs = load_docs(vector_store)

    print(f"Loaded {len(docs)} docs")

    # ========================================================
    # BM25
    # ========================================================

    print("\nBuilding BM25 retriever...")

    bm25_retriever = (
        BM25Retriever.from_documents(
            docs
        )
    )

    bm25_retriever.k = 20

    print("BM25 ready")

    # ========================================================
    # PIPELINE
    # ========================================================

    pipeline = RetrievalPipeline(

        semantic_retriever=

            semantic_retriever,

        bm25_retriever=

            bm25_retriever
    )

    # ========================================================
    # TEST LOOP
    # ========================================================

    while True:

        query = input(

            "\nQuery (or 'exit'): "
        )

        if query.lower() == "exit":

            break

        messages = [

            {
                "role": "user",

                "content": query
            }
        ]

        results = pipeline.run(
            messages
        )

        print("\n" + "=" * 80)

        print("RESULTS")

        print("=" * 80)

        for idx, result in enumerate(

            results,

            start=1
        ):

            doc = result["document"]

            score = result["score"]

            metadata = doc.metadata

            print(
                f"\n{idx}. "
                f"{metadata.get('name')}"
            )

            print(
                f"URL: "
                f"{metadata.get('url')}"
            )

            print(
                f"RRF Score: {score}"
            )

            print(
                f"Categories: "
                f"{metadata.get('categories')}"
            )

            print("-" * 80)


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()