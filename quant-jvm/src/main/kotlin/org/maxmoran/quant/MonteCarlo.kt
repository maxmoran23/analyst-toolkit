package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import java.util.Random
import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Port of `quant/monte_carlo.py` — GBM price paths with optional Merton jumps, ending-price
 * and max-drawdown distributions.
 *
 * Regime split per parity-contract.md: the path generators are stochastic and verified
 * under §1.3 (distributional agreement at N >= 10,000; bit-matching Python's Mersenne
 * Twister is explicitly rejected there). The skeleton around them — `percentile`, per-path
 * max drawdown, and the entire output-shaping block — is deterministic §1.1 material and
 * is tested at exact parity against a Python oracle on fixed injected samples.
 *
 * RNG: `java.util.Random(seed)` (spec-pinned LCG + Marsaglia polar Gaussian), so the
 * KOTLIN side is bit-reproducible for a given seed across runs and JVMs. Seeds are NOT
 * cross-language comparable: the same `--seed` produces different (equally valid) draws
 * here and in Python.
 */

/** Index-truncating percentile pick from a pre-sorted list; mirrors `percentile` exactly. */
fun percentile(sortedList: List<Double>, p: Double): Double {
    var idx = (p * sortedList.size).toInt()
    idx = min(max(0, idx), sortedList.size - 1)
    return sortedList[idx]
}

/** One geometric Brownian motion path of [days] steps, drawing from [rng]. */
fun gbmPath(
    spot: Double,
    drift: Double,
    vol: Double,
    days: Int,
    dt: Double = 1.0 / 365.0,
    rng: Random,
): List<Double> {
    val path = ArrayList<Double>(days + 1)
    path.add(spot)
    for (step in 0 until days) {
        val z = rng.nextGaussian()
        path.add(path.last() * exp((drift - 0.5 * vol * vol) * dt + vol * sqrt(dt) * z))
    }
    return path
}

/** GBM with Poisson-approximated Merton jumps; `gauss(mean, vol)` = mean + vol * z. */
fun jumpGbmPath(
    spot: Double,
    drift: Double,
    vol: Double,
    days: Int,
    jumpIntensity: Double = 0.5,
    jumpMean: Double = -0.05,
    jumpVol: Double = 0.15,
    dt: Double = 1.0 / 365.0,
    rng: Random,
): List<Double> {
    val path = ArrayList<Double>(days + 1)
    path.add(spot)
    for (step in 0 until days) {
        val z = rng.nextGaussian()
        var jump = 0.0
        if (rng.nextDouble() < jumpIntensity * dt) {
            jump = jumpMean + jumpVol * rng.nextGaussian()
        }
        path.add(path.last() * exp((drift - 0.5 * vol * vol) * dt + vol * sqrt(dt) * z + jump))
    }
    return path
}

/** Deterministic per-path max drawdown, mirroring the inline loop in the Python main. */
fun pathMaxDrawdown(path: List<Double>): Double {
    var peak = path[0]
    var maxDd = 0.0
    for (p in path) {
        peak = max(peak, p)
        val dd = if (peak > 0.0) (peak - p) / peak else 0.0
        maxDd = max(maxDd, dd)
    }
    return maxDd
}

/** Ending prices and max drawdowns for [paths] simulated paths from a seeded RNG. */
data class SimulationResult(val endingPrices: List<Double>, val maxDrawdowns: List<Double>)

fun simulate(
    spot: Double,
    vol: Double,
    drift: Double = 0.0,
    days: Int = 30,
    paths: Int = 10000,
    jumps: Boolean = false,
    seed: Long = 42L,
): SimulationResult {
    val rng = Random(seed)
    val endingPrices = ArrayList<Double>(max(0, paths))
    val maxDrawdowns = ArrayList<Double>(max(0, paths))
    for (i in 0 until paths) {
        val path = if (jumps) {
            jumpGbmPath(spot, drift, vol, days, rng = rng)
        } else {
            gbmPath(spot, drift, vol, days, rng = rng)
        }
        endingPrices.add(path.last())
        maxDrawdowns.add(pathMaxDrawdown(path))
    }
    return SimulationResult(endingPrices, maxDrawdowns)
}

/**
 * Deterministic output shaping, field-for-field with the Python main given the same
 * sample arrays. Sorting happens here, matching `sorted(...)` in the reference.
 * Python raises ZeroDivisionError for zero paths (mean) and zero spot (vs-spot fields);
 * Kotlin's silent NaN/Infinity would break the no-silent-failure contract, so both throw.
 */
fun monteCarloSummary(
    endingPrices: List<Double>,
    maxDrawdowns: List<Double>,
    spot: Double,
    vol: Double,
    drift: Double,
    days: Int,
    paths: Int,
    jumps: Boolean,
): JsonObject {
    if (endingPrices.isEmpty()) throw ArithmeticException("division by zero: no simulated paths")
    if (spot == 0.0) throw ArithmeticException("division by zero: spot is zero")
    val ep = endingPrices.sorted()
    val dd = maxDrawdowns.sorted()
    val meanEnding = ep.sum() / ep.size

    return buildJsonObject {
        put("inputs", buildJsonObject {
            put("spot", JsonPrimitive(spot))
            put("vol", JsonPrimitive(vol))
            put("drift", JsonPrimitive(drift))
            put("days", JsonPrimitive(days))
            put("paths", JsonPrimitive(paths))
            put("jumps", JsonPrimitive(jumps))
        })
        put("ending_price_distribution", buildJsonObject {
            put("p05", JsonPrimitive(round4(percentile(ep, 0.05))))
            put("p25", JsonPrimitive(round4(percentile(ep, 0.25))))
            put("p50", JsonPrimitive(round4(percentile(ep, 0.50))))
            put("p75", JsonPrimitive(round4(percentile(ep, 0.75))))
            put("p95", JsonPrimitive(round4(percentile(ep, 0.95))))
            put("mean", JsonPrimitive(round4(meanEnding)))
            put("vs_spot_pct_p50", JsonPrimitive(round3((percentile(ep, 0.50) / spot - 1.0) * 100.0)))
            put("vs_spot_pct_p05", JsonPrimitive(round3((percentile(ep, 0.05) / spot - 1.0) * 100.0)))
            put("vs_spot_pct_p95", JsonPrimitive(round3((percentile(ep, 0.95) / spot - 1.0) * 100.0)))
        })
        put("max_drawdown_distribution", buildJsonObject {
            put("p50_max_dd_pct", JsonPrimitive(round3(percentile(dd, 0.50) * 100.0)))
            put("p75_max_dd_pct", JsonPrimitive(round3(percentile(dd, 0.75) * 100.0)))
            put("p95_max_dd_pct", JsonPrimitive(round3(percentile(dd, 0.95) * 100.0)))
            put("p99_max_dd_pct", JsonPrimitive(round3(percentile(dd, 0.99) * 100.0)))
        })
        put("prob_below_spot", JsonPrimitive(round2(ep.count { it < spot }.toDouble() / ep.size * 100.0)))
        put("prob_halving", JsonPrimitive(round2(ep.count { it < spot * 0.5 }.toDouble() / ep.size * 100.0)))
        put("prob_doubling", JsonPrimitive(round2(ep.count { it > spot * 2.0 }.toDouble() / ep.size * 100.0)))
    }
}

/** Testable result of evaluating the Monte Carlo CLI contract. */
data class MonteCarloCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateMonteCarlo(args: Array<String>): MonteCarloCliResult {
    return try {
        var spot: Double? = null
        var vol: Double? = null
        var drift = 0.0
        var days = 30
        var paths = 10000
        var jumps = false
        var seed = 42L
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
                "--spot" -> spot = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--spot must be a number")
                "--vol" -> vol = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--vol must be a number")
                "--drift" -> drift = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--drift must be a number")
                "--days" -> days = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--days must be an integer")
                "--paths" -> paths = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--paths must be an integer")
                "--jumps" -> jumps = true
                "--seed" -> seed = optionValue(arg).toLongOrNull()
                    ?: throw IllegalArgumentException("--seed must be an integer")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        val spotValue = spot ?: throw IllegalArgumentException("need --spot")
        val volValue = vol ?: throw IllegalArgumentException("need --vol")
        val result = simulate(spotValue, volValue, drift, days, paths, jumps, seed)
        MonteCarloCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(
                JsonObject.serializer(),
                monteCarloSummary(
                    result.endingPrices, result.maxDrawdowns,
                    spotValue, volValue, drift, days, paths, jumps,
                ),
            ),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        MonteCarloCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — args in / JSON out, matching the Python entrypoint. */
fun runMonteCarlo(args: Array<String>) {
    val result = evaluateMonteCarlo(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
