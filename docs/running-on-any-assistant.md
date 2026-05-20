# Running on any assistant

Every prompt in this toolkit is built to run on any capable AI assistant — GitHub Copilot, Microsoft 365 Copilot, Claude, ChatGPT, or another — with no setup, no integration, and no dependence on a particular product's features. This document explains how that works and what to expect when a capability is, or is not, available.

---

## The prompts assume nothing

The prompt templates are deliberately built to depend on nothing beyond the assistant reading them and the material you provide:

- **No specific assistant.** No prompt instructs the model to "use Claude" or any other named product. Each names a role ("You are a ...") and a method; any capable assistant can execute it.
- **No memory or persistence.** No prompt assumes the assistant remembers a prior run, an earlier conversation, or anything across sessions. Where continuity matters — a regulatory scan that should not repeat last week's items, a monitor tracking deltas — the prompt has an explicit `PRIOR OUTPUT` (or similarly named) paste-in field. **You** supply the continuity; the assistant is never asked to recall it.
- **No tools or integrations.** No prompt requires web access, a plugin, an extension, a database, or a live data feed. Each has a `PROVIDED MATERIAL` slot — or takes your material as its main input — so it runs entirely from what you paste in.
- **No repository or file structure.** Each prompt is one self-contained block. Pasted into an assistant, it references no other file, no folder layout, and not this repository.

That is the whole point of the copy/paste design: a prompt is portable because it carries its entire method inside one block of text.

---

## Graceful degradation — when a capability is missing

Some prompts can do **more** when the assistant happens to have a capability — live web access to gather fresh data, document reading to ingest a filing. Every prompt is written so that capability is a bonus, never a requirement. Two standing rules in each prompt's `## Rules` block govern this:

1. **Runs standalone.** Provided material is the primary evidence base; live access only supplements; anything not established from the material or a cited source is marked an explicit gap.
2. **Capability fallback.** If a step needs something the assistant cannot do, or a required input is missing, it does not fail silently and does not fabricate — it states what is missing and either proceeds with what it has (marking the gap) or asks you for the specific input it needs.

The result: the same prompt produces a complete, honest, standardized output whether it is run by a fully-tooled agent or a plain chat window with no web access. A more capable assistant fills more in itself; a less capable one tells you exactly what to hand it. **Neither fabricates, and neither stalls.**

---

## The clarification protocol

When a prompt needs something it cannot get, it asks — and it is instructed to ask *well*: briefly, specifically, as a short labeled list, never a vague "can you tell me more." A typical clarification looks like this:

> I can complete this assessment, but three inputs would materially improve it:
> 1. **Registry filing** — the entity's incorporation document, to confirm ownership.
> 2. **Recent financials** — any audited statement from the last two years.
> 3. **Primary jurisdiction** — the main operating country, to score geographic risk.
>
> I will proceed now with what is available and mark these as gaps. Paste any of them and I will revise.

You paste what you can; the assistant revises. Nothing stalls waiting on a system, and nothing is invented to paper over the gap.

---

## Capability quick-reference

| Capability | If the assistant has it | If it does not |
|---|---|---|
| Live web access | Gathers fresh data to supplement your material | Works from `PROVIDED MATERIAL`; marks anything unverifiable as a gap |
| Document / image reading | Ingests an attached file directly | Paste the document text into `PROVIDED MATERIAL` |
| Cross-session memory | Not used by any prompt | Not needed — continuity is the `PRIOR OUTPUT` paste-in |
| A specific data feed or tool | May use it to enrich a finding | Paste the data; the prompt scores what you give it |

---

## What this means for you

Pick whichever assistant is in front of you. Paste the prompt. Paste your data. You get the same standardized, audit-defensible deliverable. If the assistant needs more, it tells you plainly and specifically. That is the entire design — and it is why these prompts move cleanly between a personal machine and a managed work environment without rework.

For turning a prompt you use often into a saved, named tool, see [using-with-copilot.md](using-with-copilot.md).
