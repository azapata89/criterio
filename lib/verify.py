"""Verificaciones deterministas para los hooks de cierre. Solo stdlib, sin modelo.

- check_claims: el investigador entrega un bloque JSON de afirmaciones; cada
  afirmación «verificado» cita una URL que de verdad abrió con WebFetch, y cada
  «verificado_previo» indica la nota de la base de conocimiento de la que sale.
- check_stop: si en este turno se editó código, debe haberse corrido una
  verificación después de la última edición, o declarado qué quedó sin verificar.
  Las ediciones se detectan por las herramientas Edit/Write y, como también se
  edita desde Bash (sed, heredocs, scripts), por los archivos que git ve
  modificados con fecha posterior al inicio del turno.
"""

import datetime as dt
import json
import os
import re
import subprocess
from urllib.parse import urlsplit

ESTADOS = ("verificado", "verificado_previo", "no_verificado")
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
NON_CODE = re.compile(r"(^|/)(docs/|\.claude/|LICENSE$)|\.(md|mdx|txt|rst|example|sample|dist)$", re.IGNORECASE)
VERIFY_CMD = re.compile(
    r"\b(pytest|unittest|tox|nox|ruff|mypy|pyright|flake8|"
    r"vitest|jest|mocha|playwright|tsc|eslint|biome|"
    r"phpunit|pest|phpstan|psalm|artisan\s+test|"
    r"(npm|pnpm|yarn|bun|composer)\s+(run\s+)?(test|lint|typecheck|check)|"
    r"cargo\s+(test|check|clippy)|go\s+(test|vet)|make\s+(test|check|lint))\b"
    # Scripts de prueba propios del proyecto: probar.sh, test.sh, run-tests.sh, scripts/check, bin/test…
    r"|(^|[\s;&|])(\./|[\w.-]+/)*(run-)?(test|tests|check|probar|prueba|pruebas)\.sh(\s|$|;|&|\|)"
    r"|(^|[\s;&|])(\./|[\w.-]+/)+(run-)?(test|tests|check|probar|prueba|pruebas)(\s|$|;|&|\|)"
)
DECLARED_UNVERIFIED = re.compile(r"sin verificar|no verificad[oa]|no (lo )?pude verificar", re.IGNORECASE)
FAILED_OUTPUT = re.compile(
    r'"result"\s*:\s*"failed"|\bFAILED\b|ERRORS!|\b[1-9]\d*\s+(failed|failing|failures?|errors?)\b'
)
ACK_FAILURE = re.compile(r"\bfall(a|an|ó|aron|ando|ido)\b|en rojo|failing|failed", re.IGNORECASE)


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


def _tool_uses(entries, with_id=False):
    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        for item in _content(entry):
            if isinstance(item, dict) and item.get("type") == "tool_use":
                inp = item.get("input")
                inp = inp if isinstance(inp, dict) else {}
                if with_id:
                    yield item.get("id"), item.get("name", ""), inp
                else:
                    yield item.get("name", ""), inp


def _tool_results(entries):
    """id de tool_use → (falló, momento en que llegó el resultado)."""
    results = {}
    for entry in entries:
        for item in _content(entry):
            if isinstance(item, dict) and item.get("type") == "tool_result":
                text = item.get("content")
                text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
                failed = bool(item.get("is_error")) or bool(FAILED_OUTPUT.search(text))
                results[item.get("tool_use_id")] = (failed, _timestamp(entry))
    return results


def _norm_url(url):
    parts = urlsplit(url.strip())
    return f"{parts.netloc.lower()}{parts.path.rstrip('/')}"


def _squash(text):
    return re.sub(r"\s+", "", text)


def _check_local_quote(i, path, cita):
    """Evidencia local (lockfile, código): el archivo existe y la cita aparece en él (sin contar espacios)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError:
        return [f"Afirmación {i}: el archivo {path} no existe o no se puede leer."]
    if not cita.strip():
        return [f"Afirmación {i}: marcada verificado sin cita textual."]
    if _squash(cita) not in _squash(content):
        return [f"Afirmación {i}: la cita no aparece en {path}; cópiala literal o márcala no_verificado."]
    return []


def _handback_message(entries):
    """Último informe entregado con la herramienta SubagentHandback, si existe."""
    message = None
    for name, inp in _tool_uses(entries):
        if name == "SubagentHandback" and isinstance(inp.get("message"), str):
            message = inp["message"]
    return message


def check_claims(message, transcript_path):
    """Devuelve la lista de problemas (vacía si todo está en orden)."""
    entries = _read_jsonl(transcript_path)
    message = _handback_message(entries) or message
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

    fetched = {_norm_url(inp.get("url", "")) for name, inp in _tool_uses(entries) if name == "WebFetch"}
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
        if url.startswith("file://"):
            problems += _check_local_quote(i, url[len("file://"):], str(claim.get("cita") or ""))
            continue
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


def _timestamp(entry):
    try:
        return dt.datetime.fromisoformat(str(entry["timestamp"]).replace("Z", "+00:00")).timestamp()
    except (KeyError, ValueError):
        return None


def _git(cwd, *args):
    out = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5)
    return out.stdout if out.returncode == 0 else None


def _git_code_changes(cwd, since):
    """(mtime, ruta) de archivos de código modificados o nuevos según git, posteriores a `since`."""
    try:
        top = _git(cwd, "rev-parse", "--show-toplevel")
        status = _git(cwd, "status", "--porcelain", "-z", "--untracked-files=all") if top else None
    except (OSError, subprocess.SubprocessError):
        return []
    if not status:
        return []
    changes, tokens = [], status.split("\0")
    i = 0
    while i < len(tokens):
        token = tokens[i]
        i += 1
        if len(token) < 4:
            continue
        code, path = token[:2], token[3:]
        if "R" in code or "C" in code:
            i += 1  # el siguiente token es la ruta original del renombrado
        if NON_CODE.search(path):
            continue
        full = os.path.join(top.strip(), path)
        try:
            mtime = os.stat(full).st_mtime
        except OSError:
            continue
        if mtime > since:
            changes.append((mtime, path))
    return changes


def check_stop(transcript_path, last_message, cwd=None):
    """Devuelve el motivo para bloquear el cierre, o None si se puede cerrar."""
    turn = _current_turn(_read_jsonl(transcript_path))
    # Las entradas de metadatos (modo, título…) no traen hora: heredan la de la anterior.
    times, last = [], None
    for entry in turn:
        last = _timestamp(entry) or last
        times.append(last)
    timed = bool(turn) and times[0] is not None
    results = _tool_results(turn)
    events = []  # (momento, orden, tipo, ruta)
    for i, entry in enumerate(turn):
        when = times[i] if timed else i
        for j, (tid, name, inp) in enumerate(_tool_uses([entry], with_id=True)):
            path = str(inp.get("file_path") or inp.get("notebook_path") or "")
            if name in EDIT_TOOLS and path and not NON_CODE.search(path):
                events.append((when, (i, j), "edit", path))
            elif (name == "Bash" and VERIFY_CMD.search(str(inp.get("command", "")))
                  and not inp.get("run_in_background")):  # en segundo plano aún no hay resultado
                failed, done_at = results.get(tid, (False, None))
                # La verificación vale desde que terminó: el mismo comando puede editar antes de probar.
                at = done_at if (timed and done_at is not None) else when
                events.append((at, (i, j), "fail" if failed else "verify", None))
    if timed and cwd:
        events += [(mtime, (-1, 0), "edit", path) for mtime, path in _git_code_changes(cwd, times[0])]

    last_edit, verified_after, last_failed = None, False, False
    for _, _, kind, path in sorted(events, key=lambda e: (e[0], e[1])):
        if kind == "edit":
            last_edit, verified_after, last_failed = path, False, False
        elif last_edit:
            verified_after, last_failed = kind == "verify", kind == "fail"
    message = last_message or ""
    if last_edit is None or verified_after or DECLARED_UNVERIFIED.search(message):
        return None
    if last_failed:
        if ACK_FAILURE.search(message):
            return None
        return (
            f"La última verificación después de editar ({last_edit}) falló y tu mensaje no lo dice. "
            "Corrige el fallo y vuelve a correrla, o explica qué falla y por qué."
        )
    return (
        f"Editaste código ({last_edit}) y no corriste ninguna verificación después. "
        "Corre los tests, lint o type-check relevantes del proyecto; si no es posible, "
        "termina con una línea «Sin verificar: <qué y por qué>»."
    )
