"""Verify archived instructions without trusting envelope paths or hash claims."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "_tooling/toolkit.py"
sys.path.insert(0, str(CLI.parent))
import toolkit


class ExportVerificationTests(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(CLI), *args], cwd=cwd or ROOT,
                              capture_output=True, text=True)

    def envelope(self):
        result = self.run_cli("assemble", "prompts/compliance/entity-risk-assessment", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_saved_export_verifies_outside_repository(self):
        for demo in (False, True):
            with self.subTest(demo=demo), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "envelope.json"
                args = ["assemble", "prompts/compliance/entity-risk-assessment", "--with-base",
                        "--json", "--output", str(path)]
                if demo:
                    args.append("--demo")
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = self.run_cli("verify", str(path), "--json", cwd=directory)
                self.assertEqual(result.returncode, 0, result.stderr)
                verified = json.loads(result.stdout)
                self.assertEqual(verified["status"], "verified")
                self.assertEqual(verified["source_files"], 3 if demo else 2)

    def test_standalone_export_verifies_without_base(self):
        entry = next(row for row in toolkit.inventory() if row["kind"] == "standalone")
        payload, manifest = toolkit.assemble(entry, False, False)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standalone.json"
            path.write_text(json.dumps({"payload": payload, "manifest": manifest}))
            self.assertEqual(toolkit.verify_export(path)["status"], "verified")

    def test_rehashed_modified_payload_is_not_canonical(self):
        envelope = self.envelope()
        envelope["payload"] += "Altered instruction\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed.json"
            path.write_text(json.dumps(envelope))
            result = self.run_cli("verify", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertIn("Payload hash", result.stderr)
            envelope["manifest"]["payload_sha256"] = toolkit.digest(envelope["payload"].encode())
            path.write_text(json.dumps(envelope))
            result = self.run_cli("verify", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertIn("current repository assembly", result.stderr)

    def test_source_and_metadata_drift_rejected(self):
        original = self.envelope()
        for field in ("source_hash", "source_path", "size", "boolean_size"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                envelope = json.loads(json.dumps(original))
                manifest = envelope["manifest"]
                if field == "source_hash":
                    manifest["sources"][0]["sha256"] = "0" * 64
                elif field == "source_path":
                    manifest["sources"][0]["path"] = "../private-input.txt"
                elif field == "size":
                    manifest["payload_size"]["characters"] += 1
                else:
                    manifest["input_file_count"] = True
                path = Path(directory) / "changed.json"
                path.write_text(json.dumps(envelope))
                result = self.run_cli("verify", str(path))
                self.assertEqual(result.returncode, 2)
                self.assertIn("Manifest differs", result.stderr)

    def test_malformed_export_is_a_clean_failure(self):
        cases = ["[]", "{}", '{"payload": "a", "payload": "b"}',
                 '{"payload": NaN, "manifest": {}}',
                 '{"payload": "text", "manifest": {"schema_version": true}}',
                 '{"payload": "text", "manifest": []}']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for content in cases:
                with self.subTest(content=content):
                    path.write_text(content)
                    result = self.run_cli("verify", str(path))
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertNotIn("Traceback", result.stderr)

    def test_source_symlinks_cannot_export_ignored_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "private.txt"
            private.write_text("synthetic private marker")
            direct = root / "source.md"
            direct.symlink_to(private)
            folder = root / "linked"
            folder.symlink_to(root, target_is_directory=True)
            with patch.object(toolkit, "ROOT", root):
                for path in (direct, folder / "private.txt"):
                    with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Symbolic links"):
                        toolkit.read_source(path)


if __name__ == "__main__":
    unittest.main()
