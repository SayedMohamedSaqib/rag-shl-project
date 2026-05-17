from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

EMBED_MODEL = "BAAI/bge-m3"

TOP_K = 10

SEMANTIC_TOP_K = 20

BM25_TOP_K = 20

RRF_K = 60

SEMANTIC_WEIGHT = 0.7

KEYWORD_WEIGHT = 0.3

DEVICE = "cuda"