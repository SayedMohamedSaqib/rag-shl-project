# ============================================================
# DETECT WORKFLOW FLAGS
# ============================================================

def detect_workflow_flags(messages):

    text = " ".join([

        msg["content"]

        for msg in messages
    ]).lower()

    return {

        # ====================================================
        # HIRING SCALE
        # ====================================================

        "volume_hiring": any(

            phrase in text

            for phrase in [

                "high volume",

                "500 candidates",

                "mass hiring",

                "bulk hiring",

                "volume screening",
            ]
        ),

        # ====================================================
        # FINALIST STAGE
        # ====================================================

        "finalist_stage": any(

            phrase in text

            for phrase in [

                "finalist",

                "shortlisted",

                "final round",

                "later stage",
            ]
        ),

        # ====================================================
        # DEVELOPMENT USE CASE
        # ====================================================

        "development_context": any(

            phrase in text

            for phrase in [

                "development",

                "reskill",

                "upskill",

                "talent audit",

                "leadership development",
            ]
        ),

        # ====================================================
        # SELECTION USE CASE
        # ====================================================

        "selection_context": any(

            phrase in text

            for phrase in [

                "selection",

                "hiring",

                "recruiting",

                "screening",
            ]
        ),

        # ====================================================
        # TWO STAGE PROCESS
        # ====================================================

        "two_stage_hiring": any(

            phrase in text

            for phrase in [

                "first filter",

                "shortlisted candidates",

                "finalists",

                "second stage",

                "two-stage",
            ]
        ),
    }


# ============================================================
# WORKFLOW GUIDANCE
# ============================================================

def generate_workflow_guidance(flags):

    guidance = []

    # ========================================================
    # VOLUME HIRING
    # ========================================================

    if flags.get(
        "volume_hiring"
    ):

        guidance.append(

            "For high-volume hiring, consider "
            "using shorter assessments early "
            "in the funnel before deeper "
            "evaluation stages."
        )

    # ========================================================
    # TWO STAGE
    # ========================================================

    if flags.get(
        "two_stage_hiring"
    ):

        guidance.append(

            "A staged assessment workflow can "
            "improve efficiency by using "
            "cognitive or screening assessments "
            "early and simulations or deeper "
            "technical evaluations later."
        )

    # ========================================================
    # DEVELOPMENT
    # ========================================================

    if flags.get(
        "development_context"
    ):

        guidance.append(

            "Development-focused workflows "
            "benefit from personality and "
            "competency-based reports alongside "
            "skill measurement."
        )

    # ========================================================
    # FINALISTS
    # ========================================================

    if flags.get(
        "finalist_stage"
    ):

        guidance.append(

            "Simulation-based assessments are "
            "especially valuable during "
            "finalist-stage evaluation."
        )

    return guidance