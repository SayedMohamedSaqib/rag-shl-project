from agent.ontology import (
    get_ontology_metadata,
)


# ============================================================
# ENRICH RESULTS
# ============================================================

def enrich_assessment_relationships(results):

    enriched = []

    for result in results:

        doc = result.get(
            "document",
            result
        )

        metadata = doc.metadata

        name = metadata.get(
            "name",
            ""
        )

        ontology = (
            get_ontology_metadata(
                name
            )
        )

        # ====================================================
        # ONTOLOGY METADATA
        # ====================================================

        metadata[
            "ontology"
        ] = ontology

        # ====================================================
        # RELATIONSHIP INFO
        # ====================================================

        metadata[
            "relationship_info"
        ] = {

            "entity_type": ontology.get(
                "entity_type"
            ),

            "assessment_family": ontology.get(
                "assessment_family"
            ),

            "requires_parent": ontology.get(
                "requires_parent",
                False
            ),

            "derived_from": ontology.get(
                "derived_from"
            ),

            "is_foundational": ontology.get(
                "is_foundational",
                False
            ),
        }

        enriched.append(result)

    return enriched