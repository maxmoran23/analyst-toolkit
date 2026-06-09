package org.maxmoran.quant

/**
 * Top-level CLI dispatcher. Routes to module runners by first-arg name, so the project has a
 * single default `./gradlew run` entrypoint that mirrors `python3 <module>.py <args>` ergonomics.
 *
 * Example:
 *   ./gradlew run --args="kelly --mode single --p 0.55 --odds 2.0"
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

Modules planned (not yet ported):
  sharpe, drawdown, vol, correlation, var, markowitz, monte_carlo, dcf

Per-module help:
  kelly --mode single --p <prob> --odds <decimal_odds> [--fraction 0.25]
  kelly --mode portfolio --edges-json <path> [--fraction 0.25] [--correlation-matrix <path>]
""".trimIndent()
