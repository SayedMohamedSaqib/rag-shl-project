SYSTEM_PROMPT = """
Expand recruiter hiring queries.

Generate:
- related skills
- synonyms
- behavioral equivalents
- hiring terminology
"""



def expand_query(intent):

    query_parts = []

    # ========================================================
    # ROLE
    # ========================================================

    if intent.role:

        query_parts.append(
            intent.role
        )

    # ========================================================
    # TECHNICAL SKILLS
    # ========================================================

    if intent.technical_skills:

        query_parts.extend(
            intent.technical_skills
        )

    # ========================================================
    # BEHAVIORAL
    # ========================================================

    if intent.behavioral_traits:

        query_parts.extend(
            intent.behavioral_traits
        )

    # ========================================================
    # SENIORITY
    # ========================================================

    if intent.seniority:

        query_parts.append(
            intent.seniority
        )

    # ========================================================
    # PERSONALITY
    # ========================================================

    if intent.personality_required:

        query_parts.extend([

            "personality",

            "behavioral assessment",

            "teamwork",

            "communication"
        ])

    # ========================================================
    # COGNITIVE
    # ========================================================

    if intent.cognitive_required:

        query_parts.extend([

            "cognitive ability",

            "aptitude",

            "logical reasoning"
        ])

    # ========================================================
    # FINAL QUERY
    # ========================================================

    expanded_query = " ".join(
        query_parts
    )

    return {

        "expanded_query": expanded_query,

        "keywords": query_parts,

        "behavioral_terms": (
            intent.behavioral_traits
        )
    }