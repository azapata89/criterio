import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import verify  # noqa: E402


def entry(role, content, **extra):
    return {"type": role, "message": {"role": role, "content": content}, **extra}


def tool_use(name, **inp):
    return {"type": "tool_use", "id": "t", "name": name, "input": inp}


def tool_result(text="ok"):
    return {"type": "tool_result", "tool_use_id": "t", "content": text}


def claims_message(*claims, prose="Resumen."):
    return prose + "\n\n```json\n" + json.dumps({"afirmaciones": list(claims)}) + "\n```\n"


def claim(url="https://docs.example.com/a", estado="verificado", cita="texto citado"):
    return {"afirmacion": "x", "url": url, "cita": cita, "fecha_consulta": "2026-10-09",
            "version": "1.0", "tipo_fuente": "oficial", "estado": estado}


class TranscriptMixin:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, *entries):
        path = Path(self.tmp.name) / f"t{id(entries)}.jsonl"
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
        return str(path)


class ClaimsTest(TranscriptMixin, unittest.TestCase):
    def fetched(self, *urls):
        return self.transcript(*[entry("assistant", [tool_use("WebFetch", url=u, prompt="p")]) for u in urls])

    def test_ok_when_verified_urls_were_fetched(self):
        msg = claims_message(claim("https://docs.example.com/a#sec"), claim("", estado="no_verificado", cita=""))
        self.assertEqual(verify.check_claims(msg, self.fetched("https://docs.example.com/a/")), [])

    def test_missing_json_block(self):
        problems = verify.check_claims("Solo prosa sin bloque", self.fetched())
        self.assertIn("bloque", problems[0])

    def test_invalid_json(self):
        problems = verify.check_claims("```json\n{malo\n```", self.fetched())
        self.assertIn("JSON", problems[0])

    def test_verified_claim_needs_url_and_quote(self):
        msg = claims_message(claim(url=""), claim(cita=" "))
        problems = verify.check_claims(msg, self.fetched("https://docs.example.com/a"))
        self.assertEqual(len(problems), 2)

    def test_verified_url_must_have_been_fetched(self):
        msg = claims_message(claim("https://inventada.dev/api"))
        problems = verify.check_claims(msg, self.fetched("https://docs.example.com/a"))
        self.assertIn("inventada.dev", problems[0])

    def test_claim_must_be_object(self):
        problems = verify.check_claims("```json\n{\"afirmaciones\": [\"texto\"]}\n```", self.fetched())
        self.assertIn("objeto", problems[0])

    def test_reused_note_needs_note_path_not_fetch(self):
        ok = claim("https://docs.example.com/a", estado="verificado_previo")
        ok["nota"] = "docs/knowledge/research/vue@3.5.md"
        bad = claim("https://docs.example.com/a", estado="verificado_previo")
        problems = verify.check_claims(claims_message(ok, bad), self.fetched())
        self.assertEqual(len(problems), 1)
        self.assertIn("Afirmación 2", problems[0])

    def test_unknown_estado(self):
        problems = verify.check_claims(claims_message(claim(estado="seguro")), self.fetched())
        self.assertIn("estado", problems[0])


class StopTest(TranscriptMixin, unittest.TestCase):
    def turn(self, *assistant_items, prompt="haz algo"):
        entries = [entry("user", "turno anterior"), entry("assistant", [tool_use("Edit", file_path="/p/old.py")]),
                   entry("user", prompt)]
        for item in assistant_items:
            entries.append(entry("assistant", [item]))
            entries.append(entry("user", [tool_result()]))
        return self.transcript(*entries)

    def test_no_edits_is_fine(self):
        t = self.turn(tool_use("Read", file_path="/p/a.py"))
        self.assertIsNone(verify.check_stop(t, "listo"))

    def test_previous_turn_edits_are_ignored(self):
        self.assertIsNone(verify.check_stop(self.turn(), "listo"))

    def test_code_edit_without_verification_blocks(self):
        t = self.turn(tool_use("Edit", file_path="/p/src/app.py"))
        self.assertIn("verific", verify.check_stop(t, "Hecho."))

    def test_test_run_after_edit_passes(self):
        t = self.turn(tool_use("Edit", file_path="/p/src/app.py"), tool_use("Bash", command="pnpm test -- sum"))
        self.assertIsNone(verify.check_stop(t, "Hecho."))

    def test_test_run_before_edit_does_not_count(self):
        t = self.turn(tool_use("Bash", command="pytest -q"), tool_use("Write", file_path="/p/src/app.py"))
        self.assertIsNotNone(verify.check_stop(t, "Hecho."))

    def test_declared_unverified_passes(self):
        t = self.turn(tool_use("Edit", file_path="/p/src/app.py"))
        self.assertIsNone(verify.check_stop(t, "Cambio hecho.\nSin verificar: no hay runner de tests."))

    def test_docs_and_notes_edits_do_not_require_tests(self):
        t = self.turn(tool_use("Write", file_path="/p/docs/knowledge/learnings/x.md"),
                      tool_use("Edit", file_path="/p/README.md"))
        self.assertIsNone(verify.check_stop(t, "Hecho."))

    def test_verification_commands_recognized(self):
        for cmd in ("php artisan test", "vendor/bin/pest", "npx tsc --noEmit", "ruff check .",
                    "python -m unittest discover", "npx vitest run", "composer test", "mypy src"):
            t = self.turn(tool_use("Edit", file_path="/p/a.ts"), tool_use("Bash", command=cmd))
            self.assertIsNone(verify.check_stop(t, "Hecho."), cmd)

    def test_tool_result_entries_do_not_start_a_turn(self):
        t = self.transcript(entry("user", "haz algo"),
                            entry("assistant", [tool_use("Edit", file_path="/p/a.py")]),
                            entry("user", [tool_result()]),
                            entry("assistant", [{"type": "text", "text": "listo"}]))
        self.assertIsNotNone(verify.check_stop(t, "listo"))


if __name__ == "__main__":
    unittest.main()


class HookScriptsTest(TranscriptMixin, unittest.TestCase):
    def run_script(self, name, payload):
        import subprocess
        return subprocess.run([sys.executable, str(ROOT / "hooks" / name)], input=json.dumps(payload),
                              capture_output=True, text=True, check=True).stdout

    def test_subagent_stop_blocks_investigador_without_evidence(self):
        t = self.transcript(entry("assistant", [tool_use("WebSearch", query="q")]))
        out = self.run_script("subagent_stop.py", {"agent_type": "criterio:investigador",
                                                    "last_assistant_message": claims_message(claim()),
                                                    "agent_transcript_path": t})
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_subagent_stop_ignores_other_agents_and_second_pass(self):
        t = self.transcript(entry("assistant", []))
        base = {"last_assistant_message": "sin bloque", "agent_transcript_path": t}
        self.assertEqual(self.run_script("subagent_stop.py", {**base, "agent_type": "criterio:explorador"}), "")
        self.assertEqual(self.run_script("subagent_stop.py", {**base, "agent_type": "criterio:investigador",
                                                               "stop_hook_active": True}), "")

    def test_stop_blocks_once(self):
        t = self.transcript(entry("user", "haz algo"), entry("assistant", [tool_use("Edit", file_path="/p/a.py")]))
        payload = {"transcript_path": t, "last_assistant_message": "Hecho."}
        self.assertEqual(json.loads(self.run_script("stop.py", payload))["decision"], "block")
        self.assertEqual(self.run_script("stop.py", {**payload, "stop_hook_active": True}), "")


class StopGitTest(TranscriptMixin, unittest.TestCase):
    """Ediciones hechas por Bash (sed, scripts) no aparecen como Edit/Write: se detectan por git + mtime."""

    def setUp(self):
        super().setUp()
        import os
        import subprocess
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        run = lambda *a: subprocess.run(a, cwd=self.repo, check=True, capture_output=True)
        (self.repo / "app.py").write_text("x = 1\n")
        (self.repo / "README.md").write_text("doc\n")
        run("git", "init", "-q")
        run("git", "add", "-A")
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        self.os = os

    def at(self, ts, role, content):
        return {**entry(role, content), "timestamp": ts}

    def touch(self, name, iso, text="x = 2\n"):
        import datetime as dt
        p = self.repo / name
        p.write_text(text)
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
        self.os.utime(p, (t, t))

    def test_bash_edit_without_verification_blocks(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "haz algo"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="python3 - <<EOF")]))
        self.touch("app.py", "2026-10-10T01:00:06Z")
        reason = verify.check_stop(t, "Hecho.", cwd=str(self.repo))
        self.assertIn("app.py", reason)

    def test_bash_edit_then_tests_passes(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "haz algo"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="sed -i '' s/1/2/ app.py")]),
                            self.at("2026-10-10T01:00:20Z", "assistant", [tool_use("Bash", command="pytest -q")]))
        self.touch("app.py", "2026-10-10T01:00:06Z")
        self.assertIsNone(verify.check_stop(t, "Hecho.", cwd=str(self.repo)))

    def test_changes_from_previous_turns_are_ignored(self):
        self.touch("app.py", "2026-10-10T00:30:00Z")
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "¿qué hace app.py?"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Read", file_path="app.py")]))
        self.assertIsNone(verify.check_stop(t, "Imprime x.", cwd=str(self.repo)))

    def test_docs_changes_do_not_require_tests(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "documenta"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="echo >> README.md")]))
        self.touch("README.md", "2026-10-10T01:00:06Z", "doc 2\n")
        self.assertIsNone(verify.check_stop(t, "Hecho.", cwd=str(self.repo)))

    def test_untracked_new_code_file_counts(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "crea un módulo"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="cat > nuevo.py")]))
        self.touch("nuevo.py", "2026-10-10T01:00:06Z")
        self.assertIn("nuevo.py", verify.check_stop(t, "Hecho.", cwd=str(self.repo)))

    def test_metadata_entries_without_timestamp_are_ignored(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "haz algo"),
                            {"type": "mode", "mode": "auto"},
                            {"type": "ai-title", "aiTitle": "x"},
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="python3 - <<EOF")]))
        self.touch("app.py", "2026-10-10T01:00:06Z")
        self.assertIn("app.py", verify.check_stop(t, "Hecho.", cwd=str(self.repo)))

    def test_not_a_git_repo_falls_back_to_tools(self):
        t = self.transcript(self.at("2026-10-10T01:00:00Z", "user", "haz algo"),
                            self.at("2026-10-10T01:00:05Z", "assistant", [tool_use("Bash", command="python3 x.py")]))
        self.assertIsNone(verify.check_stop(t, "Hecho.", cwd=self.tmp.name))
