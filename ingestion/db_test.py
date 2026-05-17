import os
import re
import json

from collections import Counter

import torch

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# CONFIG
# ============================================================

CATALOG_JSON = "data/json_documents/shl_catalog.json"

MARKDOWN_DIR = "data/markdown_documents"

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
# NORMALIZATION
# ============================================================

def normalize_name(text):

    """
    Normalize names for robust matching.

    Handles:
    - punctuation
    - spaces
    - symbols
    - case differences
    - special chars
    """

    if not text:

        return ""

    text = text.lower()

    text = text.replace("&", "and")

    text = text.replace("+", "plus")

    text = text.replace("/", "")

    text = text.replace("\\", "")

    text = re.sub(
        r"\(new\)",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9]",
        "",
        text
    )

    return text.strip()


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

def load_embeddings():

    print("\nLoading embeddings...")

    embeddings = HuggingFaceEmbeddings(

        model_name=EMBED_MODEL,

        model_kwargs={
            "device": device
        },

        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    print("Embeddings loaded")

    return embeddings


# ============================================================
# LOAD CHROMA DB
# ============================================================

def load_vector_store(embeddings):

    print("\nLoading Chroma DB...")

    vector_store = Chroma(

        persist_directory=CHROMA_DIR,

        embedding_function=embeddings
    )

    print("Chroma DB loaded successfully")

    return vector_store


# ============================================================
# LOAD RAW CATALOG
# ============================================================

def load_catalog():

    print("\nLoading raw catalog JSON...")

    with open(
        CATALOG_JSON,
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
# LOAD MARKDOWN FILES
# ============================================================

def load_markdown_files():

    print("\nScanning markdown files...")

    md_files = [

        f for f in os.listdir(MARKDOWN_DIR)

        if f.endswith(".md")
    ]

    print(
        f"Found {len(md_files)} markdown files"
    )

    return md_files


# ============================================================
# INSPECT CHROMA
# ============================================================

def inspect_chroma(vector_store):

    print("\nInspecting Chroma DB...")

    collection = vector_store._collection

    data = collection.get()

    documents = data["documents"]

    metadatas = data["metadatas"]

    ids = data["ids"]

    print(
        f"\nTotal vectors stored: {len(ids)}"
    )

    return documents, metadatas, ids


# ============================================================
# COUNT VALIDATION
# ============================================================

def check_counts(
    catalog,
    md_files,
    chroma_ids
):

    print("\n" + "=" * 80)

    print("COUNT VALIDATION")

    print("=" * 80)

    print(
        f"\nCatalog Entries: {len(catalog)}"
    )

    print(
        f"Markdown Files: {len(md_files)}"
    )

    print(
        f"Chroma Documents: {len(chroma_ids)}"
    )

    if (
        len(catalog)
        == len(md_files)
        == len(chroma_ids)
    ):

        print(
            "\nPASS: Counts match perfectly"
        )

    else:

        print(
            "\nWARNING: Count mismatch detected"
        )


# ============================================================
# DUPLICATE CHECK
# ============================================================

def check_duplicates(
    md_files,
    chroma_ids
):

    print("\n" + "=" * 80)

    print("DUPLICATE CHECK")

    print("=" * 80)

    # ========================================================
    # MARKDOWN DUPLICATES
    # ========================================================

    md_counter = Counter(md_files)

    duplicate_md = [

        file

        for file, count in md_counter.items()

        if count > 1
    ]

    if duplicate_md:

        print(
            "\nDuplicate markdown files:"
        )

        for file in duplicate_md:

            print(file)

    else:

        print(
            "\nPASS: No duplicate markdown files"
        )

    # ========================================================
    # CHROMA DUPLICATES
    # ========================================================

    chroma_counter = Counter(chroma_ids)

    duplicate_ids = [

        doc_id

        for doc_id, count in chroma_counter.items()

        if count > 1
    ]

    if duplicate_ids:

        print(
            "\nDuplicate Chroma IDs:"
        )

        for doc_id in duplicate_ids:

            print(doc_id)

    else:

        print(
            "\nPASS: No duplicate Chroma IDs"
        )


# ============================================================
# METADATA VALIDATION
# ============================================================

def check_metadata(metadatas):

    print("\n" + "=" * 80)

    print("METADATA VALIDATION")

    print("=" * 80)

    required_fields = [

        "id",
        "name",
        "url",
        "duration",
        "adaptive",
        "remote",
        "job_levels",
        "languages",
        "categories",
        "status"
    ]

    issues = 0

    for idx, metadata in enumerate(
        metadatas
    ):

        for field in required_fields:

            if field not in metadata:

                print(
                    f"\nMissing field '{field}' "
                    f"in document {idx}"
                )

                issues += 1

            elif metadata[field] in [
                None,
                "",
                [],
            ]:

                print(
                    f"\nEmpty field '{field}' "
                    f"in document {idx}"
                )

                issues += 1

    if issues == 0:

        print(
            "\nPASS: Metadata validation passed"
        )

    else:

        print(
            f"\nWARNING: Found {issues} metadata issues"
        )


# ============================================================
# MARKDOWN ↔ CHROMA ALIGNMENT
# ============================================================

def check_markdown_alignment(
    md_files,
    metadatas
):

    print("\n" + "=" * 80)

    print("MARKDOWN ↔ CHROMA ALIGNMENT")

    print("=" * 80)

    # ========================================================
    # NORMALIZED CHROMA NAMES
    # ========================================================

    chroma_names = {

        normalize_name(
            metadata.get("name", "")
        )

        for metadata in metadatas
    }

    missing = []

    matched = []

    for md_file in md_files:

        clean_name = normalize_name(

            md_file.replace(".md", "")
        )

        if clean_name not in chroma_names:

            missing.append(md_file)

        else:

            matched.append(md_file)

    # ========================================================
    # RESULTS
    # ========================================================

    print(
        f"\nMatched Files: {len(matched)}"
    )

    print(
        f"Missing Files: {len(missing)}"
    )

    if not missing:

        print(
            "\nPASS: All markdown files aligned"
        )

    else:

        print(
            "\nWARNING: Missing markdown mappings:"
        )

        for item in missing:

            print(item)


# ============================================================
# CATEGORY ANALYSIS
# ============================================================

def analyze_categories(metadatas):

    print("\n" + "=" * 80)

    print("CATEGORY DISTRIBUTION")

    print("=" * 80)

    category_counter = Counter()

    for metadata in metadatas:

        categories = metadata.get(
            "categories",
            []
        )

        for category in categories:

            category_counter[category] += 1

    print("\nTop categories:\n")

    for category, count in category_counter.most_common():

        print(f"{category}: {count}")


# ============================================================
# SAMPLE DOCUMENT INSPECTION
# ============================================================

def sample_documents(
    documents,
    metadatas,
    sample_size=5
):

    print("\n" + "=" * 80)

    print("SAMPLE DOCUMENT INSPECTION")

    print("=" * 80)

    for idx in range(

        min(sample_size, len(documents))
    ):

        print(f"\nDOCUMENT {idx + 1}")

        print("-" * 80)

        print("\nMETADATA:\n")

        print(

            json.dumps(
                metadatas[idx],
                indent=2
            )
        )

        print("\nDOCUMENT PREVIEW:\n")

        print(documents[idx][:1000])

        print("\n" + "=" * 80)


# ============================================================
# SUMMARY REPORT
# ============================================================

def generate_summary(
    catalog,
    md_files,
    ids,
    metadatas
):

    print("\n" + "=" * 80)

    print("DATABASE SUMMARY")

    print("=" * 80)

    print(
        f"\nCatalog Entries: {len(catalog)}"
    )

    print(
        f"Markdown Files: {len(md_files)}"
    )

    print(
        f"Stored Embeddings: {len(ids)}"
    )

    # ========================================================
    # REMOTE DISTRIBUTION
    # ========================================================

    remote_counter = Counter(

        metadata.get("remote", "unknown")

        for metadata in metadatas
    )

    print("\nRemote Testing Distribution:")

    for key, value in remote_counter.items():

        print(f"{key}: {value}")

    # ========================================================
    # ADAPTIVE DISTRIBUTION
    # ========================================================

    adaptive_counter = Counter(

        metadata.get("adaptive", "unknown")

        for metadata in metadatas
    )

    print("\nAdaptive Distribution:")

    for key, value in adaptive_counter.items():

        print(f"{key}: {value}")

    # ========================================================
    # LANGUAGE DISTRIBUTION
    # ========================================================

    language_counter = Counter()

    for metadata in metadatas:

        for language in metadata.get(
            "languages",
            []
        ):

            language_counter[language] += 1

    print("\nTop Languages:")

    for lang, count in language_counter.most_common(10):

        print(f"{lang}: {count}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 80)

    print("SHL DATABASE INSPECTION")

    print("=" * 80)

    # ========================================================
    # LOAD DATA
    # ========================================================

    catalog = load_catalog()

    md_files = load_markdown_files()

    embeddings = load_embeddings()

    vector_store = load_vector_store(
        embeddings
    )

    documents, metadatas, ids = inspect_chroma(
        vector_store
    )

    # ========================================================
    # VALIDATIONS
    # ========================================================

    check_counts(
        catalog,
        md_files,
        ids
    )

    check_duplicates(
        md_files,
        ids
    )

    check_metadata(
        metadatas
    )

    check_markdown_alignment(
        md_files,
        metadatas
    )

    analyze_categories(
        metadatas
    )

    generate_summary(
        catalog,
        md_files,
        ids,
        metadatas
    )

    sample_documents(
        documents,
        metadatas
    )

    # ========================================================
    # FINAL
    # ========================================================

    print("\n" + "=" * 80)

    print("DATABASE INSPECTION COMPLETED")

    print("=" * 80)


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()