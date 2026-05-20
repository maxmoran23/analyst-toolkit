# Audit Documentation

A cheat-sheet for internal-audit and SOX-style control work — testing
workpapers, sample selection, control assessment, deficiency classification, and
audit-trail documentation.

For severity and the observed/alleged discipline, see
[`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md).
For the writing voice, see
[`../methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md).

---

## Testing workpaper

The core artifact of control testing — a single workpaper documents one control,
how it was tested, and the conclusion.

```
WORKPAPER: [WP-XXX]
CONTROL:   [Control ID] — [Control name]
PROCESS:   [Business process]
OBJECTIVE: [What the control is designed to prevent or detect]

CONTROL DESCRIPTION
[A detailed description of how the control operates.]

TESTING METHODOLOGY
- Test type:        [Inquiry / Observation / Inspection / Reperformance]
- Population:       [Description of the full population]
- Sample size:      [N] (basis: [statistical / judgmental])
- Sample selection: [Random / Systematic / Haphazard]
- Period:           [Testing period]

TESTING PROCEDURES
1. [Step 1]
2. [Step 2]
3. [Step 3]

RESULTS
| Sample # | Date | Description | Result | Exception? | Notes |
|----------|------|-------------|--------|------------|-------|

CONCLUSION
- Exceptions identified:        [X of N]
- Control operating effectively: [YES / NO]
- Deficiency classification:     [None / Deficiency / Significant Deficiency /
                                  Material Weakness]

PREPARED BY: [Name] | DATE: [Date]
REVIEWED BY: [Name] | DATE: [Date]
```

---

## Sample selection

Document the basis for the sample before testing begins — sample size and method
must be defensible on their own.

```
SAMPLE SELECTION MEMO
Control:           [Control ID]
Population:        [Description, size, source]
Confidence level:  [90% / 95%]
Expected error rate: [0-5%]
Sample size:       [Per recognized sampling tables or a statistical formula]
Selection method:  [Random number generator / Systematic / Monetary-unit sampling]
Items selected:    [Listed or referenced]
```

---

## Deficiency classification

Every control failure is classified by how severe a misstatement it could allow.
The classification drives reporting and remediation urgency.

| Level | Definition | Criteria |
|-------|-----------|----------|
| **Deficiency** | The control does not reliably prevent or detect errors | A single exception; compensating controls exist |
| **Significant Deficiency** | A reasonable possibility of a material misstatement | Multiple exceptions; weak compensating controls |
| **Material Weakness** | A reasonable possibility of a material misstatement that would not be prevented or detected | Pervasive exceptions; no compensating controls |

---

## Audit trail

For every audit finding, document the full chain of reasoning. The five-element
structure (condition, criteria, cause, effect, recommendation) is the standard
backbone; the last two elements close the loop with management.

For every finding:

1. **Condition** — what was found
2. **Criteria** — what should have happened (the standard, the policy, the
   control objective)
3. **Cause** — why the gap exists
4. **Effect** — what the impact is, quantified where possible
5. **Recommendation** — how to fix it
6. **Management response** — management's plan
7. **Remediation timeline** — when the fix will be complete, and who owns it

State the criteria before the condition where the document allows — the reader
needs the benchmark to judge the finding. Keep the condition (observed fact)
visibly separate from the cause (often an inference); label inference as
inference.

---

## Related references

- [`compliance-documents.md`](compliance-documents.md) — control matrices, risk
  assessments, policy documents
- [`financial-analysis.md`](financial-analysis.md) — variance analysis,
  reconciliation, financial-statement analysis
