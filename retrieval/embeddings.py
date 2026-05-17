import torch

from langchain_huggingface import HuggingFaceEmbeddings

from retrieval.config import EMBED_MODEL


DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


def load_embeddings():

    embeddings = HuggingFaceEmbeddings(

        model_name=EMBED_MODEL,

        model_kwargs={
            "device": DEVICE
        },

        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    return embeddings