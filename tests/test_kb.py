import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import kb  # noqa: E402

TEMPLATES = ROOT / "skills" / "remember" / "templates"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class FrontmatterTest(unittest.TestCase):
    def test_scalars_lists_and_comments(self):
        meta = kb.parse_frontmatter(
            "---\n"
            "title: \"Usar # en títulos\"\n"
            "status: active   # proposed | active\n"
            "sources: [https://a.dev/x#frag, b.py:10]  # comentario\n"
            "refs:\n"
            "  - src/app.py\n"
            "  - 'docs/x.md'\n"
            "superseded_by:\n"
            "---\nbody\n"
        )
        self.assertEqual(meta["title"], "Usar # en títulos")
        self.assertEqual(meta["status"], "active")
        self.assertEqual(meta["sources"], ["https://a.dev/x#frag", "b.py:10"])
        self.assertEqual(meta["refs"], ["src/app.py", "docs/x.md"])
        self.assertEqual(meta["superseded_by"], [])

    def test_no_frontmatter(self):
        self.assertEqual(kb.parse_frontmatter("# solo texto"), {})

    def test_templates_parse(self):
        for name in ("decision.md", "learning.md"):
            meta = kb.parse_frontmatter((TEMPLATES / name).read_text(encoding="utf-8"))
            self.assertIn(meta["status"], ("active",))
            self.assertEqual(meta["sources"], [])


class KnowledgeBaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.kb = kb.init_kb(self.root)
        write(self.root / "src" / "app.py", "x = 1\n")

    def tearDown(self):
        self.tmp.cleanup()

    def note(self, rel, **fields):
        lines = ["---"] + [f"{k}: {v}" for k, v in fields.items()] + ["---", "cuerpo"]
        write(self.kb / rel, "\n".join(lines) + "\n")

    def test_index_keeps_manual_header_and_skips_superseded(self):
        index = self.kb / kb.INDEX_NAME
        index.write_text(index.read_text().replace("- (pendiente)", "- Python 3.12", 1))
        self.note("decisions/0001-db.md", type="decision", title="Usamos Postgres", status="active", area="db")
        self.note("decisions/0000-old.md", type="decision", title="Viejo", status="superseded")
        self.note("learnings/cache.md", type="learning", title="Caché", status="stale")
        kb.build_index(self.kb)
        kb.build_index(self.kb)  # idempotente
        text = index.read_text()
        self.assertIn("- Python 3.12", text)
        self.assertIn("`decisions/0001-db.md` (decision · db): Usamos Postgres", text)
        self.assertIn("`learnings/cache.md` (learning) [stale]: Caché", text)
        self.assertNotIn("Viejo", text)
        self.assertEqual(text.count(kb.AUTO_START), 1)

    def test_index_respects_line_limit(self):
        for i in range(300):
            self.note(f"learnings/n{i:03}.md", type="learning", title=f"n{i}")
        listed, dropped = kb.build_index(self.kb)
        lines = (self.kb / kb.INDEX_NAME).read_text().splitlines()
        self.assertLessEqual(len(lines), kb.MAX_INDEX_LINES)
        self.assertGreater(dropped, 0)

    def test_check_detects_problems(self):
        today = dt.date(2026, 10, 9)
        self.note("learnings/ok.md", type="learning", title="ok", verified_at="2026-10-01",
                  sources="[https://docs.python.org]", refs="[src/app.py:1]")
        self.note("learnings/broken.md", type="learning", title="b", verified_at="2026-10-01",
                  sources="[x]", refs="[src/missing.py]")
        self.note("learnings/old.md", type="learning", title="o", verified_at="2025-01-01", sources="[x]")
        self.note("learnings/nosrc.md", type="learning", title="n", verified_at="2026-10-01")
        self.note("decisions/0001-x.md", type="decision", title="d", verified_at="2026-10-01", area="db")
        self.note("decisions/0003-z.md", type="decision", title="z", verified_at="2026-10-01", area="infra")
        self.note("decisions/0002-y.md", type="decision", title="s", status="superseded", refs="[gone.py]")
        problems = "\n".join(kb.check(self.kb, self.root, today=today))
        self.assertNotIn("ok.md", problems)
        self.assertIn("broken.md: ref inexistente `src/missing.py`", problems)
        self.assertIn("old.md: verificada hace", problems)
        self.assertIn("nosrc.md: sin sources", problems)
        self.assertIn("0003-z.md: area desconocida `infra`", problems)
        self.assertNotIn("0001-x.md", problems)  # las decisiones no exigen sources
        self.assertNotIn("0002-y.md", problems)  # superseded se ignora


class SessionStartHookTest(unittest.TestCase):
    def run_hook(self, root):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
        return subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "session_start.py")],
            input="{}", capture_output=True, text=True, env=env, check=True,
        ).stdout

    def test_triage_without_kb(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = json.loads(self.run_hook(Path(tmp)))["hookSpecificOutput"]["additionalContext"]
            self.assertIn("TRIVIAL", ctx)
            self.assertIn("/criterio:remember", ctx)
            self.assertNotIn("Base de conocimiento de este proyecto", ctx)

    def test_injects_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = kb.init_kb(root)
            write(base / "learnings" / "x.md", "---\ntype: learning\ntitle: Algo útil\n---\n")
            kb.build_index(base)
            out = json.loads(self.run_hook(root))
            ctx = out["hookSpecificOutput"]["additionalContext"]
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
            self.assertIn("Algo útil", ctx)
            self.assertIn("TRIVIAL", ctx)
            self.assertIn("knowledge-review", ctx)  # sin verified_at ni sources → aviso
            self.assertLess(len(ctx), 10000)


if __name__ == "__main__":
    unittest.main()


class PendientesTest(unittest.TestCase):
    TEXTO = """# Pendientes

## Ahora
- [ ] Proteger restablecer demo

## Siguiente
- [ ] Quitar copia de alertas externa
- [ ] CI con tests

## Bloqueadas
- [ ] SMTP real — espera: cuenta SMTP del cliente — revisar: 2026-10-08
- [ ] Registrar la marca — espera: revisión legal — revisar: 2026-12-01

## Hecho
- [x] 2026-10-09 Base del repo
"""

    def test_parse_sections_in_order(self):
        p = kb.parse_pendientes(self.TEXTO)
        self.assertEqual(p["ahora"], ["Proteger restablecer demo"])
        self.assertEqual(p["siguiente"], ["Quitar copia de alertas externa", "CI con tests"])
        self.assertEqual(len(p["bloqueadas"]), 2)
        self.assertEqual(p["hecho"], ["2026-10-09 Base del repo"])

    def test_blocked_due_for_review(self):
        due = kb.bloqueadas_para_revisar(kb.parse_pendientes(self.TEXTO), dt.date(2026, 10, 9))
        self.assertEqual(len(due), 1)
        self.assertIn("SMTP", due[0])

    def test_context_is_short_and_prioritized(self):
        ctx = kb.contexto_pendientes(self.TEXTO, dt.date(2026, 10, 9))
        self.assertIn("Ahora: Proteger restablecer demo", ctx)
        self.assertIn("1. Quitar copia de alertas externa", ctx)
        self.assertIn("2 bloqueada(s)", ctx)
        self.assertIn("revisar hoy: SMTP", ctx)
        self.assertNotIn("Base del repo", ctx)  # lo hecho no se inyecta

    def test_init_creates_pendientes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = kb.init_kb(Path(tmp))
            p = kb.parse_pendientes((base / "PENDIENTES.md").read_text())
            self.assertEqual(p, {"ahora": [], "siguiente": [], "bloqueadas": [], "hecho": []})


class SessionStartPendientesTest(unittest.TestCase):
    def test_injects_pendientes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = kb.init_kb(root)
            (base / "PENDIENTES.md").write_text(PendientesTest.TEXTO)
            env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
            out = subprocess.run([sys.executable, str(ROOT / "hooks" / "session_start.py")], input="{}",
                                 capture_output=True, text=True, env=env, check=True).stdout
            ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Ahora: Proteger restablecer demo", ctx)


class PendientesTolerantesTest(unittest.TestCase):
    """Forma real (anonimizada) escrita por un agente sin plantilla: títulos sinónimos, tareas largas y negritas."""

    def setUp(self):
        self.texto = (ROOT / "tests" / "fixtures_pendientes_reales.md").read_text(encoding="utf-8")

    def test_synonym_sections(self):
        p = kb.parse_pendientes(self.texto)
        self.assertEqual(len(p["siguiente"]), 8)   # «Por hacer»
        self.assertEqual(len(p["bloqueadas"]), 1)  # «Bloqueado»
        self.assertEqual(len(p["hecho"]), 1)

    def test_long_tasks_are_one_line_in_context(self):
        ctx = kb.contexto_pendientes(self.texto)
        self.assertIn("1. Quitar la copia de alertas a un correo externo", ctx)
        self.assertIn("1 bloqueada(s)", ctx)
        self.assertTrue(all(len(l) <= kb.MAX_TAREA + 12 for l in ctx.splitlines()[1:]), ctx)

    def test_without_ahora_points_to_first_next(self):
        self.assertIn("Ahora: (nada en curso; lo próximo es el 1)", kb.contexto_pendientes(self.texto))
