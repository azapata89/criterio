"""Verificaciones deterministas para los hooks de cierre. Solo stdlib, sin modelo.

- check_claims: el investigador entrega un bloque JSON de afirmaciones; cada
  afirmación «verificado» cita una URL que de verdad abrió con WebFetch, y cada
  «verificado_previo» indica la nota de la base de conocimiento de la que sale.
- check_stop: si en este turno se editó código, debe haberse corrido una
  verificación después de la última edición, o declarado qué quedó sin verificar.
"""

import json
import re
from urllib.parse import urlsplit

ESTADOS = ("verificado", "verificado_previo", "no_verificado")
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
NON_CODE = re.compile(r"(^|/)(docs/|\.claude/)|\.(md|mdx|txt|rst)$", re.IGNORECASE)
VERIFY_CMD = re.compile(
    r"\b(pytest|unittest|tox|nox|ruff|mypy|pyright|flake8|"
    r"vitest|jest|mocha|playwright|tsc|eslint|biome|"
    r"phpunit|pest|phpstan|psalm|artisan\s+test|"
    r"(npm|pnpm|yarn|bun|composer)\s+(run\s+)?(test|lint|typecheck|check)|"
    r"cargo\s+(test|check|clippy)|go\s+(test|vet)|make\s+(test|check|lint))\b"
)
DECLARED_UNVERIFIED = re.compile(r"sin verificar|no verificad[oa]|no (lo )?pude verificar", re.IGNORECASE)


def _read_jsonl(path):
    entries = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    return entries


def _content(entry):
    msg = entry.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def _tool_uses(entries):
    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        for item in _content(entry):
            if isinstance(item, dict) and item.get("type") == "tool_use":
                inp = item.get("input")
                yield item.get("name", ""), inp if isinstance(inp, dict) else {}


def _norm_url(url):
    parts = urlsplit(url.strip())
    return f"{parts.netloc.lower()}{parts.path.rstrip('/')}"


def check_claims(message, transcript_path):
    """Devuelve la lista de problemas (vacía si todo está en orden)."""
    blocks = JSON_BLOCK.findall(message or "")
    if not blocks:
        return ["Falta el bloque ```json con las afirmaciones (formato en la definición del agente)."]
    try:
        data = json.loads(blocks[-1])
    except ValueError as exc:
        return [f"El bloque JSON de afirmaciones no es válido: {exc}"]
    claims = data.get("afirmaciones") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return ["El bloque JSON debe tener la forma {\"afirmaciones\": [...]}."]

    fetched = {_norm_url(inp.get("url", "")) for name, inp in _tool_uses(_read_jsonl(transcript_path))
               if name == "WebFetch"}
    problems = []
    for i, claim in enumerate(claims, 1):
        if not isinstance(claim, dict):
            problems.append(f"Afirmación {i}: debe ser un objeto JSON.")
            continue
        estado = claim.get("estado")
        if estado not in ESTADOS:
            problems.append(f"Afirmación {i}: estado `{estado}` inválido; usa {', '.join(ESTADOS)}.")
            continue
        if estado == "verificado_previo":
            if not str(claim.get("nota") or "").strip():
                problems.append(f"Afirmación {i}: verificado_previo debe indicar la `nota` de la que sale.")
            continue
        if estado != "verificado":
            continue
        url = str(claim.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            problems.append(f"Afirmación {i}: marcada verificado sin URL.")
        elif _norm_url(url) not in fetched:
            problems.append(f"Afirmación {i}: la URL {url} no se abrió con WebFetch en esta investigación; ábrela o márcala no_verificado.")
        if not str(claim.get("cita") or "").strip():
            problems.append(f"Afirmación {i}: marcada verificado sin cita textual.")
    return problems


def _current_turn(entries):
    """Entradas desde el último mensaje real del usuario (no resultados de herramientas)."""
    start = 0
    for i, entry in enumerate(entries):
        if entry.get("type") != "user" or entry.get("isMeta"):
            continue
        items = _content(entry)
        if items and not any(isinstance(x, dict) and x.get("type") == "tool_result" for x in items):
            start = i
    return entries[start:]


def check_stop(transcript_path, last_message):
    """Devuelve el motivo para bloquear el cierre, o None si se puede cerrar."""
    last_edit, verified_after = None, False
    for name, inp in _tool_uses(_current_turn(_read_jsonl(transcript_path))):
        path = str(inp.get("file_path") or inp.get("notebook_path") or "")
        if name in EDIT_TOOLS and path and not NON_CODE.search(path):
            last_edit, verified_after = path, False
        elif name == "Bash" and last_edit and VERIFY_CMD.search(str(inp.get("command", ""))):
            verified_after = True
    if last_edit is None or verified_after or DECLARED_UNVERIFIED.search(last_message or ""):
        return None
    return (
        f"Editaste código ({last_edit}) y no corriste ninguna verificación después. "
        "Corre los tests, lint o type-check relevantes del proyecto; si no es posible, "
        "termina con una línea «Sin verificar: <qué y por qué>»."
    )
