def rerank_results(

    results,

    intent,

    bucket_type=None
):

    reranked = []

    role = (

        intent.role.lower()

        if intent.role else ""
    )

    technical_skills = [

        skill.lower()

        for skill in intent.technical_skills
    ]

    behavioral_traits = [

        trait.lower()

        for trait in intent.behavioral_traits
    ]

    # ========================================================
    # ROLE GROUPS
    # ========================================================

    engineering_roles = [

        "developer",

        "engineer",

        "backend",

        "frontend",

        "software",

        "java",

        "python",

        "full stack",
    ]

    leadership_roles = [

        "manager",

        "director",

        "lead",

        "executive",

        "vp",

        "cxo",
    ]

    sales_roles = [

        "sales",

        "account",

        "business development",

        "customer success",
    ]

    # ========================================================
    # MAIN LOOP
    # ========================================================

    for result in results:

        doc = result["document"]

        base_score = result["score"]

        metadata = doc.metadata

        ontology = metadata.get(
            "ontology",
            {}
        )

        name = metadata.get(
            "name",
            ""
        ).lower()

        categories = [

            c.lower()

            for c in metadata.get(
                "categories",
                []
            )
        ]

        text = (
            doc.page_content.lower()
        )

        boost = 0.0

        # ====================================================
        # ONTOLOGY BOOSTS
        # ====================================================

        if ontology:

            dimensions = ontology.get(
                "dimensions",
                []
            )

            role_alignment = ontology.get(
                "role_alignment",
                []
            )

            # =================================================
            # DIMENSION MATCH
            # =================================================

            if bucket_type in dimensions:

                boost += 0.15

            # =================================================
            # ENGINEERING ALIGNMENT
            # =================================================

            if any(

                term in role

                for term in engineering_roles
            ):

                if (
                    "engineering"
                    in role_alignment
                ):

                    boost += 0.10

            # =================================================
            # LEADERSHIP ALIGNMENT
            # =================================================

            if any(

                term in role

                for term in leadership_roles
            ):

                if (
                    "leadership"
                    in role_alignment
                ):

                    boost += 0.10

        # ====================================================
        # TECHNICAL BUCKET
        # ====================================================

        if bucket_type == "technical":

            if (
                "knowledge & skills"
                in categories
            ):

                boost += 0.05

            for skill in technical_skills:

                if skill in name:

                    boost += 0.10

                if skill in text:

                    boost += 0.05

        # ====================================================
        # COGNITIVE BUCKET
        # ====================================================

        if bucket_type == "cognitive":

            if (
                "ability & aptitude"
                in categories
            ):

                boost += 0.10

            if "deductive" in name:

                boost += 0.08

            if "inductive" in name:

                boost += 0.08

        # ====================================================
        # PERSONALITY BUCKET
        # ====================================================

        if bucket_type == "personality":

            if (
                "personality & behavior"
                in categories
            ):

                boost += 0.10

            if ontology.get(
                "assessment_family"
            ) == "OPQ":

                boost += 0.08

        # ====================================================
        # BEHAVIORAL BUCKET
        # ====================================================

        if bucket_type == "behavioral":

            if (
                "personality & behavior"
                in categories
            ):

                boost += 0.08

            if "communication" in text:

                boost += 0.05

            if "collaboration" in text:

                boost += 0.05

        # ====================================================
        # PENALTIES
        # ====================================================

        irrelevant_terms = [

            "spanish",

            "excel",

            "typing",

            "administration",
        ]

        for term in irrelevant_terms:

            if term in name:

                boost -= 0.10

        # ====================================================
        # FINAL SCORE
        # ====================================================

        final_score = (
            base_score + boost
        )

        reranked.append({

            "document": doc,

            "score": round(
                final_score,
                6
            )
        })

    # ========================================================
    # SORT
    # ========================================================

    reranked = sorted(

        reranked,

        key=lambda x: x["score"],

        reverse=True
    )

    return reranked