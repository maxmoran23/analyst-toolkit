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
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sqrt
import kotlin.system.exitProcess


private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/sharpe.py`.
 *
 * Raw functions intentionally retain the Python operation order so the parity tests can
 * compare unrounded doubles. [sharpeOutput] is the public JSON contract and applies the same
 * half-even display rounding as Python's `round`.
 */

/** Arithmetic mean; Python's reference returns 0.0 for an empty list. */
fun mean(xs: List<Double>): Double = if (xs.isEmpty()) 0.0 else xs.sum() / xs.size

/** Sample standard deviation, matching `stdev(xs, ddof=1)` in the Python reference. */
fun sampleStandardDeviation(xs: List<Double>, ddof: Int = 1): Double {
    if (xs.size < 2) return 0.0
    // Python's float summation returns an exact common value for a constant
    // sequence; preserve the resulting zero-volatility contract explicitly.
    if (xs.all { it == xs[0] }) return 0.0
    val average = mean(xs)
    val squaredDeviations = xs.sumOf { value ->
        val deviation = value - average
        deviation * deviation
    }
    return sqrt(squaredDeviations / (xs.size - ddof))
}

/** Root-mean-square shortfall below [target], including zero shortfalls in the denominator. */
fun downsideDeviation(xs: List<Double>, target: Double = 0.0): Double {
    if (xs.isEmpty()) return 0.0
    val squaredShortfalls = xs.sumOf { value ->
        val shortfall = min(0.0, value - target)
        shortfall * shortfall
    }
    return sqrt(squaredShortfalls / xs.size)
}

/** Maximum peak-to-trough drawdown as a positive fraction. */
fun maxDrawdown(returns: List<Double>): Double {
    var equity = 1.0
    var peak = equity
    var maximum = 0.0
    for (value in returns) {
        equity *= 1.0 + value
        peak = max(peak, equity)
        maximum = max(maximum, (peak - equity) / peak)
    }
    return maximum
}

/** Annualized Sharpe ratio from periodic mean excess return and sample volatility. */
fun sharpeRatio(meanExcess: Double, volatility: Double, annualize: Int): Double =
    if (volatility > 0.0) (meanExcess / volatility) * sqrt(annualize.toDouble()) else 0.0

/** Annualized Sortino ratio from periodic mean excess return and downside deviation. */
fun sortinoRatio(meanExcess: Double, downside: Double, annualize: Int): Double =
    if (downside > 0.0) (meanExcess / downside) * sqrt(annualize.toDouble()) else 0.0

/** Calmar ratio from CAGR and maximum drawdown. */
fun calmarRatio(cagr: Double, drawdown: Double): Double =
    if (drawdown > 0.0) cagr / drawdown else 0.0

/** Omega ratio at a periodic threshold; positive infinity means no observations below it. */
fun omegaRatio(returns: List<Double>, threshold: Double): Double {
    val gains = returns.sumOf { max(0.0, it - threshold) }
    val losses = returns.sumOf { max(0.0, threshold - it) }
    return if (losses > 0.0) gains / losses else Double.POSITIVE_INFINITY
}

/** Unrounded values used to construct the public report and exercise language parity. */
data class SharpeRawMetrics(
    val nPeriods: Int,
    val annualizeFactor: Int,
    val riskFreeRate: Double,
    val periodicRiskFreeRate: Double,
    val meanExcessReturn: Double,
    val annualizedVolatility: Double,
    val cagr: Double,
    val sharpe: Double,
    val sortino: Double,
    val calmar: Double,
    val omega: Double,
    val maximumDrawdown: Double,
    val winRate: Double,
    val averageWin: Double,
    val averageLoss: Double,
    val profitFactor: Double,
)

/** Calculate every unrounded value in `sharpe.py` using the same sequencing. */
fun calculateSharpeMetrics(
    returns: List<Double>,
    riskFreeRate: Double = 0.05,
    annualize: Int = 252,
): SharpeRawMetrics {
    require(returns.size >= 30) { "need >= 30 periods" }
    require(annualize > 0) { "annualize must be positive" }
    require(riskFreeRate.isFinite()) { "risk-free rate must be finite" }
    require(returns.all { it.isFinite() }) { "returns must contain only finite numbers" }

    val periodicRiskFreeRate = (1.0 + riskFreeRate).pow(1.0 / annualize) - 1.0
    val excess = returns.map { it - periodicRiskFreeRate }
    val meanExcess = mean(excess)
    val volatility = sampleStandardDeviation(excess)
    val downside = downsideDeviation(returns, periodicRiskFreeRate)

    var totalReturn = 1.0
    for (value in returns) totalReturn *= 1.0 + value
    val cagr = totalReturn.pow(annualize.toDouble() / returns.size) - 1.0
    val maximumDrawdown = maxDrawdown(returns)

    val wins = returns.count { it > 0.0 }
    val positiveReturns = returns.filter { it > 0.0 }
    val negativeReturns = returns.filter { it < 0.0 }
    val positiveSum = positiveReturns.sum()
    val negativeSum = negativeReturns.sum()

    return SharpeRawMetrics(
        nPeriods = returns.size,
        annualizeFactor = annualize,
        riskFreeRate = riskFreeRate,
        periodicRiskFreeRate = periodicRiskFreeRate,
        meanExcessReturn = meanExcess,
        annualizedVolatility = volatility * sqrt(annualize.toDouble()),
        cagr = cagr,
        sharpe = sharpeRatio(meanExcess, volatility, annualize),
        sortino = sortinoRatio(meanExcess, downside, annualize),
        calmar = calmarRatio(cagr, maximumDrawdown),
        omega = omegaRatio(returns, periodicRiskFreeRate),
        maximumDrawdown = maximumDrawdown,
        winRate = wins.toDouble() / returns.size,
        averageWin = if (wins > 0) mean(positiveReturns) else 0.0,
        averageLoss = if (returns.size - wins > 0) mean(negativeReturns) else 0.0,
        profitFactor = if (negativeReturns.isNotEmpty()) {
            kotlin.math.abs(positiveSum / negativeSum)
        } else {
            Double.POSITIVE_INFINITY
        },
    )
}

/** Public rounded JSON value contract, field-for-field with `quant/sharpe.py`. */
fun sharpeOutput(
    returns: List<Double>,
    riskFreeRate: Double = 0.05,
    annualize: Int = 252,
): JsonObject {
    val raw = calculateSharpeMetrics(returns, riskFreeRate, annualize)
    return buildJsonObject {
        put("n_periods", JsonPrimitive(raw.nPeriods))
        put("annualize_factor", JsonPrimitive(raw.annualizeFactor))
        put("risk_free_rate", JsonPrimitive(raw.riskFreeRate))
        put("cagr_pct", JsonPrimitive(round3(raw.cagr * 100.0)))
        put("annualized_vol_pct", JsonPrimitive(round3(raw.annualizedVolatility * 100.0)))
        put("sharpe", JsonPrimitive(round3(raw.sharpe)))
        put("sortino", JsonPrimitive(round3(raw.sortino)))
        put("calmar", JsonPrimitive(round3(raw.calmar)))
        put("omega", finiteOrInf(raw.omega, 3))
        put("max_drawdown_pct", JsonPrimitive(round3(raw.maximumDrawdown * 100.0)))
        put("win_rate_pct", JsonPrimitive(round2(raw.winRate * 100.0)))
        put("avg_win_pct", JsonPrimitive(round3(raw.averageWin * 100.0)))
        put("avg_loss_pct", JsonPrimitive(round3(raw.averageLoss * 100.0)))
        put("profit_factor", finiteOrInf(raw.profitFactor, 3))
    }
}

/** Match Python's `round(value, 2)` using the same binary-double constructor as [round3]. */
fun round2(value: Double): Double {
    if (value.isNaN() || value.isInfinite()) return value
    return BigDecimal(value).setScale(2, RoundingMode.HALF_EVEN).toDouble()
}

private fun finiteOrInf(value: Double, scale: Int): JsonPrimitive =
    if (value.isInfinite()) JsonPrimitive("inf")
    else JsonPrimitive(BigDecimal(value).setScale(scale, RoundingMode.HALF_EVEN).toDouble())

/** Testable result of evaluating the Sharpe CLI contract. */
data class SharpeCliResult(val exitCode: Int, val output: String)

/**
 * Parse input and produce CLI output without terminating the process.
 *
 * [stdinText] is injectable for tests; when null, `--stdin` reads the real standard input.
 */
fun evaluateSharpe(args: Array<String>, stdinText: String? = null): SharpeCliResult {
    return try {
        var useStdin = false
        var returnsPath: String? = null
        var riskFreeRate = 0.05
        var annualize = 252
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
                "--rf" -> riskFreeRate = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--rf must be a number")
                "--annualize" -> annualize = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--annualize must be an integer")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        val text = when {
            useStdin -> stdinText ?: System.`in`.bufferedReader().readText()
            returnsPath != null -> File(returnsPath).readText()
            else -> throw IllegalArgumentException("need --returns-json or --stdin")
        }
        val parsed = Json.parseToJsonElement(text)
        if (parsed !is JsonArray) throw IllegalArgumentException("returns JSON must be an array")
        val returns = parsed.mapIndexed { itemIndex, element ->
            val primitive = element.jsonPrimitive
            if (primitive.isString) {
                throw IllegalArgumentException("return at index $itemIndex must be a number")
            }
            primitive.content.toDoubleOrNull()?.takeIf { it.isFinite() }
                ?: throw IllegalArgumentException("return at index $itemIndex must be finite")
        }
        val output = sharpeOutput(returns, riskFreeRate, annualize)
        SharpeCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(JsonObject.serializer(), output),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        SharpeCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — JSON in / JSON out, matching the Python entrypoint. */
fun runSharpe(args: Array<String>) {
    val result = evaluateSharpe(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
