package org.maxmoran.quant

/**
 * Top-level CLI dispatcher. Routes to module runners by first-arg name, so the project has a
 * single default `./gradlew run` entrypoint that mirrors `python3 <module>.py <args>` ergonomics.
 *
 * Example:
 *   ./gradlew run --args="kelly --mode single --p 0.55 --odds 2.0"
 *   ./gradlew run --args="sharpe --returns-json returns.json --rf 0.05 --annualize 252"
 */
fun main(args: Array<String>) {
    if (args.isEmpty()) {
        println(USAGE)
        return
    }
    val module = args[0]
    val rest = args.drop(1).toTypedArray()
    when (module) {
        "kelly" -> runKelly(rest)
        "sharpe" -> runSharpe(rest)
        "drawdown" -> runDrawdown(rest)
        "vol" -> runVol(rest)
        "correlation" -> runCorrelation(rest)
        "var" -> runVar(rest)
        "markowitz" -> runMarkowitz(rest)
        "dcf" -> runDcf(rest)
        "--help", "-h", "help" -> println(USAGE)
        else -> {
            System.err.println("unknown module: $module")
            System.err.println(USAGE)
            kotlin.system.exitProcess(2)
        }
    }
}

private val USAGE = """
quant-jvm — Kotlin port of analyst-toolkit/quant/

Usage: <module> [args...]

Modules implemented:
  kelly       Kelly criterion (single + portfolio)
  sharpe      Sharpe, Sortino, Calmar, and Omega ratios
  drawdown    Max drawdown, underwater curve, recovery episodes
  vol         Realized, EWMA, Parkinson, Garman-Klass, simplified GARCH(1,1)
  correlation Full-sample, crisis-only, and rolling pairwise correlation
  var         Historical and parametric (Gaussian) VaR and CVaR
  markowitz   Min-variance, max-Sharpe, and equal-weight portfolios
  dcf         Token fee-capture DCF with scenarios and sensitivity

Modules planned (not yet ported):
  monte_carlo

Per-module help:
  kelly --mode single --p <prob> --odds <decimal_odds> [--fraction 0.25]
  kelly --mode portfolio --edges-json <path> [--fraction 0.25] [--correlation-matrix <path>]
  sharpe (--returns-json <path> | --stdin) [--rf 0.05] [--annualize 252]
  drawdown (--equity-json <path> | --returns-json <path>) [--top-n 5]
  vol --method realized|ewma|parkinson|garman_klass|garch (--returns-json <path> | --ohlc-json <path>) [--annualize 252] [--ewma-lambda 0.94]
  correlation --returns-csv <path> [--asset-names a,b,c] [--window 30] [--crisis-threshold -0.05]
  var (--returns-json <path> | --stdin) [--confidence 0.95] [--method historical|parametric|both] [--portfolio-value 1.0]
  markowitz --returns-csv <path> [--asset-names a,b,c] [--rf 0.05] [--annualize 252]
  dcf --fees-yearly <json_array> --circulating-supply <tokens> [--discount 0.15] [--terminal-growth 0.03] [--capture-ratio 1.0] [--current-price <p>]
""".trimIndent()
