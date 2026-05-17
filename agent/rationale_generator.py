# ============================================================
# GENERATE RATIONALE
# ============================================================

def generate_recommendation_rationale(
    result,
    state,
    archetype,
):

    doc = result.get(
        "document",
        result
    )

    metadata = doc.metadata

    name = metadata.get(
        "name",
        ""
    )

    categories = metadata.get(
        "categories",
        []
    )

    test_type = metadata.get(
        "test_type",
        ""
    )

    role = state.get(
        "role",
        "the role"
    )

    seniority = state.get(
        "seniority"
    )

    # ========================================================
    # COGNITIVE
    # ========================================================

    if "A" in str(test_type):

        if seniority in [

            "senior",

            "lead",

            "principal",

            "executive",
        ]:

            return (
                f"{name} helps evaluate "
                f"reasoning ability and "
                f"problem-solving capability "
                f"for complex decision-making "
                f"in {role} positions."
            )

        return (
            f"{name} measures cognitive "
            f"ability and learning agility "
            f"relevant for success in "
            f"{role} roles."
        )

    # ========================================================
    # PERSONALITY
    # ========================================================

    if "P" in str(test_type):

        return (
            f"{name} evaluates workplace "
            f"behavioral tendencies and "
            f"personality traits relevant "
            f"to success in {role}."
        )

    # ========================================================
    # SIMULATION
    # ========================================================

    if "S" in str(test_type):

        return (
            f"{name} provides a practical "
            f"simulation-based measure of "
            f"real-world performance for "
            f"{role} candidates."
        )

    # ========================================================
    # TECHNICAL
    # ========================================================

    if any(

        "Knowledge" in str(cat)

        for cat in categories
    ):

        return (
            f"{name} validates critical "
            f"technical skills required "
            f"for {role} responsibilities."
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    return (
        f"{name} is relevant for "
        f"evaluating suitability for "
        f"{role}."
    )