from agent.archetypes import (
    detect_role_archetype,
)

from agent.product_graph import (
    enrich_assessment_relationships,
)

from agent.rationale_generator import (
    generate_recommendation_rationale,
)

from agent.workflow_reasoner import (
    detect_workflow_flags,
    generate_workflow_guidance,
)


# ============================================================
# DEDUP
# ============================================================

def deduplicate_results(results):

    seen = set()

    final = []

    for result in results:

        doc = result.get(
            "document",
            result
        )

        name = doc.metadata.get(
            "name",
            ""
        )

        normalized = (
            str(name)
            .lower()
            .strip()
        )

        if normalized in seen:

            continue

        seen.add(normalized)

        final.append(result)

    return final


# ============================================================
# GROUP RESULTS
# ============================================================

def group_results(results):

    grouped = {

        "cognitive": [],

        "personality": [],

        "technical": [],

        "simulation": [],

        "other": [],
    }

    for result in results:

        doc = result.get(
            "document",
            result
        )

        metadata = doc.metadata


        categories_text = str(
            metadata.get("categories", "")
        ).lower()

        # ====================================================
        # TECHNICAL
        # ====================================================

        if any(

            keyword in categories_text

            for keyword in [

                "knowledge",

                "skills",
            ]
        ):

            grouped[
                "technical"
            ].append(result)

        # ====================================================
        # COGNITIVE
        # ====================================================

        elif any(

            keyword in categories_text

            for keyword in [

                "ability",

                "aptitude",

                "reasoning",
            ]
        ):

            grouped[
                "cognitive"
            ].append(result)

        # ====================================================
        # PERSONALITY
        # ====================================================

        elif any(

            keyword in categories_text

            for keyword in [

                "personality",

                "behavior",
            ]
        ):

            grouped[
                "personality"
            ].append(result)

        # ====================================================
        # SIMULATION
        # ====================================================

        elif any(

            keyword in categories_text

            for keyword in [

                "simulation",
            ]
        ):

            grouped[
                "simulation"
            ].append(result)

        # ====================================================
        # OTHER
        # ====================================================

        else:

            grouped[
                "other"
            ].append(result)

    return grouped


# ============================================================
# DEDUP BATTERY
# ============================================================

def deduplicate_battery(results):

    final = []

    seen = set()

    for result in results:

        doc = result.get(
            "document",
            result
        )

        name = doc.metadata.get(
            "name",
            ""
        )

        normalized = (
            str(name)
            .lower()
            .strip()
        )

        if normalized in seen:

            continue

        seen.add(normalized)

        final.append(result)

    return final


# ============================================================
# COMPOSE RESPONSE
# ============================================================

def compose_assessment_recommendation(
    state,
    results,
    messages,
):

    # ========================================================
    # ARCHETYPE
    # ========================================================

    archetype = detect_role_archetype(
        state
    )

    # ========================================================
    # WORKFLOW FLAGS
    # ========================================================

    workflow_flags = (
        detect_workflow_flags(
            messages
        )
    )

    workflow_guidance = (
        generate_workflow_guidance(
            workflow_flags
        )
    )

    # ========================================================
    # DEDUP RESULTS
    # ========================================================

    results = deduplicate_results(
        results
    )

    # ========================================================
    # ENRICH
    # ========================================================

    enriched = (
        enrich_assessment_relationships(
            results
        )
    )

    # ========================================================
    # GROUP
    # ========================================================

    grouped = group_results(
        enriched
    )

    # ========================================================
    # DIMENSIONS
    # ========================================================

    recommended_dimensions = {

        "technical": False,

        "cognitive": False,

        "personality": False,
    }

    # ========================================================
    # ROLE-BASED DEFAULTS
    # ========================================================

    role_defaults = archetype.get(
        "recommended_dimensions",
        {}
    )

    recommended_dimensions.update(
        role_defaults
    )

    # ========================================================
    # EXPLICIT USER FLAGS
    # ========================================================

    if state.get(
        "cognitive_required"
    ):

        recommended_dimensions[
            "cognitive"
        ] = True

    if state.get(
        "personality_required"
    ):

        recommended_dimensions[
            "personality"
        ] = True

    # ========================================================
    # TECHNICAL AUTO ENABLE
    # ========================================================

    if state.get(
        "technical_skills"
    ):

        recommended_dimensions[
            "technical"
        ] = True

    # ========================================================
    # BUILD BATTERY
    # ========================================================

    battery = []

    # ========================================================
    # TECHNICAL
    # ========================================================

    if recommended_dimensions.get(
        "technical"
    ):

        battery.extend(
            grouped["technical"][:5]
        )

    # ========================================================
    # COGNITIVE
    # ========================================================

    if recommended_dimensions.get(
        "cognitive"
    ):

        battery.extend(
            grouped["cognitive"][:3]
        )

    # ========================================================
    # PERSONALITY
    # ========================================================

    if recommended_dimensions.get(
        "personality"
    ):

        battery.extend(
            grouped["personality"][:3]
        )

    # ========================================================
    # SIMULATIONS
    # ========================================================

    if workflow_flags.get(
        "finalist_stage"
    ):

        battery.extend(
            grouped["simulation"][:2]
        )

    # ========================================================
    # FINAL DEDUP
    # ========================================================

    final_battery = (
        deduplicate_battery(
            battery
        )
    )

    # ========================================================
    # LIMIT
    # ========================================================

    MAX_RESULTS = 10

    final_battery = (
        final_battery[:MAX_RESULTS]
    )

    # ========================================================
    # BUILD RATIONALES
    # ========================================================

    recommendations = []

    for result in final_battery:

        rationale = (
            generate_recommendation_rationale(
                result=result,
                state=state,
                archetype=archetype,
            )
        )

        recommendations.append({

            "assessment": result,

            "rationale": rationale,
        })

    # ========================================================
    # INTRO
    # ========================================================

    role = state.get(
        "role",
        "this role"
    )

    dimension_names = [

        key

        for key, value in recommended_dimensions.items()

        if value
    ]

    if dimension_names:

        dimension_text = ", ".join(
            dimension_names
        )

    else:

        dimension_text = (
            "the most relevant hiring dimensions"
        )

    intro = (

        f"For {role}, I'd recommend "
        f"a balanced assessment battery "
        f"focused on {dimension_text}."
    )

    # ========================================================
    # FINAL
    # ========================================================

    return {

        "intro": intro,

        "workflow_guidance": (
            workflow_guidance or []
        ),

        "recommendations": (
            recommendations
        ),
    }
