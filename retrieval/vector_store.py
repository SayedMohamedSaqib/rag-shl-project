from langchain_chroma import Chroma

from retrieval.config import CHROMA_DIR



def load_vector_store(embeddings):

    vector_store = Chroma(

        persist_directory=str(CHROMA_DIR),

        embedding_function=embeddings
    )

    return vector_store