from retrieval.config import (
    SEMANTIC_WEIGHT,
    KEYWORD_WEIGHT
)



def hybrid_search(
    semantic_results,
    bm25_results
):

    """
    Combine semantic + keyword retrieval.
    """

    return {
        "semantic": semantic_results,
        "bm25": bm25_results
    }