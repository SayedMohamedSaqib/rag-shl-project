from retrieval.constraint_extractor import (
    extract_constraints,
)


# ============================================================
# EXTRACT ASSESSMENT NAMES
# ============================================================

def extract_assessment_names(text):

    comparison_terms = [

        "vs",

        "versus",

        "compare",

        "difference",
    ]

    cleaned = text.lower()

    for term in comparison_terms:

        cleaned = cleaned.replace(
            term,
            "|"
        )

    parts = [

        p.strip()

        for p in cleaned.split("|")

        if p.strip()
    ]

    return parts[:2]


# ============================================================
# FIND MATCHING DOCS
# ============================================================

def find_matching_documents(

    documents,

    assessment_names
):

    matches = []

    for target in assessment_names:

        best_match = None

        best_score = 0

        for doc in documents:

            name = doc.metadata.get(
                "name",
                ""
            ).lower()

            if target in name:

                score = len(target)

                if score > best_score:

                    best_match = doc

                    best_score = score

        if best_match:

            matches.append(best_match)

    return matches


# ============================================================
# BUILD COMPARISON
# ============================================================

def build_comparison_response(docs):

    if len(docs) < 2:

        return (

            "I could not find both "
            "SHL assessments for "
            "comparison."
        )

    doc1 = docs[0]

    doc2 = docs[1]

    m1 = doc1.metadata

    m2 = doc2.metadata

    response = []

    response.append(

        f"{m1.get('name')} vs "
        f"{m2.get('name')}\n"
    )

    response.append(
        "Key Differences:\n"
    )

    # ========================================================
    # CATEGORIES
    # ========================================================

    response.append(

        f"- Categories:\n"

        f"  • {m1.get('name')}: "
        f"{', '.join(m1.get('categories', []))}\n"

        f"  • {m2.get('name')}: "
        f"{', '.join(m2.get('categories', []))}\n"
    )

    # ========================================================
    # DURATION
    # ========================================================

    response.append(

        f"- Duration:\n"

        f"  • {m1.get('name')}: "
        f"{m1.get('duration')}\n"

        f"  • {m2.get('name')}: "
        f"{m2.get('duration')}\n"
    )

    # ========================================================
    # JOB LEVELS
    # ========================================================

    response.append(

        f"- Target Levels:\n"

        f"  • {m1.get('name')}: "
        f"{', '.join(m1.get('job_levels', []))}\n"

        f"  • {m2.get('name')}: "
        f"{', '.join(m2.get('job_levels', []))}\n"
    )

    # ========================================================
    # URLS
    # ========================================================

    response.append(

        f"- URLs:\n"

        f"  • {m1.get('url')}\n"

        f"  • {m2.get('url')}\n"
    )

    return "\n".join(response)