ASSESSMENT_ONTOLOGY = {

    # ========================================================
    # FOUNDATIONAL PERSONALITY INSTRUMENT
    # ========================================================

    "Occupational Personality Questionnaire OPQ32r": {

        "entity_type": "instrument",

        "assessment_family": "OPQ",

        "dimensions": [
            "personality"
        ],

        "role_alignment": [
            "general"
        ],

        "seniority_fit": [
            "mid",
            "senior",
            "executive"
        ],

        "is_foundational": True,

        "requires_parent": False,

        "derived_from": None,
    },

    # ========================================================
    # LEADERSHIP REPORT
    # ========================================================

    "OPQ Leadership Report": {

        "entity_type": "report",

        "assessment_family": "OPQ",

        "dimensions": [
            "leadership"
        ],

        "role_alignment": [
            "leadership"
        ],

        "seniority_fit": [
            "senior",
            "executive"
        ],

        "is_foundational": False,

        "requires_parent": True,

        "derived_from": (
            "Occupational Personality "
            "Questionnaire OPQ32r"
        ),
    },

    # ========================================================
    # GENERAL PERSONALITY REPORT
    # ========================================================

    "OPQ Universal Competency Report 2.0": {

        "entity_type": "report",

        "assessment_family": "OPQ",

        "dimensions": [
            "personality"
        ],

        "role_alignment": [
            "general"
        ],

        "seniority_fit": [
            "mid",
            "senior",
            "executive"
        ],

        "is_foundational": False,

        "requires_parent": True,

        "derived_from": (
            "Occupational Personality "
            "Questionnaire OPQ32r"
        ),
    },

    # ========================================================
    # COGNITIVE
    # ========================================================

    "Verify - Inductive Reasoning (2014)": {

        "entity_type": "assessment",

        "assessment_family": "Verify",

        "dimensions": [
            "cognitive"
        ],

        "role_alignment": [
            "engineering",
            "general"
        ],

        "seniority_fit": [
            "entry",
            "mid",
            "senior"
        ],

        "is_foundational": True,

        "requires_parent": False,

        "derived_from": None,
    },

    "Verify - Deductive Reasoning": {

        "entity_type": "assessment",

        "assessment_family": "Verify",

        "dimensions": [
            "cognitive"
        ],

        "role_alignment": [
            "engineering",
            "general"
        ],

        "seniority_fit": [
            "entry",
            "mid",
            "senior"
        ],

        "is_foundational": True,

        "requires_parent": False,

        "derived_from": None,
    },
}


# ============================================================
# HELPERS
# ============================================================

def get_ontology_metadata(name):

    return ASSESSMENT_ONTOLOGY.get(
        name,
        {}
    )