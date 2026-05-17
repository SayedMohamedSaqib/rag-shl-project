import json
import os

from openai import OpenAI

from dotenv import load_dotenv

from agent.trace_loader import (
    load_conversation_traces,
)

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

    api_key=OPENROUTER_API_KEY,
)

# ============================================================
# LOAD TRACES
# ============================================================

TRACE_EXAMPLES = load_conversation_traces()

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = f"""
You are an SHL assessment recommendation orchestration engine.

Your job is to decide:

- whether to clarify
- whether to retrieve
- whether to refuse
- whether to compare

You MUST follow the conversational behavior patterns shown below.

CONVERSATIONAL TRACES:

{TRACE_EXAMPLES}

Rules:

- Clarify vague recruiter requests before retrieval.
- Do NOT recommend too early.
- Ask for missing seniority when needed.
- Ask for missing assessment dimensions when needed.
- Support refinement naturally.
- Only discuss SHL assessments.
- Refuse off-topic requests.

Return STRICT JSON ONLY.

Schema:

{{
  "action": "clarify" | "retrieve" | "refuse" | "compare",
  "reply": string,
  "reason": string
}}
"""

# ============================================================
# DECISION
# ============================================================

def llm_decide(messages, state):

    payload = {

        "messages": messages,

        "state": state,
    }

    response = client.chat.completions.create(

        model="qwen/qwen-2.5-7b-instruct",

        temperature=0,

        messages=[

            {
                "role": "system",

                "content": SYSTEM_PROMPT,
            },

            {
                "role": "user",

                "content": json.dumps(
                    payload,
                    indent=2,
                ),
            },
        ],
    )

    text = response.choices[0].message.content

    text = text.replace(
        "```json",
        "",
    )

    text = text.replace(
        "```",
        "",
    ).strip()

    try:

        return json.loads(text)

    except Exception as e:

        print(
            "\nLLM Decision Parse Error:\n"
        )

        print(e)

        print("\nRaw Output:\n")

        print(text)

        return {

            "action": "clarify",

            "reply": (
                "Could you share more "
                "details about the role?"
            ),

            "reason": "fallback",
        }