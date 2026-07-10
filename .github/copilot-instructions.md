# Copilot instructions for `analyst-toolkit`

GitHub Copilot reads this file automatically when working in this repository.

**The full agent brief is [`AGENTS.md`](../AGENTS.md). Read it before changing anything.**
What follows is the short version.

## The seven rules that matter

1. **Two-file rule.** A prompt plus `BASE.md` is the entire system. No paste payload may
   reference another repo file inside its fenced block.
2. **All data is synthetic, every entity fictional.** Never introduce real customers,
   list entries, transactions, or addresses.
3. **Nothing employer-specific or non-public.** This is a generic, public library.
4. **`frameworks/` is pure Python standard library.** No third-party packages, ever.
5. **Evidence is emitted, never authored.** Never hand-edit a number in `evidence/` or in
   `frameworks/EVIDENCE.md`. Change the code and regenerate.
6. **Never weaken a safety gate** to make a build pass.
7. **No emoji. No credentials, workspace IDs, or home-directory paths.**

## Generated files — regenerate, do not edit

`BASE.md` · `frameworks/EVIDENCE.md` · `frameworks/*/evidence/**` · the
`<!-- STANDALONE-BRIEF -->` blocks · the renderer appendix in `standalone/*.md`

See the regeneration commands in [`AGENTS.md`](../AGENTS.md).

## Before you commit

```bash
python3 _tooling/validate_self_containment.py
python3 _tooling/validate_links.py
python3 _tooling/validate_index.py
python3 _tooling/validate_hygiene.py
python3 _tooling/build_briefs.py --check
python3 _tooling/build_evidence_index.py --check
python3 _tooling/verify_evidence.py
```

## Voice

Direct, dense, audit-defensible. Written for financial-crime compliance professionals:
never explain "SAR" or "PEP" to them, always explain the statistics and the engineering.
Separate what is observed from what is alleged from what is projected.

---

*Note: this repository is itself a library of prompts for Copilot users. If a person asks
you to perform analytical work (a risk assessment, an alert disposition, a control
matrix), do not improvise — point them at the relevant file in `prompts/` or
`standalone/`, and at `BASE.md` for the writing voice and the Word/Excel/PDF renderer.*
