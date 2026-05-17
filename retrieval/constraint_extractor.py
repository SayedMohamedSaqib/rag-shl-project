import json
import os

from openai import OpenAI

from dotenv import load_dotenv

from retrieval.schemas import RetrievalIntent


# ============================================================
# ENV
# ============================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


# ============================================================
# CLIENT
# ============================================================

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=OPENROUTER_API_KEY
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert hiring intent extraction engine.

Extract structured hiring constraints from recruiter conversations.

Return STRICT JSON ONLY.

Schema:

{
  "role": string | null,
  "technical_skills": list[string],
  "behavioral_traits": list[string],
  "seniority": string | null,
  "cognitive_required": boolean,
  "personality_required": boolean,
  "assessment_preferences": list[string],
  "constraints": list[string]
}

Rules:

- Only extract information explicitly mentioned.
- Do NOT infer missing recruiter intent.
- Do NOT hallucinate assessment preferences.
- Only set cognitive_required=true if explicitly requested.
- Only set personality_required=true if explicitly requested.
- If not specified, set booleans to false.
- Return valid JSON only.
"""


# ============================================================
# FORMAT MESSAGES
# ============================================================

def format_messages(messages):

    formatted = []

    for msg in messages:

        role = msg["role"]

        content = msg["content"]

        formatted.append(
            f"{role.upper()}: {content}"
        )

    return "\n".join(formatted)


# ============================================================
# SAFE BOOLEAN
# ============================================================

def safe_bool(value):

    if isinstance(value, bool):

        return value

    if value is None:

        return False

    if isinstance(value, str):

        value = value.lower().strip()

        return value in [
            "true",
            "yes",
            "1"
        ]

    return bool(value)


# ============================================================
# EXTRACTION
# ============================================================

def extract_constraints(messages):

    conversation = format_messages(
        messages
    )

    response = client.chat.completions.create(

        model="qwen/qwen-2.5-7b-instruct",

        temperature=0,

        messages=[

            {
                "role": "system",

                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",

                "content": conversation
            }
        ]
    )

    text = response.choices[0].message.content

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    ).strip()

    try:

        data = json.loads(text)

        # ====================================================
        # HANDLE NULL JSON
        # ====================================================

        if data is None:

            data = {}

        intent = RetrievalIntent(

            role=data.get("role"),

            technical_skills=data.get(
                "technical_skills",
                []
            ),

            behavioral_traits=data.get(
                "behavioral_traits",
                []
            ),

            seniority=data.get(
                "seniority"
            ),

            cognitive_required=safe_bool(
                data.get(
                    "cognitive_required"
                )
            ),

            personality_required=safe_bool(
                data.get(
                    "personality_required"
                )
            ),

            assessment_preferences=data.get(
                "assessment_preferences",
                []
            ),

            constraints=data.get(
                "constraints",
                []
            )
        )

        return intent

    except Exception as e:

        print(
            "\nConstraint Extraction Error:\n"
        )

        print(e)

        print("\nRaw Output:\n")

        print(text)

        return RetrievalIntent()