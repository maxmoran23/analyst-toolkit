# `workspace/` — configure and automate your AI workspace

Most of this library makes an assistant *do* a piece of analytical work. This category is
different: it makes your *tools* work better. These prompts configure the assistant you
already use and design the automation around it — so the environment is tuned once and
every later task starts from a better place.

Nothing here is domain-specific. It is generic productivity and setup tooling: safe on
any machine, useful to any analyst.

| Prompt | What it does |
|--------|--------------|
| [custom-instructions-architect](custom-instructions-architect.md) | Deep-indexes your role, work, and delivery preferences, then writes an optimized custom-instructions statement to paste into your assistant's settings |
| [outlook-copilot-automation](outlook-copilot-automation.md) | Designs an inbox automation — priority model, category taxonomy, native Outlook rules, and a Copilot triage block — that sorts and surfaces mail without ever deleting or sending |

Both follow the same rules as the rest of the library: they run standalone, ask before
guessing, encode your hard constraints exactly, and stop at design or draft — a person
applies the result.
