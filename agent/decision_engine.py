from agent.conversation_state import (
    build_conversation_state,
)

from agent.llm_decision import (
    llm_decide,
)


# ============================================================
# OFF-TOPIC DETECTION
# ============================================================

OFF_TOPIC_KEYWORDS = [

    "weather",

    "politics",

    "medical",

    "legal",

    "recipe",

    "travel",

    "sports",

    "movie",
]


# ============================================================
# OFF-TOPIC
# ============================================================

def is_off_topic(text):

    text = text.lower()

    return any(

        keyword in text

        for keyword in OFF_TOPIC_KEYWORDS
    )


# ============================================================
# DECISION ENGINE
# ============================================================

def decide_next_action(messages):

    latest_user_message = (
        messages[-1]["content"]
    )

    # ========================================================
    # OFF TOPIC
    # ========================================================

    if is_off_topic(
        latest_user_message
    ):

        return {

            "action": "refuse",

            "reply": (
                "I can only help with "
                "SHL assessment "
                "recommendations and "
                "comparisons."
            ),

            "end_of_conversation": False,
        }

    # ========================================================
    # BUILD STATE
    # ========================================================

    state = build_conversation_state(
        messages
    )

    print("\nConversation State:\n")

    print(state)

    # ========================================================
    # LLM DECISION
    # ========================================================

    decision = llm_decide(
        messages,
        state,
    )

    print("\nLLM Decision:\n")

    print(decision)

    action = decision.get(
        "action",
        "clarify",
    )

    # ========================================================
    # CLARIFY
    # ========================================================

    if action == "clarify":

        return {

            "action": "clarify",

            "reply": decision.get(
                "reply",
                "Could you share more details?",
            ),

            "end_of_conversation": False,
        }

    # ========================================================
    # REFUSE
    # ========================================================

    if action == "refuse":

        refusal_reply = decision.get(
            "reply",
            ""
        ).lower()

        # ====================================================
        # CONFLICT / AMBIGUITY RECOVERY
        # ====================================================

        ambiguity_terms = [

            "confusion",

            "conflicting",

            "clarify",

            "which role",

            "unclear",
        ]

        if any(

            term in refusal_reply

            for term in ambiguity_terms
        ):

            return {

                "action": "clarify",

                "reply": decision.get(
                    "reply",
                    "Could you clarify the role?"
                ),

                "end_of_conversation": False,
            }

        # ====================================================
        # TRUE REFUSAL
        # ====================================================

        return {

            "action": "refuse",

            "reply": decision.get(
                "reply",
                "I can only help with SHL assessments.",
            ),

            "end_of_conversation": False,
        }

    # ========================================================
    # COMPARE
    # ========================================================

    if action == "compare":

        return {
            "action": "compare"
        }

    # ========================================================
    # RETRIEVE SAFETY CHECK
    # ========================================================

    reply_text = decision.get(
        "reply",
        ""
    ).lower()

    # Only force clarify if the model is
    # explicitly requesting missing info.

    strong_clarification_markers = [

        "could you please provide",

        "please provide",

        "please specify",

        "please clarify",

        "what role",

        "which role",

        "what seniority",

        "which seniority",

        "what skills",

        "which skills",
    ]

    if any(

        marker in reply_text

        for marker in strong_clarification_markers
    ):

        return {

            "action": "clarify",

            "reply": decision.get(
                "reply",
                "Could you share more details?"
            ),

            "end_of_conversation": False,
        }

    # ========================================================
    # TRUE RETRIEVE
    # ========================================================

    return {

        "action": "retrieve",

        "state": state,
    }