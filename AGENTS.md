# AGENTS.md — instructions for AI tooling working in this repository

This file is for **coding agents and AI assistants** (Claude Code, GitHub Copilot,
Cursor, and similar) operating on this repository. Humans should read
[`README.md`](README.md) instead — it is written for a different audience and optimised
for a different job.

If you are an agent: read this file before changing anything. It is short on purpose.

---

## What this repository is

A reference library for AI-assisted analytical work at financial institutions, covering
every function of a financial-crime organization. Three artifact classes:

| Class | Path | What it is | Rules that apply |
|---|---|---|---|
| **Paste payloads** | `prompts/`, `standalone/`, `BASE.md`, `methodology/` | Text a human copies into an AI assistant | The two-file rule (below) |
| **Runnable engines** | `frameworks/` | Deterministic pure-stdlib scoring engines with reproducible evidence | The rigor contract (below) |
| **Navigation & reference** | `teams/`, `docs/`, `reference/`, `samples/`, `output-templates/` | Orientation over the above | Standalone-readability (below) |

Also: `quant/` (dependency-free Python quant primitives) and `quant-jvm/` (Kotlin port,
parity-tested against it).

---

## Hard invariants — do not break these

1. **The two-file rule.** Any feature must replicate with at most one prompt file plus
   `BASE.md`. No paste payload may reference another repository file *inside its fenced
   block*. Enforced by `_tooling/validate_self_containment.py`.

2. **All data is synthetic; all entities are fictional.** The recurring institution is
   "Harborview Financial Group"; the recurring counterparty is "Meridian Digital
   Exchange". Never introduce a real customer, list entry, transaction, or address into
   evidence, fixtures, or examples. Public-list *parsers* may fetch at run time, but the
   repository redistributes no list data.

3. **Nothing employer-specific, nothing non-public.** This is a generic, public
   methodology library. No employer name, no internal data, no client names.

4. **`frameworks/` is pure Python standard library.** No numpy, no pandas, no
   third-party package of any kind — including `defusedxml`. If you need a capability,
   implement it in `frameworks/_lib/` or do without. The engines must run unchanged on a
   locked-down machine.

5. **Evidence is emitted, never authored.** No number in any `evidence/` directory or in
   `frameworks/EVIDENCE.md` may be typed by hand. If a figure needs to change, change
   the code and regenerate.

6. **Safety gates are structural.** Each harness exits non-zero if its engine ever
   auto-clears a labelled true positive, rates a hard-risk case low, or passes a
   critically deficient item. Never weaken a gate to make a build pass.

7. **No emoji, and no leak shapes** (Slack IDs, home-directory paths, credentials).
   Enforced by `_tooling/validate_hygiene.py`.

---

## Generated files — never hand-edit

Editing these is always a mistake; regenerate instead. CI fails if they drift.

| File | Regenerate with |
|---|---|
| `BASE.md` | `python3 _tooling/build_base.py` |
| `frameworks/EVIDENCE.md` | `python3 _tooling/build_evidence_index.py` |
| `frameworks/*/evidence/**` | the framework's command in `frameworks/REPRODUCE.json` |
| The `<!-- STANDALONE-BRIEF -->` block on every `frameworks/*/README.md` and `prompts/*/README.md` | `python3 _tooling/build_briefs.py` |
| The renderer appendix in `standalone/*.md` | `python3 _tooling/append_renderer.py .` |
| The `**Run-time needs**` row + `<!-- RUNTIME_CONTRACT -->` footer in every prompt | `python3 _tooling/apply_runtime_contract.py` |

Everything *outside* the `STANDALONE-BRIEF` markers is hand-written and yours to edit.

---

## Single sources of truth

Change the registry, not the twelve places downstream of it.

| Registry | Governs |
|---|---|
| `frameworks/REPRODUCE.json` | Each framework's reproduction command, its positive class, and its audience brief. Read by `verify_evidence.py`, `build_evidence_index.py`, `build_briefs.py`. |
| `prompts/CATEGORIES.json` | Each prompt category's audience brief. |
| `methodology/` (4 files) | The content of `BASE.md`. |
| `methodology/report-templates.md` | The renderer embedded in every `standalone/` file. |

---

## Run the gates before you commit

All are pure stdlib and fast. CI runs exactly these.

```bash
python3 _tooling/validate_self_containment.py    # two-file rule
python3 _tooling/build_base.py --check           # BASE.md in sync
python3 _tooling/validate_embedded.py standalone # fenced code parses
python3 _tooling/validate_embedded.py methodology
python3 _tooling/validate_links.py               # every relative link resolves
python3 _tooling/validate_index.py               # indexes + declared counts match disk
python3 _tooling/validate_hygiene.py             # leak shapes, emoji
python3 _tooling/build_briefs.py --check         # standalone briefs current
python3 _tooling/build_evidence_index.py --check # EVIDENCE.md current
python3 _tooling/verify_evidence.py              # all 13 evidence packs re-derive (~20s)
```

If `verify_evidence.py` fails, the committed evidence no longer matches what the code
produces. Regenerate the pack; do not edit the report.

---

## Where to make a change

| You want to… | Do this |
|---|---|
| Add a prompt | Create `prompts/<category>/<name>.md`, run `apply_runtime_contract.py`, add it to `prompts/README.md` and the root `README.md` catalog, bump the counts those files declare. `validate_index.py` will tell you exactly what you missed. |
| Add a prompt category | Also add an entry to `prompts/CATEGORIES.json`, then `build_briefs.py`. |
| Add a framework | Ship the full package standard (README, METHODOLOGY, engine, generator, harness, tuning, DEPLOYMENT, evidence). Register it in `frameworks/REPRODUCE.json` with a `brief`. Add a CI step. `validate_index.py` enforces the file set. |
| Change an engine's behaviour | Regenerate its evidence pack, then `build_evidence_index.py`. Expect the numbers to move; that is the point. |
| Change a headline number | You cannot. Change the code. |
| Restate an accuracy claim | Include its exact confidence bound — see `frameworks/_lib/attest.py`. "Recall 1.0" without a sample size is not a claim this repository makes. |

---

## Voice

Direct, dense, audit-defensible. Tables for comparisons. No marketing language, no
hedging on benign statements, no trailing summaries. Distinguish *observed* from
*alleged* from *projected*, always. Vendor and self-reported claims are untrusted until
evidenced.

Write for a financial-crime compliance professional: they do not need "SAR" or "PEP"
explained, and doing so reads as condescending. They do need the statistics and the
engineering in plain language — explain a confidence bound, not a suspicious activity
report.

---

## What not to do

- Do not add a dependency to `frameworks/` or `quant/`.
- Do not weaken or bypass a safety gate, a validator, or a CI job to get a green build.
- Do not hand-edit generated files, or the numbers in an evidence pack.
- Do not add real data of any kind, from any source.
- Do not claim a capability the code does not have. If a parser cannot be verified
  against a real published document, register the source **without** a parser and say
  why — that is what `EU_CFSP` does in `frameworks/_lib/knowledge_base/sources.py`.
