from retrieval.constraint_extractor import (
    extract_constraints,
)


# ============================================================
# MERGE LISTS
# ============================================================

def merge_lists(old, new):

    merged = []

    seen = set()

    for item in old + new:

        normalized = str(
            item
        ).lower()

        if normalized not in seen:

            seen.add(normalized)

            merged.append(item)

    return merged


# ============================================================
# BUILD CONVERSATION STATE
# ============================================================

def build_conversation_state(messages):

    """
    Reconstruct recruiter intent
    from full conversation history.

    Since API is stateless,
    we derive state every request.
    """

    state = {

        "role": None,

        "technical_skills": [],

        "behavioral_traits": [],

        "seniority": None,

        "cognitive_required": False,

        "personality_required": False,

        "assessment_preferences": [],

        "constraints": [],
    }

    # ========================================================
    # PROCESS USER MESSAGES ONLY
    # ========================================================

    user_messages = [

        msg

        for msg in messages

        if msg["role"] == "user"
    ]

    # ========================================================
    # EXTRACT CONSTRAINTS TURN-BY-TURN
    # ========================================================

    for msg in user_messages:

        extracted = extract_constraints(
            [msg]
        )

        message_text = msg[
            "content"
        ].lower()

        # ====================================================
        # ROLE
        # ====================================================

        if extracted.role:

            state["role"] = (
                extracted.role
            )

        # ====================================================
        # SENIORITY
        # ====================================================

        if extracted.seniority:

            state["seniority"] = (
                extracted.seniority
            )

        # ====================================================
        # TECHNICAL SKILLS
        # ====================================================

        state["technical_skills"] = (

            merge_lists(

                state[
                    "technical_skills"
                ],

                extracted.technical_skills
            )
        )

        # ====================================================
        # BEHAVIORAL TRAITS
        # ====================================================

        state["behavioral_traits"] = (

            merge_lists(

                state[
                    "behavioral_traits"
                ],

                extracted.behavioral_traits
            )
        )

        # ====================================================
        # ASSESSMENT PREFERENCES
        # ====================================================

        state[
            "assessment_preferences"
        ] = merge_lists(

            state[
                "assessment_preferences"
            ],

            extracted.assessment_preferences
        )

        # ====================================================
        # CONSTRAINTS
        # ====================================================

        state["constraints"] = merge_lists(

            state["constraints"],

            extracted.constraints
        )

        # ====================================================
        # BOOLEAN FLAGS
        # ====================================================

        if extracted.cognitive_required:

            state[
                "cognitive_required"
            ] = True

        if extracted.personality_required:

            state[
                "personality_required"
            ] = True

        # ====================================================
        # RULE-BASED OVERRIDES
        # ====================================================

        # ----------------------------------------------------
        # DROP PERSONALITY
        # ----------------------------------------------------

        if any(

            phrase in message_text

            for phrase in [

                "drop personality",

                "remove personality",

                "no personality",

                "without personality",
            ]
        ):

            state[
                "personality_required"
            ] = False

            state[
                "assessment_preferences"
            ] = [

                pref

                for pref in state[
                    "assessment_preferences"
                ]

                if pref.lower() != "personality"
            ]

        # ----------------------------------------------------
        # COGNITIVE REQUESTS
        # ----------------------------------------------------

        if any(

            phrase in message_text

            for phrase in [

                "add cognitive",

                "keep cognitive",

                "include cognitive",

                "cognitive only",

                "technical plus cognitive",
            ]
        ):

            state[
                "cognitive_required"
            ] = True

            state[
                "assessment_preferences"
            ] = merge_lists(

                state[
                    "assessment_preferences"
                ],

                ["cognitive"]
            )

        # ----------------------------------------------------
        # TECHNICAL REQUESTS
        # ----------------------------------------------------

        if any(

            phrase in message_text

            for phrase in [

                "technical only",

                "keep technical",

                "technical plus cognitive",

                "only technical",
            ]
        ):

            state[
                "assessment_preferences"
            ] = merge_lists(

                state[
                    "assessment_preferences"
                ],

                ["technical"]
            )

        # ----------------------------------------------------
        # PERSONALITY REQUESTS
        # ----------------------------------------------------

        if any(

            phrase in message_text

            for phrase in [

                "add personality",

                "include personality",

                "keep personality",
            ]
        ):

            state[
                "personality_required"
            ] = True

            state[
                "assessment_preferences"
            ] = merge_lists(

                state[
                    "assessment_preferences"
                ],

                ["personality"]
            )

    return state