"""Enumerate publishable files without scanning ignored local working material."""
from pathlib import Path
import subprocess

ARCHIVE_IGNORES = {".git", "__pycache__", "node_modules", ".venv", "venv", ".gradle"}


def public_files(root: Path) -> list[Path]:
    """Include tracked files plus new nonignored files; support ZIP checkouts.

    Tracked files remain in scope even if a later ignore rule matches them.
    Gitignore matching is delegated to Git rather than approximated. Archives
    have no Git index, so all files outside runtime caches are inspected.
    """
    root = root.resolve()
    try:
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True)
    except FileNotFoundError:
        top = None
    if top is not None and top.returncode == 0 and Path(top.stdout.strip()).resolve() == root:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others",
                                 "--exclude-standard", "-z"], capture_output=True)
        if result.returncode:
            raise RuntimeError("Cannot enumerate repository files: " + result.stderr.decode(errors="replace"))
        paths = {root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item}
    else:
        paths = {path for path in root.rglob("*")
                 if not any(part in ARCHIVE_IGNORES for part in path.relative_to(root).parts)}
    for path in sorted(paths):
        # A public symlink can target private ignored material even inside the root.
        # Never follow it into a validator or disclose its destination in an error.
        if any(part.is_symlink() for part in [path, *path.parents] if part != root and root in part.parents):
            raise ValueError(f"Symbolic links are not publishable source files: {path.relative_to(root)}")
    return sorted(path for path in paths if path.is_file())
