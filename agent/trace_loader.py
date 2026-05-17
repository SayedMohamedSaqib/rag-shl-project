from pathlib import Path


TRACE_DIR = Path(
    "Conversation_Traces"
)


def load_conversation_traces():

    traces = []

    if not TRACE_DIR.exists():

        return ""

    for path in sorted(
        TRACE_DIR.glob("*.md")
    ):

        try:

            content = path.read_text(
                encoding="utf-8"
            )

            traces.append(content)

        except Exception as e:

            print(
                f"Failed loading {path}: {e}"
            )

    return "\n\n".join(traces)