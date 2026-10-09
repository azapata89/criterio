#!/usr/bin/env python3
"""SubagentStop: bloquea al investigador si entrega afirmaciones sin evidencia comprobable.

Sin llamadas al modelo. Bloquea como mucho una vez seguida (stop_hook_active).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import verify  # noqa: E402


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    agent = str(data.get("agent_type") or "")
    if agent.split(":")[-1] != "investigador" or data.get("stop_hook_active"):
        return 0
    problems = verify.check_claims(data.get("last_assistant_message", ""), data.get("agent_transcript_path", ""))
    if problems:
        reason = "Corrige tu entrega antes de terminar:\n- " + "\n- ".join(problems)
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
