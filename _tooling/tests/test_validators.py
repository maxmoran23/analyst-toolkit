"""Negative fixtures prove safety gates reject malformed payloads."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_tooling"))
from markdown_blocks import fenced_blocks
from build_demos import extract_prompt_block
from validate_embedded import validate
from repository_files import public_files
from validate_index import content_directories


class FenceTests(unittest.TestCase):
    def test_matching_fence_type_and_length(self):
        text = "````python\na = '''\n```\n~~~\n'''\n````\n"
        blocks = fenced_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].body, "a = '''\n```\n~~~\n'''\n")
        self.assertTrue(blocks[0].closed)

    def test_long_closer_tilde_and_indentation(self):
        block = fenced_blocks("   ~~~python\nx = 1\n  ~~~~~\n")[0]
        self.assertEqual(block.language, "python")
        self.assertTrue(block.closed)

    def test_unclosed_fence_and_syntax_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.md"
            path.write_text("~~~python\ndef broken(:\n")
            _, errors = validate(path)
        self.assertTrue(any("UNCLOSED" in error for error in errors))
        self.assertTrue(any("PYTHON SYNTAX" in error for error in errors))

    def test_extractor_does_not_steal_demo_when_prompt_absent(self):
        with self.assertRaises(SystemExit):
            extract_prompt_block("## The prompt\nMissing\n## Try it now\n```text\nDemo\n```\n", "fixture")

    def test_extractor_handles_tilde_prompt(self):
        self.assertEqual(extract_prompt_block("## The prompt\n\n~~~text\nActual\n~~~\n", "fixture"), ("text", "Actual\n"))


class ContainmentTests(unittest.TestCase):
    def check_prompt(self, payload, pairing="Attach `BASE.md`."):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prompts/example/example.md"
            path.parent.mkdir(parents=True)
            path.write_text("# Example\n| **Run-time needs** | None |\n" + pairing + "\n" + payload + "\n<!-- RUNTIME_CONTRACT -->\n")
            return subprocess.run([sys.executable, str(ROOT / "_tooling/validate_self_containment.py"), directory], capture_output=True, text=True)

    def test_valid_pair_passes(self):
        self.assertEqual(self.check_prompt("```text\nAnalyze provided data.\n```\n").returncode, 0)

    def test_multiple_html_companions_rejected(self):
        result = self.check_prompt("```text\nAnalyze.\n```", "Attach `first.html` and `second.html`.")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pairing budget exceeded (3 files)", result.stdout)

    def test_base_and_html_companion_rejected(self):
        self.assertNotEqual(self.check_prompt("```text\nAnalyze.\n```", "Attach `BASE.md` and `first.html`.").returncode, 0)

    def test_same_basename_distinct_paths_rejected(self):
        self.assertNotEqual(self.check_prompt("```text\nAnalyze.\n```", "Attach `one/template.html` and `two/template.html`.").returncode, 0)

    def test_long_fence_does_not_hide_dependency(self):
        result = self.check_prompt("````text\n```\nLoad frameworks/example/rules.json\n````\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RULE A", result.stdout)

    def test_wrong_fence_does_not_hide_dependency(self):
        result = self.check_prompt("```text\n~~~\nLoad teams/example.md\n```\n")
        self.assertNotEqual(result.returncode, 0)

    def test_unclosed_payload_fails(self):
        self.assertNotEqual(self.check_prompt("```text\nAnalyze.").returncode, 0)


class PublicScopeTests(unittest.TestCase):
    def test_runtime_and_private_directories_are_not_frameworks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("engine", "__pycache__", "_lib", ".cache"):
                (root / name).mkdir()
            self.assertEqual([path.name for path in content_directories(root)], ["engine"])

    def test_ignored_local_files_excluded_new_and_tracked_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            subprocess.run(["git", "init", "-q", directory], check=True)
            (root / ".gitignore").write_text("private/\n")
            (root / "private").mkdir()
            (root / "private/local.md").write_text("Local working material")
            (root / "new.md").write_text("New public deliverable")
            (root / "private/published.md").write_text("Already tracked")
            subprocess.run(["git", "-C", directory, "add", "-f", "private/published.md"], check=True)
            actual = {path.relative_to(root).as_posix() for path in public_files(root)}
            self.assertNotIn("private/local.md", actual)
            self.assertIn("new.md", actual)
            self.assertIn("private/published.md", actual)

    def test_public_symlink_rejected_before_reading_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            private = Path(directory) / "private.md"
            private.write_text("SYNTHETIC PRIVATE CONTENT")
            (root / "linked.md").symlink_to(private)
            with self.assertRaisesRegex(ValueError, "Symbolic links"):
                public_files(root)
            result = subprocess.run([sys.executable, str(ROOT / "_tooling/validate_hygiene.py"), str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(private.read_text(), result.stdout + result.stderr)

    def test_hygiene_diagnostics_redact_matching_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic = "gh" + "p_" + "x" * 24
            (root / "example.md").write_text(synthetic)
            result = subprocess.run([sys.executable, str(ROOT / "_tooling/validate_hygiene.py"), str(root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[REDACTED]", result.stdout)
            self.assertNotIn(synthetic, result.stdout + result.stderr)

    def test_archive_scans_documents_without_git(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "readme.md").write_text("Portable source archive")
            self.assertEqual(public_files(root), [root / "readme.md"])


if __name__ == "__main__":
    unittest.main()
