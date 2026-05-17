from collections import defaultdict

from retrieval.config import RRF_K


def reciprocal_rank_fusion(result_sets):

    scores = defaultdict(float)

    documents = {}

    # ========================================================
    # ACCUMULATE SCORES
    # ========================================================

    for results in result_sets:

        for rank, doc in enumerate(results):

            doc_id = doc.metadata.get(
                "id"
            )

            documents[doc_id] = doc

            rrf_score = (

                1 / (RRF_K + rank + 1)
            )

            scores[doc_id] += rrf_score

    # ========================================================
    # SORT
    # ========================================================

    ranked = sorted(

        scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    # ========================================================
    # RETURN DOC + SCORE
    # ========================================================

    final_results = []

    for doc_id, score in ranked:

        doc = documents[doc_id]

        final_results.append({

            "document": doc,

            "score": round(score, 6)
        })

    return final_results