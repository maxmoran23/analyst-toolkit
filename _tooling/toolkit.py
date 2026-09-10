#!/usr/bin/env python3
"""Discover and assemble the toolkit locally, using only Python's standard library.

Commands work from any directory. Output files are created exclusively; existing
files are never overwritten. No prompts are executed and no network calls occur.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from build_demos import build_block, extract_prompt_block, load_registry

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
SIZE_METHOD = "Exact Unicode characters and UTF-8 bytes; token estimate is ceil(characters / 4), not a tokenizer count."


def measure(text: str) -> dict:
    return {"characters": len(text), "utf8_bytes": len(text.encode("utf-8")),
            "estimated_tokens": math.ceil(len(text) / 4)}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_source(path: Path) -> tuple[str, dict]:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError("Source resolves outside the repository")
    data = resolved.read_bytes()
    return data.decode("utf-8"), {"path": path.relative_to(ROOT).as_posix(),
                                 "sha256": digest(data)}


def fields(text: str) -> dict:
    return {name.casefold(): value.strip() for name, value in
            re.findall(r"^\| \*\*([^*]+)\*\* \| (.*?) \|$", text, re.MULTILINE)}


def inventory() -> list[dict]:
    categories = json.loads((ROOT / "prompts/CATEGORIES.json").read_text(encoding="utf-8"))["categories"]
    entries = []
    groups = [("prompt", (ROOT / "prompts").glob("*/*.md")),
              ("standalone", (ROOT / "standalone").glob("*.md")),
              ("framework", (ROOT / "frameworks").glob("*/README.md"))]
    for kind, paths in groups:
        for path in sorted(paths):
            if path.name == "README.md" and kind != "framework":
                continue
            if path.parent.name.startswith("_"):
                continue
            text, source = read_source(path)
            title = re.search(r"^# (.+)$", text, re.MULTILINE)
            meta = fields(text)
            category = path.parent.name if kind == "prompt" else kind
            identifier = source["path"].removesuffix("/README.md").removesuffix(".md")
            payload = extract_prompt_block(text, source["path"])[1] if kind == "prompt" else text
            summary = meta.get("use when") or next((line[2:] for line in text.splitlines() if line.startswith("> ")), "")
            entry = {"id": identifier, "kind": kind, "category": category,
                     "title": title[1] if title else path.stem,
                     "summary": summary, "produces": meta.get("produces", ""),
                     "audience": categories.get(category, {}).get("audience", ""),
                     "runtime_needs": meta.get("run-time needs", ""),
                     "source": source, "payload_size": measure(payload),
                     "placeholders": list(dict.fromkeys(PLACEHOLDER_RE.findall(payload))),
                     "assembly_supported": kind != "framework",
                     "_text": text, "_payload": payload}
            entries.append(entry)
    return sorted(entries, key=lambda entry: entry["id"])


def public(entry: dict) -> dict:
    return {key: value for key, value in entry.items() if not key.startswith("_")}


def select(entries: list[dict], identifier: str) -> dict:
    identifier = identifier.removesuffix(".md").removesuffix("/README")
    matches = [entry for entry in entries if entry["id"] == identifier]
    if not matches:
        matches = [entry for entry in entries if entry["id"].split("/")[-1] == identifier]
    if len(matches) != 1:
        suffix = ": " + ", ".join(entry["id"] for entry in matches) if matches else ""
        raise ValueError(("Ambiguous ID; use a full catalog ID" if matches else "Unknown catalog ID") + suffix)
    return matches[0]


def payload_for(entry: dict, demo: bool) -> tuple[str, list[dict]]:
    sources = [entry["source"]]
    if not demo:
        return entry["_payload"], sources
    if entry["kind"] != "prompt":
        raise ValueError("--demo is available only for prompts")
    key = entry["source"]["path"].removeprefix("prompts/")
    registry = load_registry()
    if key not in registry:
        raise ValueError("No registered synthetic demo for this prompt")
    _, source = read_source(ROOT / "_tooling/demos" / (entry["category"] + ".json"))
    sources.append(source)
    return build_block(key, entry["_payload"], registry[key]), sources


def assemble(entry: dict, demo: bool, include_base: bool) -> tuple[str, dict]:
    if not entry["assembly_supported"]:
        raise ValueError("Frameworks are runnable engines; use show to read their execution instructions")
    if include_base and entry["kind"] == "standalone":
        raise ValueError("Standalone files already embed their renderer; omit --with-base")
    payload, sources = payload_for(entry, demo)
    if include_base:
        base, source = read_source(ROOT / "BASE.md")
        sources.insert(0, source)
        payload = base.rstrip("\n") + "\n\n---\n\n" + payload
    if not payload.endswith("\n"):
        payload += "\n"
    manifest = {"schema_version": 1, "id": entry["id"], "mode": "synthetic-demo" if demo else "template",
                "with_base": include_base, "input_file_count": 2 if include_base else 1,
                "sources": sources, "payload_sha256": digest(payload.encode("utf-8")),
                "payload_size": measure(payload), "size_method": SIZE_METHOD,
                "remaining_placeholders": list(dict.fromkeys(PLACEHOLDER_RE.findall(payload)))}
    return payload, manifest


def emit(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also rejects existing symlinks, including dangling ones.
    with output.open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="Search the live catalog; all query terms must match")
    listing.add_argument("query", nargs="*", help="Case-insensitive terms matched against title, metadata, and content")
    listing.add_argument("--category")
    listing.add_argument("--kind", choices=("prompt", "standalone", "framework"))
    listing.add_argument("--json", action="store_true", help="Emit deterministic catalog JSON")
    listing.add_argument("--output", type=Path)
    for name in ("show", "assemble"):
        command = commands.add_parser(name, help="Read the canonical payload" if name == "show" else "Export one prompt, optionally combined with BASE")
        command.add_argument("id", help="Full catalog ID, or an unambiguous basename")
        command.add_argument("--demo", action="store_true", help="Fill prompt using the registered fictional demo")
        command.add_argument("--output", type=Path)
        if name == "assemble":
            command.add_argument("--with-base", action="store_true")
            command.add_argument("--json", action="store_true", help="Export an envelope containing payload and reproducibility manifest")
            command.add_argument("--max-chars", type=int, help="Reject payloads larger than this exact character budget")
    return result


def main(argv: list[str] | None = None) -> int:
    cli = parser()
    args = cli.parse_args(argv)
    try:
        entries = inventory()
        if args.command == "list":
            if args.category and args.category not in {entry["category"] for entry in entries}:
                raise ValueError("Unknown category: " + args.category)
            terms = [term.casefold() for word in args.query for term in word.split()]
            entries = [entry for entry in entries if (not args.category or entry["category"] == args.category)
                       and (not args.kind or entry["kind"] == args.kind)
                       and all(term in (json.dumps(public(entry), ensure_ascii=False) + entry["_text"]).casefold() for term in terms)]
            if args.json:
                data = {"schema_version": 1, "count": len(entries), "size_method": SIZE_METHOD,
                        "entries": [public(entry) for entry in entries]}
                output = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            else:
                output = "ID | KIND | PAYLOAD CHARS | TITLE\n" + "\n".join(
                    f"{entry['id']} | {entry['kind']} | {entry['payload_size']['characters']} | {entry['title']}" for entry in entries)
                output += f"\n{len(entries)} result(s). Sizes exclude BASE; framework sizes describe their README.\n"
        else:
            entry = select(entries, args.id)
            if args.command == "show":
                output, _ = payload_for(entry, args.demo)
            else:
                output, manifest = assemble(entry, args.demo, args.with_base)
                if args.max_chars is not None:
                    if args.max_chars < 1:
                        raise ValueError("--max-chars must be positive")
                    if len(output) > args.max_chars:
                        raise ValueError(f"Payload has {len(output)} characters, exceeding budget {args.max_chars}")
                if args.json:
                    output = json.dumps({"manifest": manifest, "payload": output}, ensure_ascii=False, indent=2) + "\n"
                else:
                    print(f"Payload: {len(output)} characters; {manifest['payload_size']['utf8_bytes']} UTF-8 bytes. "
                          f"Remaining placeholders: {len(manifest['remaining_placeholders'])}.", file=sys.stderr)
        emit(output, args.output)
    except (OSError, ValueError, KeyError) as error:
        cli.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
