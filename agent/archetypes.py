ROLE_ARCHETYPES = {

    # ========================================================
    # ENGINEERING
    # ========================================================

    "engineering": {

        "keywords": [

            "engineer",

            "developer",

            "backend",

            "frontend",

            "software",

            "java",

            "python",

            "full stack",
        ],

        "recommended_dimensions": {

            "technical": True,

            "cognitive": True,

            "personality": False,
        }
    },

    # ========================================================
    # LEADERSHIP
    # ========================================================

    "leadership": {

        "keywords": [

            "manager",

            "director",

            "lead",

            "executive",

            "vp",

            "cxo",
        ],

        "recommended_dimensions": {

            "technical": False,

            "cognitive": True,

            "personality": True,
        }
    },

    # ========================================================
    # SALES
    # ========================================================

    "sales": {

        "keywords": [

            "sales",

            "account",

            "business development",

            "customer success",
        ],

        "recommended_dimensions": {

            "technical": False,

            "cognitive": False,

            "personality": True,
        }
    },
}


# ============================================================
# DETECT ARCHETYPE
# ============================================================

def detect_role_archetype(state):

    role = (

        state.get(
            "role",
            ""
        )
        .lower()
    )

    for archetype_name, config in (

        ROLE_ARCHETYPES.items()
    ):

        keywords = config.get(
            "keywords",
            []
        )

        if any(

            keyword in role

            for keyword in keywords
        ):

            return {

                "name": archetype_name,

                "recommended_dimensions": (
                    config[
                        "recommended_dimensions"
                    ]
                ),
            }

    # ========================================================
    # FALLBACK
    # ========================================================

    return {

        "name": "general",

        "recommended_dimensions": {

            "technical": False,

            "cognitive": True,

            "personality": False,
        }
    }