#!/usr/bin/env python3
"""Stop: si se editó código en este turno, exige verificación o declarar qué quedó sin verificar.

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
    if data.get("stop_hook_active") or not data.get("transcript_path"):
        return 0
    try:
        reason = verify.check_stop(data["transcript_path"], data.get("last_assistant_message", ""))
    except OSError:
        return 0
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
