"""Base de conocimiento por proyecto: notas markdown con frontmatter en docs/knowledge/.

Solo stdlib. Lo usan los hooks y los ejecutables de bin/.
"""

import datetime as dt
import os
import re
import subprocess
from pathlib import Path

KB_DIR = Path("docs") / "knowledge"
INDEX_NAME = "INDEX.md"
PENDIENTES_NAME = "PENDIENTES.md"
SECCIONES = {"ahora": "Ahora", "siguiente": "Siguiente", "bloqueadas": "Bloqueadas", "hecho": "Hecho"}
MAX_SIGUIENTE = 5
MAX_TAREA = 110
# Los agentes no siempre usan los títulos exactos: se aceptan sinónimos comunes.
SINONIMOS = {
    "ahora": ("ahora", "en curso", "en progreso", "doing", "now", "actual"),
    "siguiente": ("siguiente", "siguientes", "por hacer", "pendiente", "pendientes", "backlog", "to do", "todo", "next", "próximo", "próximos"),
    "bloqueadas": ("bloqueadas", "bloqueada", "bloqueado", "bloqueados", "en espera", "pospuestas", "pospuesto", "blocked"),
    "hecho": ("hecho", "hechas", "hechos", "completado", "completadas", "terminado", "terminadas", "done"),
}
NOTE_DIRS = ("decisions", "learnings", "research")
AREAS = ("frontend", "backend", "db", "security", "qa", "perf", "ops", "producto")
AUTO_START = "<!-- kb:auto:start -->"
AUTO_END = "<!-- kb:auto:end -->"
MAX_INDEX_LINES = 200
STALE_DAYS = 180

INDEX_HEADER = f"""# Base de conocimiento del proyecto

<!-- Escrito a mano: stack, versiones clave y comandos. Mantenerlo corto. -->
## Stack
- (pendiente)

## Comandos
- (pendiente)

## Notas
{AUTO_START}
{AUTO_END}
"""


PENDIENTES_PLANTILLA = """# Pendientes

<!-- En orden de prioridad. Bloqueadas: «— espera: <qué la desbloquea> — revisar: AAAA-MM-DD».
     Hecho: «- [x] AAAA-MM-DD tarea», solo las últimas 10. -->
## Ahora

## Siguiente

## Bloqueadas

## Hecho
"""


def project_root(explicit=None):
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()


def parse_frontmatter(text):
    """Frontmatter YAML mínimo: `clave: valor`, `clave: [a, b]` y listas con `- item`."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data, key = {}, None
    for raw in text[4:end].splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s*(.*)$", line)
        if item and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(_scalar(_strip_comment(item.group(1))))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not kv:
            continue
        key, value = kv.group(1), _strip_comment(kv.group(2))
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_scalar(v) for v in inner.split(",")] if inner else []
        else:
            data[key] = _scalar(value) if value else []
    return data


def _strip_comment(value):
    """Quita un comentario ` # ...` al final, salvo dentro de comillas."""
    value = value.strip()
    if value[:1] in "\"'":
        return value
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def _scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def iter_notes(kb):
    for sub in NOTE_DIRS:
        folder = kb / sub
        if folder.is_dir():
            yield from sorted(folder.glob("*.md"))


def load_note(path):
    meta = parse_frontmatter(path.read_text(encoding="utf-8"))
    return {
        "path": path,
        "type": meta.get("type") or path.parent.name.rstrip("s"),
        "title": meta.get("title") or path.stem,
        "status": meta.get("status") or "active",
        "area": meta.get("area") or "",
        "verified_at": meta.get("verified_at") or "",
        "sources": _as_list(meta.get("sources")),
        "refs": _as_list(meta.get("refs")),
    }


def _as_list(value):
    if value in (None, ""):
        return []
    return value if isinstance(value, list) else [value]


def init_kb(root):
    kb = root / KB_DIR
    for sub in NOTE_DIRS:
        (kb / sub).mkdir(parents=True, exist_ok=True)
    index = kb / INDEX_NAME
    if not index.exists():
        index.write_text(INDEX_HEADER, encoding="utf-8")
    pendientes = kb / PENDIENTES_NAME
    if not pendientes.exists():
        pendientes.write_text(PENDIENTES_PLANTILLA, encoding="utf-8")
    return kb


def parse_pendientes(text):
    """Secciones de PENDIENTES.md → listas de tareas (sin la casilla), en orden."""
    out, actual = {k: [] for k in SECCIONES}, None
    for linea in text.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", linea)
        if h:
            titulo = re.sub(r"[^\wáéíóúñ ]", "", h.group(1).lower()).strip()
            actual = next((k for k, nombres in SINONIMOS.items() if titulo in nombres), None)
            continue
        item = re.match(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$", linea)
        if item and actual:
            out[actual].append(item.group(1))
    return out


def bloqueadas_para_revisar(pendientes, today=None):
    today = today or dt.date.today()
    due = []
    for tarea in pendientes["bloqueadas"]:
        m = re.search(r"revisar:\s*(\d{4}-\d{2}-\d{2})", tarea)
        if m:
            try:
                if dt.date.fromisoformat(m.group(1)) <= today:
                    due.append(tarea)
            except ValueError:
                continue
    return due


def _corta(tarea):
    """Una línea: sin negritas, primera oración y como máximo MAX_TAREA caracteres."""
    limpia = re.sub(r"\*\*|__", "", tarea).strip()
    primera = re.split(r"(?<=[.;])\s", limpia, maxsplit=1)[0]
    return primera if len(primera) <= MAX_TAREA else primera[: MAX_TAREA - 1].rstrip() + "…"


def contexto_pendientes(text, today=None):
    """Resumen corto para inyectar al iniciar: ahora, siguiente (top N) y bloqueadas a revisar."""
    p = parse_pendientes(text)
    lineas = ["Pendientes del proyecto (docs/knowledge/PENDIENTES.md):"]
    vacio = "(nada en curso; lo próximo es el 1)" if p["siguiente"] else "(nada en curso)"
    lineas += [f"- Ahora: {_corta(t)}" for t in p["ahora"]] or [f"- Ahora: {vacio}"]
    for i, t in enumerate(p["siguiente"][:MAX_SIGUIENTE], 1):
        lineas.append(f"  {i}. {_corta(t)}")
    if len(p["siguiente"]) > MAX_SIGUIENTE:
        lineas.append(f"  … y {len(p['siguiente']) - MAX_SIGUIENTE} más")
    if p["bloqueadas"]:
        lineas.append(f"- {len(p['bloqueadas'])} bloqueada(s).")
        lineas += [f"  revisar hoy: {_corta(t)}" for t in bloqueadas_para_revisar(p, today)]
    return "\n".join(lineas)


def render_listing(kb):
    lines = []
    for path in iter_notes(kb):
        note = load_note(path)
        if note["status"] == "superseded":
            continue
        rel = path.relative_to(kb).as_posix()
        mark = f" [{note['status']}]" if note["status"] != "active" else ""
        kind = f"{note['type']} · {note['area']}" if note["area"] else note["type"]
        lines.append(f"- `{rel}` ({kind}){mark}: {note['title']}")
    return lines


def build_index(kb):
    """Reescribe solo el bloque automático del INDEX; la cabecera manual no se toca."""
    index = kb / INDEX_NAME
    text = index.read_text(encoding="utf-8") if index.exists() else INDEX_HEADER
    if AUTO_START not in text or AUTO_END not in text:
        text = text.rstrip() + f"\n\n## Notas\n{AUTO_START}\n{AUTO_END}\n"
    head, rest = text.split(AUTO_START, 1)
    _, tail = rest.split(AUTO_END, 1)
    listing = render_listing(kb)
    budget = MAX_INDEX_LINES - head.count("\n") - tail.count("\n") - 3
    dropped = 0
    if len(listing) > budget:
        dropped = len(listing) - max(budget, 0)
        listing = listing[: max(budget, 0)]
    if dropped:
        listing.append(f"- … {dropped} notas más no listadas: buscar con grep en {KB_DIR.as_posix()}/")
    body = "\n".join(listing) if listing else "- (sin notas todavía)"
    new = f"{head}{AUTO_START}\n{body}\n{AUTO_END}{tail}"
    index.write_text(new, encoding="utf-8")
    return len(listing), dropped


def check(kb, root, today=None, stale_days=STALE_DAYS):
    """Problemas de frescura detectables sin modelo: refs rotos, verificación vieja, sin fuentes."""
    today = today or dt.date.today()
    problems = []
    for path in iter_notes(kb):
        note = load_note(path)
        if note["status"] == "superseded":
            continue
        rel = path.relative_to(kb).as_posix()
        for ref in note["refs"]:
            target = ref.split(":", 1)[0].split("#", 1)[0]
            if target and not (root / target).exists():
                problems.append(f"{rel}: ref inexistente `{ref}`")
        if note["status"] == "stale":
            problems.append(f"{rel}: marcada como stale")
        elif note["verified_at"]:
            try:
                age = (today - dt.date.fromisoformat(str(note["verified_at"]))).days
            except ValueError:
                problems.append(f"{rel}: verified_at inválido `{note['verified_at']}`")
            else:
                if age > stale_days:
                    problems.append(f"{rel}: verificada hace {age} días")
        else:
            problems.append(f"{rel}: sin verified_at")
        if note["area"] and note["area"] not in AREAS:
            problems.append(f"{rel}: area desconocida `{note['area']}`")
        if note["type"] in ("learning", "research") and not note["sources"]:
            problems.append(f"{rel}: sin sources")
    return problems
