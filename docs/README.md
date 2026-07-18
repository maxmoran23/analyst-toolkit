# Guides — how to use this library, and how to judge it

These guides. The first is the one to read if you only read one.

| Guide | Who it's for | What it answers |
|---|---|---|
| **[How the system works](how-the-system-works.md)** | Senior reviewers, examiners, anyone being asked to trust this | What is this, what can it and can it not do, and why should its results be believed? Written in plain English, no code, no prompts. |
| [Using with Copilot](using-with-copilot.md) | Anyone on a locked-down work machine | The copy/paste loop end to end — how to get a prompt into Copilot and a clean Word/Excel/PDF file back out. |
| [Running on any assistant](running-on-any-assistant.md) | Claude, ChatGPT, or Copilot users | Why every prompt is assistant-agnostic, and how it degrades gracefully when a capability is missing. |
| [Methodology as base](methodology-as-base.md) | Anyone setting the library up once, then using thin prompts forever | How to load the methodology as your assistant's standing instructions so every later task is a one-line request. |
| [What am I looking at?](prompt-vs-engine-map.md) | Anyone unsure why two files have similar names | Which folder is which artifact class, and the prompt↔engine "cousin" pairs — same subject, one works a case, one triages a queue. |

## The short version

You do not install this library. You copy a page of instructions out of it and paste
that page into an AI assistant you already have. The instructions carry the analytical
method, the scoring rubric, the required output structure, and the quality bar — so the
result comes back structured, sourced, and comparable to what a colleague would get from
the same prompt.

A small part of the library is different: [`frameworks/`](../frameworks/) holds fifteen
runnable scoring engines for the high-volume problems (triaging tens of thousands of
alerts). Those you run rather than paste, and each one publishes evidence of exactly how
accurate it is — evidence an automated check re-derives from scratch on every change to
this repository. If you are the person who has to sign off, start with
[`frameworks/EVIDENCE.md`](../frameworks/EVIDENCE.md).

Nothing here connects to a bank system, blocks a payment, or files a report. It drafts,
scores, and documents; a qualified person decides. All test data is synthetic and every
entity is fictional.
