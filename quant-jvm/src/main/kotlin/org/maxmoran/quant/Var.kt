package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import java.io.File
import kotlin.math.PI
import kotlin.math.exp
import kotlin.math.floor
import kotlin.math.max
import kotlin.math.sqrt
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/var.py` — historical and parametric (Gaussian) VaR and CVaR.
 *
 * Both methods are deterministic pure math under parity-contract.md §1.1: historical VaR is
 * a sorted-quantile lookup and parametric VaR uses a fixed z-table (no inverse-CDF fit, no
 * RNG). `var.py` ships no Monte Carlo or bootstrap variant, so nothing falls under the §1.3
 * stochastic regime and nothing is deferred.
 */

/** VaR and CVaR as the (1-confidence) quantile of the sorted historical distribution. */
fun historicalVar(returns: List<Double>, confidence: Double): Pair<Double, Double> {
    val sorted = returns.sorted()
    val idx = max(0, floor((1.0 - confidence) * sorted.size).toInt())
    val varValue = -sorted[idx]
    val tail = sorted.subList(0, idx + 1)
    val cvar = -tail.sum() / tail.size
    return varValue to cvar
}

// Fixed z-scores keyed by round(confidence, 3), matching the Python table and its
// 1.645 fallback for any confidence level not in the table.
private val Z_TABLE = mapOf(
    0.90 to 1.282, 0.95 to 1.645, 0.975 to 1.960,
    0.99 to 2.326, 0.995 to 2.576, 0.999 to 3.090,
)

/** Gaussian VaR from sample mean and ddof=1 sigma; understates fat tails by construction. */
fun parametricVar(returns: List<Double>, confidence: Double): Pair<Double, Double> {
    val n = returns.size
    val mean = returns.sum() / n
    val variance = returns.sumOf { value ->
        val deviation = value - mean
        deviation * deviation
    } / (n - 1)
    val sigma = sqrt(variance)
    val z = Z_TABLE[round3(confidence)] ?: 1.645
    val varValue = z * sigma - mean
    val phiZ = exp(-0.5 * z * z) / sqrt(2.0 * PI)
    // Python raises ZeroDivisionError at confidence = 1.0; Kotlin's silent Infinity would
    // break the no-silent-failure contract, so the zero denominator throws instead.
    val denominator = 1.0 - confidence
    if (denominator == 0.0) throw ArithmeticException("float division by zero")
    val cvar = sigma * phiZ / denominator - mean
    return varValue to cvar
}

/** Public rounded JSON value contract, field-for-field with `quant/var.py`. */
fun varOutput(
    returns: List<Double>,
    confidence: Double = 0.95,
    method: String = "both",
    portfolioValue: Double = 1.0,
): JsonObject = buildJsonObject {
    put("confidence", JsonPrimitive(confidence))
    put("n_observations", JsonPrimitive(returns.size))
    put("portfolio_value", JsonPrimitive(portfolioValue))
    if (method == "historical" || method == "both") {
        val (v, c) = historicalVar(returns, confidence)
        put("historical", methodBlock(v, c, portfolioValue))
    }
    if (method == "parametric" || method == "both") {
        val (v, c) = parametricVar(returns, confidence)
        put("parametric", methodBlock(v, c, portfolioValue))
    }
    val mean = returns.sum() / returns.size
    put("stats", buildJsonObject {
        put("mean_pct", JsonPrimitive(round4(mean * 100.0)))
        put("worst_day_pct", JsonPrimitive(round4(returns.min() * 100.0)))
        put("best_day_pct", JsonPrimitive(round4(returns.max() * 100.0)))
    })
}

private fun methodBlock(varValue: Double, cvar: Double, portfolioValue: Double): JsonObject =
    buildJsonObject {
        put("var_pct", JsonPrimitive(round4(varValue * 100.0)))
        put("cvar_pct", JsonPrimitive(round4(cvar * 100.0)))
        put("var_dollar", JsonPrimitive(round2(varValue * portfolioValue)))
        put("cvar_dollar", JsonPrimitive(round2(cvar * portfolioValue)))
    }

/** Testable result of evaluating the VaR CLI contract. */
data class VarCliResult(val exitCode: Int, val output: String)

/**
 * Parse input and produce CLI output without terminating the process.
 *
 * [stdinText] is injectable for tests; when null, `--stdin` reads the real standard input.
 */
fun evaluateVar(args: Array<String>, stdinText: String? = null): VarCliResult {
    return try {
        var useStdin = false
        var returnsPath: String? = null
        var confidence = 0.95
        var method = "both"
        var portfolioValue = 1.0
        var index = 0

        fun optionValue(option: String): String {
            if (index + 1 >= args.size || args[index + 1].startsWith("--")) {
                throw IllegalArgumentException("$option requires a value")
            }
            index += 1
            return args[index]
        }

        while (index < args.size) {
            when (val arg = args[index]) {
                "--stdin" -> useStdin = true
                "--returns-json" -> returnsPath = optionValue(arg)
                "--confidence" -> confidence = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--confidence must be a number")
                "--method" -> method = optionValue(arg)
                "--portfolio-value" -> portfolioValue = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--portfolio-value must be a number")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }
        if (method !in listOf("historical", "parametric", "both")) {
            throw IllegalArgumentException("invalid --method: $method (choose historical|parametric|both)")
        }

        // Same precedence as Python: --stdin wins if both input flags are supplied.
        val text = when {
            useStdin -> stdinText ?: System.`in`.bufferedReader().readText()
            returnsPath != null -> File(returnsPath).readText()
            else -> throw IllegalArgumentException("must supply --returns-json or --stdin")
        }
        val returns = parseNumberArray(text, "returns")
        if (returns.size < 20) {
            throw IllegalArgumentException("need at least 20 return observations")
        }
        VarCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(
                JsonObject.serializer(),
                varOutput(returns, confidence, method, portfolioValue),
            ),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        VarCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — JSON in / JSON out, matching the Python entrypoint. */
fun runVar(args: Array<String>) {
    val result = evaluateVar(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
