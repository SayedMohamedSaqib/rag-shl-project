from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from retrieval.config import EMBED_MODEL

# ============================================================
# SINGLETONS
# ============================================================

_embeddings = None

_vector_store = None


# ============================================================
# GET VECTOR STORE
# ============================================================

def get_vector_store():

    global _embeddings
    global _vector_store

    if _vector_store is None:

        print("\nLoading embeddings...")

        _embeddings = HuggingFaceEmbeddings(

            model_name=EMBED_MODEL,

            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        print("Embeddings loaded")

        print("\nLoading vector store...")

        _vector_store = Chroma(

            persist_directory="chroma_db",

            embedding_function=_embeddings,
        )

        print("Vector store loaded")

    return _vector_store