def split_intent_into_buckets(intent):

    buckets = []

    role = (

        intent.role.lower()

        if intent.role else ""
    )

    # ========================================================
    # TECHNICAL
    # ========================================================

    if intent.technical_skills:

        for skill in intent.technical_skills:

            buckets.append({

                "type": "technical",

                "query": skill
            })

    # ========================================================
    # BEHAVIORAL
    # ========================================================

    if intent.behavioral_traits:

        behavioral_query = " ".join(

            intent.behavioral_traits
        )

        behavioral_query += (

            " teamwork communication "
            "collaboration personality"
        )

        buckets.append({

            "type": "behavioral",

            "query": behavioral_query
        })

    # ========================================================
    # EXPLICIT COGNITIVE
    # ========================================================

    if intent.cognitive_required:

        buckets.append({

            "type": "cognitive",

            "query": (

                "cognitive aptitude "
                "logical reasoning "
                "problem solving"
            )
        })

    # ========================================================
    # EXPLICIT PERSONALITY
    # ========================================================

    if intent.personality_required:

        buckets.append({

            "type": "personality",

            "query": (

                "personality workplace "
                "behavior collaboration "
                "communication"
            )
        })

    # ========================================================
    # ROLE GROUPS
    # ========================================================

    engineering_terms = [

        "developer",

        "engineer",

        "backend",

        "frontend",

        "software",

        "java",

        "python",

        "full stack",
    ]

    leadership_terms = [

        "manager",

        "director",

        "lead",

        "executive",

        "vp",

        "cxo",
    ]

    sales_terms = [

        "sales",

        "account",

        "business development",

        "customer success",
    ]

    # ========================================================
    # ENGINEERING ROLES
    # ========================================================

    if any(

        term in role

        for term in engineering_terms
    ):

        # Only auto-add cognitive
        # if recruiter did NOT
        # explicitly ask for
        # personality-only.

        if (

            not intent.cognitive_required

            and not intent.personality_required
        ):

            buckets.append({

                "type": "cognitive",

                "query": (

                    "cognitive aptitude "
                    "logical reasoning "
                    "problem solving"
                )
            })

    # ========================================================
    # LEADERSHIP ROLES
    # ========================================================

    if any(

        term in role

        for term in leadership_terms
    ):

        # Auto-add personality
        # only if recruiter
        # did not explicitly
        # specify dimensions.

        if (

            not intent.personality_required

            and not intent.cognitive_required
        ):

            buckets.append({

                "type": "personality",

                "query": (

                    "leadership personality "
                    "behavioral assessment "
                    "executive communication"
                )
            })

    # ========================================================
    # SALES ROLES
    # ========================================================

    if any(

        term in role

        for term in sales_terms
    ):

        buckets.append({

            "type": "behavioral",

            "query": (

                "sales communication "
                "persuasion stakeholder "
                "relationship building"
            )
        })

    # ========================================================
    # DEDUP
    # ========================================================

    seen = set()

    deduped = []

    for bucket in buckets:

        key = (

            bucket["type"],

            bucket["query"]
        )

        if key not in seen:

            seen.add(key)

            deduped.append(bucket)

    return deduped