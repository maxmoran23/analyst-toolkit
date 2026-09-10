"""Shared fenced-block reader for prompt generation and validation."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Block:
    language: str
    body: str
    start_line: int
    end_line: int
    closed: bool


def fenced_blocks(text: str) -> list[Block]:
    """Read backtick/tilde fences; only a matching, long-enough fence closes.

    Line numbers are one-based and inclusive. An unclosed fence extends to EOF,
    as in Markdown, but callers can reject it for executable paste payloads.
    """
    lines = text.splitlines(keepends=True)
    blocks: list[Block] = []
    opening = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)[\r\n]*$")
    index = 0
    while index < len(lines):
        match = opening.match(lines[index])
        if not match or (match[1][0] == "`" and "`" in match[2]):
            index += 1
            continue
        fence, info = match.groups()
        start = index
        index += 1
        close = re.compile(r"^ {0,3}" + re.escape(fence[0]) + r"{" + str(len(fence)) + r",}[ \t]*[\r\n]*$")
        while index < len(lines) and not close.match(lines[index]):
            index += 1
        closed = index < len(lines)
        blocks.append(Block(info.strip().split()[0].lower() if info.strip() else "text",
                            "".join(lines[start + 1:index]), start + 1,
                            index + 1 if closed else len(lines), closed))
        index += 1
    return blocks
