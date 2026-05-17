from types import (
    SimpleNamespace,
)

from agent.conversation_state import (
    build_conversation_state,
)

from retrieval.query_expander import (
    expand_query,
)

from retrieval.rrf import (
    reciprocal_rank_fusion,
)

from retrieval.reranker import (
    rerank_results,
)

from retrieval.bucket_retriever import (
    split_intent_into_buckets,
)


class RetrievalPipeline:

    def __init__(
        self,
        semantic_retriever,
        bm25_retriever,
    ):

        self.semantic_retriever = (
            semantic_retriever
        )

        self.bm25_retriever = (
            bm25_retriever
        )

    def run(self, messages):

        # ====================================================
        # 1. BUILD CONVERSATION STATE
        # ====================================================

        intent = SimpleNamespace(

            **build_conversation_state(
                messages
            )
        )

        print("\nIntent:\n")

        print(intent)

        # ====================================================
        # 2. QUERY EXPANSION
        # ====================================================

        expanded = expand_query(
            intent
        )

        print("\nExpanded Query:\n")

        print(expanded)

        # ====================================================
        # 3. SPLIT INTO BUCKETS
        # ====================================================

        buckets = split_intent_into_buckets(
            intent
        )

        print("\nBuckets:\n")

        for bucket in buckets:

            print(bucket)

        # ====================================================
        # 4. RETRIEVE PER BUCKET
        # ====================================================

        all_results = []

        for bucket in buckets:

            query = bucket["query"]

            print(
                f"\nRunning bucket: "
                f"{bucket['type']}"
            )

            print(
                f"Query: {query}"
            )

            # ================================================
            # SEMANTIC RETRIEVAL
            # ================================================

            semantic_results = (

                self.semantic_retriever.invoke(
                    query
                )
            )

            print(
                f"Semantic Results: "
                f"{len(semantic_results)}"
            )

            # ================================================
            # BM25 RETRIEVAL
            # ================================================

            bm25_results = (

                self.bm25_retriever.invoke(
                    query
                )
            )

            print(
                f"BM25 Results: "
                f"{len(bm25_results)}"
            )

            # ================================================
            # RRF MERGE
            # ================================================

            merged = reciprocal_rank_fusion(

                [
                    semantic_results,
                    bm25_results,
                ]
            )

            # ================================================
            # RERANK
            # ================================================

            reranked = rerank_results(

                merged,
                intent,
                bucket["type"]
            )

            # ================================================
            # KEEP TOP RESULTS PER BUCKET
            # ================================================

            all_results.extend(
                reranked[:5]
            )

        # ====================================================
        # 5. GLOBAL DEDUP
        # ====================================================

        seen = set()

        final_results = []

        for result in all_results:

            doc_id = result[
                "document"
            ].metadata.get("id")

            if doc_id not in seen:

                seen.add(doc_id)

                final_results.append(
                    result
                )

        # ====================================================
        # 6. FINAL SORT
        # ====================================================

        final_results = sorted(

            final_results,

            key=lambda x: x["score"],

            reverse=True
        )

        print(
            f"\nFinal Results: "
            f"{len(final_results)}"
        )

        return final_results[:10]