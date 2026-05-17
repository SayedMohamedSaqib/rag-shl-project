from agent.assessment_composer import (
    compose_assessment_recommendation,
)


# ============================================================
# BUILD RETRIEVAL RESPONSE
# ============================================================

def build_retrieval_response(
    state,
    results,
    messages,
):

    composed = (
        compose_assessment_recommendation(
            state=state,
            results=results,
            messages=messages,
        )
    )

    recommendations = []

    for item in composed[
        "recommendations"
    ]:

        result = item[
            "assessment"
        ]

        rationale = item[
            "rationale"
        ]

        doc = result.get(
            "document",
            result
        )

        metadata = doc.metadata

        recommendations.append({

            "name": metadata.get(
                "name",
                "Unknown Assessment"
            ),

            "url": metadata.get(
                "url",
                ""
            ),

            "test_type": (

                metadata.get("test_type")

                or metadata.get("assessment_type")

                or metadata.get("type")

                or metadata.get("testType")

                or "Unknown"
            ),

            "categories": metadata.get(
                "categories",
                []
            ),

            "relationship_info": metadata.get(
                "relationship_info",
                {}
            ),

            "rationale": rationale,
        })

    return {

        "reply": composed.get(
            "intro",
            "Here are recommended SHL assessments."
        ),

        "workflow_guidance": composed.get(
            "workflow_guidance",
            []
        ),

        "recommendations": recommendations,
    }