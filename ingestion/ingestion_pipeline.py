import os
import json
import shutil
import requests
import torch

from dotenv import load_dotenv

from langchain_core.documents import Document

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()


# ============================================================
# CONFIG
# ============================================================

CATALOG_URL = (
    "https://tcp-us-prod-rnd.shl.com/"
    "voiceRater/shl-ai-hiring/shl_product_catalog.json"
)

DATA_DIR = "data/json_documents"

CHROMA_DIR = "chroma_db"

EMBED_MODEL = "BAAI/bge-m3"


# ============================================================
# DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"\nUsing device: {device}")

if device == "cuda":

    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# RESET CHROMA DB
# ============================================================

def reset_chroma():

    if os.path.exists(CHROMA_DIR):

        print("\nDeleting existing Chroma DB...")

        shutil.rmtree(CHROMA_DIR)

        print("Old Chroma DB deleted")


# ============================================================
# DOWNLOAD CATALOG
# ============================================================

def download_catalog():

    print("\nDownloading SHL catalog...")

    response = requests.get(CATALOG_URL)

    response.raise_for_status()

    filepath = os.path.join(
        DATA_DIR,
        "shl_catalog.json"
    )

    with open(filepath, "wb") as f:

        f.write(response.content)

    print("Catalog downloaded successfully")

    return filepath


# ============================================================
# LOAD JSON
# ============================================================

def load_catalog(filepath):

    print("\nLoading catalog JSON...")

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(
            f,
            strict=False
        )

    print(
        f"Loaded {len(data)} catalog entries"
    )

    return data


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_list(value):

    if isinstance(value, list):

        cleaned = [

            str(x).strip()

            for x in value

            if x is not None and str(x).strip()
        ]

        return cleaned

    return []


def safe_str(value):

    if value is None:

        return ""

    return str(value).strip()


# ============================================================
# BUILD DOCUMENTS
# ============================================================

def build_documents(data):

    print("\nBuilding semantic documents...")

    docs = []

    skipped = 0

    for item in data:

        try:

            # ====================================================
            # SAFE EXTRACTION
            # ====================================================

            name = safe_str(
                item.get("name")
            ) or "N/A"

            description = safe_str(
                item.get("description")
            ) or "N/A"

            duration = safe_str(
                item.get("duration")
            ) or "N/A"

            job_levels = safe_list(
                item.get("job_levels")
            ) or ["N/A"]

            languages = safe_list(
                item.get("languages")
            ) or ["N/A"]

            categories = safe_list(
                item.get("keys")
            ) or ["N/A"]

            adaptive = safe_str(
                item.get("adaptive")
            ) or "N/A"

            remote = safe_str(
                item.get("remote")
            ) or "N/A"

            # ====================================================
            # DERIVE TEST TYPE
            # ====================================================

            test_type = "Unknown"

            categories_text = " ".join(
                categories
            ).lower()

            if (
                "knowledge" in categories_text
                or "skills" in categories_text
            ):

                test_type = "K"

            elif (
                "personality" in categories_text
                or "behavior" in categories_text
            ):

                test_type = "P"

            elif (
                "ability" in categories_text
                or "aptitude" in categories_text
            ):

                test_type = "A"

            elif (
                "simulation" in categories_text
            ):

                test_type = "S"

            # ====================================================
            # BGE INSTRUCTION-TUNED DOCUMENT
            # ====================================================

            content = f"""
Represent this assessment catalog entry for retrieval.

# Assessment
{name}

## Description
{description}

## Duration
{duration}

## Job Levels
{chr(10).join(f"- {x}" for x in job_levels)}

## Languages
{chr(10).join(f"- {x}" for x in languages)}

## Categories
{chr(10).join(f"- {x}" for x in categories)}

## Adaptive
{adaptive}

## Remote Testing
{remote}
""".strip()

            # ====================================================
            # CHROMA-SAFE METADATA
            # ====================================================

            metadata = {

                # Core identity
                "id": safe_str(
                    item.get("entity_id")
                ) or "N/A",

                "name": name,

                "url": safe_str(
                    item.get("link")
                ) or "N/A",

                "test_type": test_type,

                # Retrieval filters
                "duration": duration,

                "adaptive": adaptive,

                "remote": remote,

                # Non-empty lists
                "job_levels": ", ".join(job_levels),

                "languages": ", ".join(languages),

                "categories": ", ".join(categories),

                # Misc
                "status": safe_str(
                    item.get("status")
                ) or "N/A"
            }

            docs.append(
                Document(
                    page_content=content,
                    metadata=metadata
                )
            )

        except Exception as e:

            skipped += 1

            print(
                f"Skipping malformed entry: {e}"
            )

    print(f"\nBuilt {len(docs)} documents")

    print(
        f"Skipped {skipped} malformed entries"
    )

    return docs


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings():

    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(

        model_name=EMBED_MODEL,

        model_kwargs={
            "device": device
        },

        encode_kwargs={

            "normalize_embeddings": True,

            "batch_size": 32
        }
    )

    print("Embedding model loaded")

    return embeddings


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vector_store(
    docs,
    embeddings
):

    print("\nCreating Chroma vector store...")

    vector_store = Chroma.from_documents(

        documents=docs,

        embedding=embeddings,

        persist_directory=CHROMA_DIR,

        collection_metadata={
            "hnsw:space": "cosine"
        }
    )

    print(
        "\nVector store created successfully!"
    )

    return vector_store


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 80)

    print("SHL INGESTION PIPELINE")

    print("=" * 80)

    reset_chroma()

    filepath = download_catalog()

    data = load_catalog(filepath)

    docs = build_documents(data)

    print("\nSample document:\n")

    print(docs[0].page_content)

    print("\nSample metadata:\n")

    print(docs[0].metadata)

    embeddings = create_embeddings()

    create_vector_store(
        docs,
        embeddings
    )

    print("\n" + "=" * 80)

    print("INGESTION COMPLETED SUCCESSFULLY")

    print("=" * 80)

    print(f"\nTotal Documents Stored: {len(docs)}")

    print(f"Embedding Model: {EMBED_MODEL}")

    print(f"Vector DB Location: {CHROMA_DIR}")

    print(f"Device Used: {device}")

    print("\nPipeline finished successfully")


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()
