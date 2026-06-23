# Model governance framing for the frameworks pillar

Every framework in this pillar is a quantitative model in the regulatory sense, and
is documented to the four pillars of model risk management. This file defines the
framing once; each framework's `METHODOLOGY.md` carries a short section that
instantiates it with that framework's specifics. The framing cites only public
guidance and contains no institution-specific policy.

> **In plain terms:** Regulators expect any scoring model a bank relies on to be
> documented, tested by someone independent, monitored over time, and honest about
> what it cannot do. This page explains how each framework here meets those four
> expectations, and points to the public rules that set them.

## Public guidance referenced

- **SR 11-7** — Federal Reserve / OCC Supervisory Guidance on Model Risk Management.
- **OCC Bulletin 2011-12** — the companion bulletin.
- **FFIEC BSA/AML Examination Manual** — expectations for monitoring and screening
  systems, including that the logic be understood, documented, and tested.
- **FATF Recommendations 15 and 16** — for the blockchain/virtual-asset frameworks.
- **Wolfsberg Group** guidance on sanctions screening control effectiveness and on
  monitoring threshold tuning (above-the-line / below-the-line testing).

This is general domain reference, not legal advice. Confirm the current state of any
rule against the issuing body before relying on it.

## The four pillars, and how each framework evidences them

### 1. Conceptual soundness — *is the method defensible and transparent?*
Evidenced by `METHODOLOGY.md` (every component, weight, threshold, and rule
documented with rationale) and by the engine itself: pure, readable standard-library
Python with no black-box dependency. The methods used (IDF-weighted token
similarity, phonetic matching, identifier corroboration, weighted composites) are
established record-linkage and screening practice. Maps to SR 11-7 / OCC 2011-12
"evaluation of conceptual soundness" and the FFIEC expectation that screening and
monitoring logic be documented and understood.

### 2. Outcomes analysis — *does it perform, and is that shown independently?*
Evidenced by `run_validation.py` and the committed `evidence/`: real metrics on a
labelled synthetic population — recall, false-positive reduction, per-category
breakdown, the threshold-sensitivity sweep, and the volume funnel — reproducible
from seed. The harness *is* the independent test: anyone re-runs it and reproduces
every number. Maps to SR 11-7 "outcomes analysis" and "effective challenge", and to
the Wolfsberg above/below-the-line threshold-testing expectation.

### 3. Ongoing monitoring — *is performance tracked, and does drift trigger action?*
Evidenced by the build-gate invariants in `RIGOR-CONTRACT.md` (the recall floor is
enforced, not asserted), the multi-seed stability runs (the result is not a
single-seed artifact), and each `tuning.md`'s recalibration procedure and cadence.
Maps to SR 11-7 ongoing-monitoring and FFIEC periodic-validation expectations.

### 4. Limitations and assumptions — *are the boundaries stated honestly?*
Evidenced by the mandatory Limitations section in every validation report and the
standing "reference implementation, not production control; recalibrate before
reliance" caveat in every README and `tuning.md`. Maps to the SR 11-7 / OCC 2011-12
requirement that models document their limitations and assumptions, and to this
repository's "honest about gaps" standard.

## The asymmetric-error posture (common to all frameworks)

These are compliance models, where the two error types are not equal in cost:

- A **false negative** (clearing a real hit) is a regulatory and legal failure;
  its tolerated rate is zero.
- A **false positive** (keeping a non-hit) is operational cost; reducing it is the
  value, but never at the expense of the line above.

Accordingly, every framework's auto-clear path is gated on a **named, provable
cause** — never a bare score — and false-negative safety is enforced as a build
gate (a validation run fails if the engine ever auto-clears a labelled true
positive). This is the structural form of "effective challenge": the safety
property is a test the code must pass, not a claim in a document.

## Work boundary

Everything in this pillar is generic and synthetic. Worked examples use fictional
entities (the recurring institution is **Harborview Financial Group**, the recurring
counterparty **Meridian Digital Exchange**). No employer-specific data, no client
names, no non-public information appears anywhere.
