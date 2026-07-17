package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import java.math.BigDecimal
import java.math.RoundingMode
import kotlin.math.ln
import kotlin.math.max
import kotlin.math.sqrt
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/vol.py` — realized, EWMA, Parkinson, Garman-Klass, and
 * simplified GARCH(1,1). The GARCH is fixed-parameter (alpha=0.10, beta=0.85, no MLE, no
 * RNG), so every function here is deterministic pure math under parity-contract.md §1.1;
 * nothing in this module falls under the §1.3 stochastic regime.
 */

/** One OHLC bar; mirrors the `[open, high, low, close]` arrays accepted by `vol.py`. */
data class OhlcBar(val open: Double, val high: Double, val low: Double, val close: Double)

/** Annualized close-to-close volatility from sample (ddof=1) variance. */
fun realizedVol(returns: List<Double>, annualize: Int = 252): Double {
    val n = returns.size
    if (n < 2) return 0.0
    val mu = returns.sum() / n
    val variance = returns.sumOf { value ->
        val deviation = value - mu
        deviation * deviation
    } / (n - 1)
    return sqrt(variance) * sqrt(annualize.toDouble())
}

/** RiskMetrics-style EWMA; lambda=0.94 is the JPM daily default. */
fun ewmaVol(returns: List<Double>, lam: Double = 0.94, annualize: Int = 252): Double {
    if (returns.isEmpty()) return 0.0
    var variance = returns[0] * returns[0]
    for (i in 1 until returns.size) {
        val r = returns[i]
        variance = lam * variance + (1 - lam) * r * r
    }
    return sqrt(variance) * sqrt(annualize.toDouble())
}

/** Parkinson range estimator from (high, low) pairs; non-positive lows are skipped. */
fun parkinsonVol(highLowPairs: List<Pair<Double, Double>>, annualize: Int = 252): Double {
    if (highLowPairs.isEmpty()) return 0.0
    val k = 1.0 / (4.0 * ln(2.0))
    var varSum = 0.0
    for ((high, low) in highLowPairs) {
        if (low > 0.0) {
            val logRange = lnPositive(high / low)
            varSum += logRange * logRange
        }
    }
    val variance = k * varSum / highLowPairs.size
    return sqrt(variance) * sqrt(annualize.toDouble())
}

/** Garman-Klass OHLC estimator; bars with non-positive open or low are skipped. */
fun garmanKlassVol(ohlc: List<OhlcBar>, annualize: Int = 252): Double {
    if (ohlc.isEmpty()) return 0.0
    var total = 0.0
    for (bar in ohlc) {
        if (bar.open > 0.0 && bar.low > 0.0) {
            val hl = lnPositive(bar.high / bar.low)
            val co = lnPositive(bar.close / bar.open)
            total += 0.5 * hl * hl - (2.0 * ln(2.0) - 1.0) * co * co
        }
    }
    val variance = total / ohlc.size
    return sqrt(max(0.0, variance)) * sqrt(annualize.toDouble())
}

/**
 * Simplified GARCH(1,1) forecast with fixed parameters, matching `simple_garch`.
 *
 * Mirrors the Python error contract exactly: on fewer than 20 returns the result is an
 * `{"error": ...}` object that `vol.py`'s main() merges into its output and still exits 0.
 */
fun simpleGarch(
    returns: List<Double>,
    annualize: Int = 252,
    omega: Double? = null,
    alpha: Double = 0.10,
    beta: Double = 0.85,
): JsonObject {
    val n = returns.size
    if (n < 20) {
        return buildJsonObject { put("error", JsonPrimitive("need >= 20 returns")) }
    }
    val unconditional = returns.sumOf { it * it } / n
    val omegaValue = omega ?: unconditional * (1.0 - alpha - beta)
    var varT = unconditional
    for (r in returns) {
        varT = omegaValue + alpha * r * r + beta * varT
    }
    val forecast = sqrt(varT) * sqrt(annualize.toDouble())
    return buildJsonObject {
        put("garch_annualized_vol_pct", JsonPrimitive(round3(forecast * 100.0)))
        put(
            "current_conditional_vol_pct",
            JsonPrimitive(round3(sqrt(varT) * sqrt(annualize.toDouble()) * 100.0)),
        )
        put("persistence", JsonPrimitive(round4(alpha + beta)))
        put(
            "unconditional_annual_vol_pct",
            JsonPrimitive(round3(sqrt(unconditional * annualize) * 100.0)),
        )
    }
}

/** Match Python's `round(value, 4)` using the same binary-double constructor as [round3]. */
fun round4(value: Double): Double {
    if (value.isNaN() || value.isInfinite()) return value
    return BigDecimal(value).setScale(4, RoundingMode.HALF_EVEN).toDouble()
}

// Python's math.log raises on non-positive input (traceback, exit 1); Kotlin's ln would
// silently return NaN, so the check preserves the no-silent-failure contract.
private fun lnPositive(x: Double): Double {
    if (!(x > 0.0)) throw IllegalArgumentException("log input must be positive, got $x")
    return ln(x)
}

/** Testable result of evaluating the vol CLI contract. */
data class VolCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateVol(args: Array<String>): VolCliResult {
    return try {
        var returnsPath: String? = null
        var ohlcPath: String? = null
        var method = "realized"
        var annualize = 252
        var ewmaLambda = 0.94
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
                "--returns-json" -> returnsPath = optionValue(arg)
                "--ohlc-json" -> ohlcPath = optionValue(arg)
                "--method" -> method = optionValue(arg)
                "--annualize" -> annualize = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--annualize must be an integer")
                "--ewma-lambda" -> ewmaLambda = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--ewma-lambda must be a number")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        fun returns(): List<Double> {
            val path = returnsPath ?: throw IllegalArgumentException("need --returns-json")
            return parseNumberArray(File(path).readText(), "returns")
        }

        fun ohlcText(): String {
            val path = ohlcPath ?: throw IllegalArgumentException("need --ohlc-json")
            return File(path).readText()
        }

        val output = buildJsonObject {
            put("method", JsonPrimitive(method))
            put("annualize_factor", JsonPrimitive(annualize))
            when (method) {
                "realized" ->
                    put("annualized_vol_pct", JsonPrimitive(round3(realizedVol(returns(), annualize) * 100.0)))
                "ewma" -> {
                    put("annualized_vol_pct", JsonPrimitive(round3(ewmaVol(returns(), ewmaLambda, annualize) * 100.0)))
                    put("ewma_lambda", JsonPrimitive(ewmaLambda))
                }
                "parkinson" -> {
                    // Python only indexes bar[1] and bar[2] here, so 3-element bars are accepted.
                    val pairs = parseOhlcBars(ohlcText(), minSize = 3).map { it[1] to it[2] }
                    put("annualized_vol_pct", JsonPrimitive(round3(parkinsonVol(pairs, annualize) * 100.0)))
                }
                "garman_klass" -> {
                    // Python tuple-unpacks each bar into (o, h, l, c) — exactly four values.
                    val bars = parseOhlcBars(ohlcText(), minSize = 4, exactSize = 4)
                        .map { OhlcBar(it[0], it[1], it[2], it[3]) }
                    put("annualized_vol_pct", JsonPrimitive(round3(garmanKlassVol(bars, annualize) * 100.0)))
                }
                "garch" ->
                    simpleGarch(returns(), annualize).forEach { (key, value) -> put(key, value) }
                else -> throw IllegalArgumentException(
                    "invalid --method: $method (choose realized|ewma|parkinson|garman_klass|garch)"
                )
            }
        }
        VolCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(JsonObject.serializer(), output),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        VolCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

private fun parseOhlcBars(text: String, minSize: Int, exactSize: Int? = null): List<List<Double>> {
    val parsed = Json.parseToJsonElement(text)
    if (parsed !is JsonArray) throw IllegalArgumentException("ohlc JSON must be an array of bars")
    return parsed.mapIndexed { index, element ->
        if (element !is JsonArray || element.size < minSize ||
            (exactSize != null && element.size != exactSize)
        ) {
            throw IllegalArgumentException("ohlc bar at index $index has the wrong shape")
        }
        element.map { component ->
            val primitive = component.jsonPrimitive
            if (primitive.isString) {
                throw IllegalArgumentException("ohlc bar at index $index must contain only numbers")
            }
            primitive.content.toDoubleOrNull()?.takeIf { it.isFinite() }
                ?: throw IllegalArgumentException("ohlc bar at index $index must contain finite numbers")
        }
    }
}

/** Module CLI runner — JSON in / JSON out, matching the Python entrypoint. */
fun runVol(args: Array<String>) {
    val result = evaluateVol(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
