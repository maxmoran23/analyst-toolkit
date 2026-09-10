"""End-to-end contracts for local discovery and portable exports."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "_tooling/toolkit.py"
sys.path.insert(0, str(CLI.parent))
import toolkit


class ToolkitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = toolkit.inventory()

    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(CLI), *args], cwd=cwd or ROOT,
                              capture_output=True, text=True)

    def test_inventory_matches_disk_and_hashes_sources(self):
        expected = sum(path.name != "README.md" for path in (ROOT / "prompts").glob("*/*.md"))
        self.assertEqual(sum(entry["kind"] == "prompt" for entry in self.entries), expected)
        self.assertEqual(len(self.entries), len({entry["id"] for entry in self.entries}))
        for entry in self.entries:
            data = (ROOT / entry["source"]["path"]).read_bytes()
            self.assertEqual(entry["source"]["sha256"], hashlib.sha256(data).hexdigest())

    def test_catalog_is_deterministic_and_works_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.run_cli("list", "--json", cwd=directory)
            second = self.run_cli("list", "--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        result = json.loads(first.stdout)
        self.assertEqual(result["count"], len(self.entries))
        self.assertNotIn("_payload", result["entries"][0])

    def test_search_filters_and_no_match(self):
        result = self.run_cli("list", "sanctions", "--category", "compliance", "--kind", "prompt", "--json")
        entries = json.loads(result.stdout)["entries"]
        self.assertTrue(entries)
        self.assertTrue(all(entry["category"] == "compliance" and entry["kind"] == "prompt" for entry in entries))
        self.assertEqual(json.loads(self.run_cli("list", "no-such-term-987654321", "--json").stdout)["count"], 0)
        self.assertEqual(self.run_cli("list", "--category", "typo").returncode, 2)

    def test_ambiguous_and_external_paths_rejected(self):
        result = self.run_cli("show", "entity-risk-assessment")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Ambiguous", result.stderr)
        self.assertEqual(self.run_cli("show", "../BASE.md").returncode, 2)
        self.assertEqual(self.run_cli("show", str(ROOT / "BASE.md")).returncode, 2)

    def test_all_prompt_demos_assemble_without_placeholders(self):
        for entry in self.entries:
            if entry["kind"] != "prompt":
                continue
            with self.subTest(entry=entry["id"]):
                payload, manifest = toolkit.assemble(entry, demo=True, include_base=False)
                self.assertEqual(manifest["remaining_placeholders"], [])
                self.assertEqual(manifest["input_file_count"], 1)
                self.assertEqual(manifest["payload_sha256"], hashlib.sha256(payload.encode()).hexdigest())
                self.assertEqual(manifest["payload_size"]["utf8_bytes"], len(payload.encode()))

    def test_base_export_payload_and_manifest(self):
        result = self.run_cli("assemble", "prompts/compliance/entity-risk-assessment", "--demo", "--with-base", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        envelope = json.loads(result.stdout)
        self.assertTrue(envelope["payload"].startswith((ROOT / "BASE.md").read_text().rstrip("\n")))
        self.assertEqual(envelope["manifest"]["input_file_count"], 2)
        self.assertEqual(envelope["manifest"]["payload_size"]["characters"], len(envelope["payload"]))
        self.assertEqual(envelope["manifest"]["payload_sha256"], hashlib.sha256(envelope["payload"].encode()).hexdigest())

    def test_stdout_contains_only_canonical_prompt(self):
        entry = toolkit.select(self.entries, "prompts/compliance/entity-risk-assessment")
        result = self.run_cli("show", entry["id"])
        self.assertEqual(result.stdout, entry["_payload"])
        self.assertNotIn("Try it now", result.stdout)
        self.assertTrue(toolkit.assemble(entry, False, False)[1]["remaining_placeholders"])

    def test_standalone_and_framework_restrictions(self):
        standalone = next(entry for entry in self.entries if entry["kind"] == "standalone")
        self.assertEqual(toolkit.assemble(standalone, False, False)[0], standalone["_text"])
        with self.assertRaises(ValueError):
            toolkit.assemble(standalone, False, True)
        framework = next(entry for entry in self.entries if entry["kind"] == "framework")
        self.assertEqual(self.run_cli("assemble", framework["id"]).returncode, 2)
        self.assertEqual(self.run_cli("show", framework["id"], "--demo").returncode, 2)

    def test_export_never_overwrites_and_budget_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "export.txt"
            args = ("assemble", "prompts/compliance/entity-risk-assessment", "--output", str(path))
            self.assertEqual(self.run_cli(*args, "--max-chars", "1").returncode, 2)
            self.assertFalse(path.exists())
            self.assertFalse(path.parent.exists())
            self.assertEqual(self.run_cli(*args).returncode, 0)
            original = path.read_bytes()
            self.assertEqual(self.run_cli(*args).returncode, 2)
            self.assertEqual(path.read_bytes(), original)
            path.unlink()
            path.symlink_to(Path(directory) / "missing.txt")
            self.assertEqual(self.run_cli(*args).returncode, 2)
            self.assertFalse(path.resolve().exists())


if __name__ == "__main__":
    unittest.main()
