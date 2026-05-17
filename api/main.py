from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ChatRequest,
    ChatResponse,
    Recommendation,
)

from retrieval.vector_store import (
    get_vector_store,
)

from retrieval.semantic_retriever import (
    build_semantic_retriever,
)

from retrieval.retrieval_pipeline import (
    RetrievalPipeline,
)

from retrieval.bm25_store import (
    get_bm25_retriever,
)

from agent.decision_engine import (
    decide_next_action,
)

from agent.response_generator import (
    build_retrieval_response,
)

# ========================================================
# FASTAPI
# ========================================================

app = FastAPI(
    title="SHL Assessment Recommendation Agent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("\nAPI Ready")


# ========================================================
# HEALTH ENDPOINT
# ========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ========================================================
# CHAT ENDPOINT
# ========================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    # ====================================================
    # CONVERT PYDANTIC OBJECTS
    # ====================================================

    messages = [

        {
            "role": msg.role,
            "content": msg.content,
        }

        for msg in request.messages
    ]

    # ====================================================
    # DECISION ENGINE
    # ====================================================

    decision = decide_next_action(
        messages
    )

    print("\nDecision:\n")

    print(decision)

    action = decision.get(
        "action"
    )

    # ====================================================
    # CLARIFY
    # ====================================================

    if action == "clarify":

        return ChatResponse(

            reply=decision["reply"],

            recommendations=[],

            end_of_conversation=False,
        )

    # ====================================================
    # REFUSE
    # ====================================================

    if action == "refuse":

        return ChatResponse(

            reply=decision["reply"],

            recommendations=[],

            end_of_conversation=True,
        )

    # ====================================================
    # RETRIEVE
    # ====================================================

    if action == "retrieve":

        # ================================================
        # VECTOR STORE
        # ================================================

        vector_store = get_vector_store()

        # ================================================
        # SEMANTIC RETRIEVER
        # ================================================

        semantic_retriever = (
            build_semantic_retriever(
                vector_store
            )
        )

        # ================================================
        # BM25 RETRIEVER
        # ================================================

        bm25_retriever = (
            get_bm25_retriever()
        )

        # ================================================
        # PIPELINE
        # ================================================

        pipeline = RetrievalPipeline(
            semantic_retriever=semantic_retriever,
            bm25_retriever=bm25_retriever,
        )

        results = pipeline.run(
            messages
        )

        response = (
            build_retrieval_response(

                state=decision[
                    "state"
                ],

                results=results,

                messages=messages,
            )
        )

        recommendations = []

        for rec in response[
            "recommendations"
        ]:

            recommendations.append(

                Recommendation(

                    name=rec[
                        "name"
                    ],

                    url=rec[
                        "url"
                    ],

                    test_type=rec.get(
                        "test_type",
                        "Unknown",
                    ),
                )
            )

        return ChatResponse(

            reply=response[
                "reply"
            ],

            recommendations=
                recommendations,

            end_of_conversation=True,
        )

    # ====================================================
    # COMPARE
    # ====================================================

    if action == "compare":

        return ChatResponse(

            reply=decision.get(
                "reply",
                "Comparison mode is not implemented yet.",
            ),

            recommendations=[],

            end_of_conversation=True,
        )

    # ====================================================
    # FALLBACK
    # ====================================================

    return ChatResponse(

        reply=(
            "I could not process your request."
        ),

        recommendations=[],

        end_of_conversation=False,
    )