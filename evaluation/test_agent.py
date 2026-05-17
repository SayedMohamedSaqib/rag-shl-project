import sys
import os

from pathlib import Path

from huggingface_hub import login

login(token=os.getenv("HF_TOKEN"))

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# ============================================================
# RETRIEVAL
# ============================================================

from retrieval.embeddings import (
    load_embeddings
)

from retrieval.vector_store import (
    load_vector_store
)

from retrieval.semantic_retriever import (
    build_semantic_retriever
)

from retrieval.retrieval_pipeline import (
    RetrievalPipeline
)

from langchain_community.retrievers import (
    BM25Retriever
)

# ============================================================
# AGENT
# ============================================================

from agent.decision_engine import (
    decide_next_action
)

from agent.response_generator import (
    build_retrieval_response
)

# ============================================================
# LOAD DOCS
# ============================================================

def load_docs(vector_store):

    collection = vector_store._collection

    data = collection.get()

    docs = []

    from langchain_core.documents import (
        Document
    )

    for doc, metadata in zip(

        data["documents"],

        data["metadatas"]
    ):

        docs.append(

            Document(

                page_content=doc,

                metadata=metadata
            )
        )

    return docs


# ============================================================
# MAIN
# ============================================================

def main():

    print("\nLoading embeddings...")

    embeddings = load_embeddings()

    print("Embeddings loaded")

    # ========================================================
    # VECTOR STORE
    # ========================================================

    print("\nLoading vector store...")

    vector_store = load_vector_store(
        embeddings
    )

    print("Vector store loaded")

    # ========================================================
    # SEMANTIC RETRIEVER
    # ========================================================

    semantic_retriever = (
        build_semantic_retriever(
            vector_store
        )
    )

    # ========================================================
    # DOCS
    # ========================================================

    docs = load_docs(vector_store)

    # ========================================================
    # BM25
    # ========================================================

    bm25_retriever = (
        BM25Retriever.from_documents(
            docs
        )
    )

    bm25_retriever.k = 20

    # ========================================================
    # PIPELINE
    # ========================================================

    retrieval_pipeline = RetrievalPipeline(

        semantic_retriever=
            semantic_retriever,

        bm25_retriever=
            bm25_retriever
    )

    # ========================================================
    # CONVERSATION LOOP
    # ========================================================

    messages = []

    print("\nAgent Ready")

    print(
        "\nType 'exit' to quit.\n"
    )

    while True:

        user_input = input(
            "User: "
        )

        if user_input.lower() == "exit":

            break

        # ====================================================
        # APPEND USER MESSAGE
        # ====================================================

        messages.append({

            "role": "user",

            "content": user_input
        })

        # ====================================================
        # DECISION ENGINE
        # ====================================================

        decision = decide_next_action(
            messages
        )

        print("\nDecision:\n")

        print(decision)

        action = decision["action"]

        # ====================================================
        # CLARIFY
        # ====================================================

        if action == "clarify":

            assistant_reply = (
                decision["reply"]
            )

            print(
                f"\nAssistant: "
                f"{assistant_reply}\n"
            )

            messages.append({

                "role": "assistant",

                "content":
                    assistant_reply
            })

            continue

        # ====================================================
        # REFUSE
        # ====================================================

        if action == "refuse":

            assistant_reply = (
                decision["reply"]
            )

            print(
                f"\nAssistant: "
                f"{assistant_reply}\n"
            )

            messages.append({

                "role": "assistant",

                "content":
                    assistant_reply
            })

            continue

        # ====================================================
        # RETRIEVE
        # ====================================================

        if action == "retrieve":

            results = (
                retrieval_pipeline.run(
                    messages
                )
            )

            response = (
                build_retrieval_response(

                    state=decision["state"],

                    results=results,

                    messages=messages,
                )
            )

            # =================================================
            # INTRO
            # =================================================

            assistant_reply = (
                response["reply"]
            )

            print(
                f"\nAssistant:\n"
            )

            print(
                assistant_reply
            )

            # =================================================
            # WORKFLOW GUIDANCE
            # =================================================

            workflow_guidance = response.get(
                "workflow_guidance",
                []
            )

            if workflow_guidance:

                print(
                    "\n" + "=" * 80
                )

                print(
                    "WORKFLOW GUIDANCE"
                )

                print(
                    "=" * 80
                )

                for guidance in workflow_guidance:

                    print(
                        f"\n- {guidance}"
                    )

            # =================================================
            # RECOMMENDATIONS
            # =================================================

            print(
                "\n" + "=" * 80
            )

            print(
                "RECOMMENDATIONS"
            )

            print(
                "=" * 80
            )

            for rec in response[
                "recommendations"
            ]:

                print(
                    f"\n- {rec['name']}"
                )

                print(
                    f"  URL: "
                    f"{rec['url']}"
                )

                print(
                    f"  Type: "
                    f"{rec['test_type']}"
                )

                categories = rec.get(
                    "categories",
                    []
                )

                if categories:

                    print(
                        f"  Categories: "
                        f"{categories}"
                    )

                # =============================================
                # RATIONALE
                # =============================================

                rationale = rec.get(
                    "rationale"
                )

                if rationale:

                    print(
                        f"  Why: "
                        f"{rationale}"
                    )

                # =============================================
                # RELATIONSHIPS
                # =============================================

                relationship_info = rec.get(
                    "relationship_info",
                    {}
                )

                if relationship_info:

                    note = relationship_info.get(
                        "relationship_note"
                    )

                    if note:

                        print(
                            f"  Note: "
                            f"{note}"
                        )

            print()

            messages.append({

                "role": "assistant",

                "content":
                    assistant_reply
            })

            continue

        # ====================================================
        # COMPARE
        # ====================================================

        if action == "compare":

            print(

                "\nComparison "
                "mode not fully "
                "implemented yet.\n"
            )

            continue


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()