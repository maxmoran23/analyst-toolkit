# Financial Analysis

A cheat-sheet for financial modeling and analysis — variance analysis,
reconciliation, financial-statement analysis, scenario modeling, and portfolio
analysis.

For the writing voice and the observed/projected discipline, see
[`../methodology/audit-defensible-writing.md`](../methodology/audit-defensible-writing.md)
and
[`../methodology/analytical-patterns.md`](../methodology/analytical-patterns.md).
The observed-vs-projected split matters here in particular: a forecast reported
as a fact is the most common failure in financial writing.

---

## Variance analysis

Decompose the difference between a budget or forecast and the actual result.

- **Revenue variance** — a price × volume decomposition
- **Expense variance** — a rate × usage decomposition
- A **waterfall chart** showing the walk from budget to actual
- A narrative explanation for each material variance (above a stated threshold —
  for example, greater than 5% or greater than a fixed dollar amount)

Every variance narrative explains *why*, not just *how much*. A number with no
driver is incomplete.

---

## Financial-statement analysis

- **Common-size analysis** — every line as a percentage of revenue or of total
  assets
- **Trend analysis** — a three-to-five-period comparison
- **Ratio analysis** — liquidity, profitability, leverage, efficiency
- **DuPont decomposition** — return on equity broken into margin, turnover, and
  leverage

---

## Scenario modeling

- **Base / bull / bear cases** — three coherent scenarios, each with stated
  assumptions
- **Sensitivity tables** — one-variable and two-variable
- **Monte Carlo simulation** — for a probabilistic distribution of outcomes
  rather than a single point estimate
- **Break-even analysis**

Every scenario is a projection. Label it as one, and state the assumptions that
drive it — a scenario whose assumptions are not visible cannot be evaluated or
challenged.

---

## Portfolio analysis

For an investment or speculative portfolio:

- **Position sizing** — how much capital each position carries, and the framework
  behind it (for example, a fractional-Kelly rule for edge-driven sizing)
- **P&L attribution** — which positions and decisions drove the result
- **Risk metrics** — value-at-risk, drawdown, volatility, the Sharpe and Sortino
  ratios
- **Cross-asset correlation** — how positions move together, and what that does
  to total portfolio risk
- **Total P&L tracking** — performance across the whole book over time

For a betting or edge-driven book specifically: edge analysis (estimated edge
versus realized results), Kelly-based sizing, and bankroll simulation to model
the distribution of outcomes over a long sequence of bets.

---

## Related references

- [`audit-documentation.md`](audit-documentation.md) — reconciliation in a
  control-testing context
- [`../methodology/output-quality-standards.md`](../methodology/output-quality-standards.md)
  — the quality bar for spreadsheet and dashboard deliverables
