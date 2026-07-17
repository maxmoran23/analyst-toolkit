package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import java.io.File
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sqrt
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/markowitz.py` — min-variance, max-Sharpe, and equal-weight
 * portfolios from a returns matrix.
 *
 * parity-contract.md §1.4 applies: the reference solves cov * x = b with a hand-rolled
 * Cholesky factorization plus forward/backward substitution (pure Python, no numpy in the
 * code path), so this port replicates that exact arithmetic — same loops, same summation
 * order, same 1e-10 pivot regularization — rather than delegating to a library solver.
 * Raw solver parity is asserted at the §1.4 tolerance (1e-6 per entry).
 */

/** Column means of a row-major returns matrix; mirrors `mean_vec`. */
fun meanVec(matrix: List<List<Double>>): List<Double> {
    val n = matrix.size
    val m = matrix[0].size
    return List(m) { j -> matrix.sumOf { it[j] } / n }
}

/** Sample (ddof=1) covariance matrix plus the mean vector; mirrors `cov_matrix`. */
fun covMatrix(matrix: List<List<Double>>): Pair<List<List<Double>>, List<Double>> {
    val n = matrix.size
    val m = matrix[0].size
    val mu = meanVec(matrix)
    val cov = Array(m) { DoubleArray(m) }
    for (j in 0 until m) {
        for (k in j until m) {
            var s = 0.0
            for (i in 0 until n) s += (matrix[i][j] - mu[j]) * (matrix[i][k] - mu[k])
            val v = s / (n - 1)
            cov[j][k] = v
            cov[k][j] = v
        }
    }
    return cov.map { it.toList() } to mu
}

/** Cholesky factor with the reference's 1e-10 regularization of non-positive pivots. */
fun cholesky(a: List<List<Double>>): List<List<Double>> {
    val n = a.size
    val l = Array(n) { DoubleArray(n) }
    for (i in 0 until n) {
        for (j in 0..i) {
            var s = 0.0
            for (k in 0 until j) s += l[i][k] * l[j][k]
            if (i == j) {
                var v = a[i][i] - s
                if (v <= 0.0) v = 1e-10
                l[i][j] = sqrt(v)
            } else {
                l[i][j] = (a[i][j] - s) / l[j][j]
            }
        }
    }
    return l.map { it.toList() }
}

private fun forwardSub(l: List<List<Double>>, b: List<Double>): List<Double> {
    val n = l.size
    val x = DoubleArray(n)
    for (i in 0 until n) {
        var s = 0.0
        for (k in 0 until i) s += l[i][k] * x[k]
        x[i] = (b[i] - s) / l[i][i]
    }
    return x.toList()
}

private fun backwardSub(u: List<List<Double>>, b: List<Double>): List<Double> {
    val n = u.size
    val x = DoubleArray(n)
    for (i in n - 1 downTo 0) {
        var s = 0.0
        for (k in i + 1 until n) s += u[i][k] * x[k]
        x[i] = (b[i] - s) / u[i][i]
    }
    return x.toList()
}

/** Solve Ax = b via Cholesky, matching `solve_linear`'s factor-transpose-substitute path. */
fun solveLinear(a: List<List<Double>>, b: List<Double>): List<Double> {
    val l = cholesky(a)
    val y = forwardSub(l, b)
    val lt = List(l.size) { i -> List(l.size) { j -> l[j][i] } }
    return backwardSub(lt, y)
}

/** Global minimum variance weights: cov^-1 * 1, normalized to sum to one. */
fun minVariancePortfolio(cov: List<List<Double>>): List<Double> {
    val ones = List(cov.size) { 1.0 }
    val invCovOnes = solveLinear(cov, ones)
    val denom = invCovOnes.sum()
    return invCovOnes.map { it / denom }
}

/** Max-Sharpe tangency weights, or null when the normalizer is degenerate (|sum| < 1e-12). */
fun maxSharpePortfolio(cov: List<List<Double>>, excessReturns: List<Double>): List<Double>? {
    val invCovR = solveLinear(cov, excessReturns)
    val denom = invCovR.sum()
    if (abs(denom) < 1e-12) return null
    return invCovR.map { it / denom }
}

/** Annualized return / volatility / Sharpe block, rounded like `portfolio_stats`. */
fun portfolioStats(
    weights: List<Double>,
    mu: List<Double>,
    cov: List<List<Double>>,
    rf: Double = 0.0,
    annualize: Int = 252,
): JsonObject {
    var ret = 0.0
    for (i in weights.indices) ret += weights[i] * mu[i]
    var variance = 0.0
    val n = weights.size
    for (i in 0 until n) {
        for (j in 0 until n) {
            variance += weights[i] * weights[j] * cov[i][j]
        }
    }
    val vol = sqrt(max(0.0, variance))
    val annualizeSqrt = sqrt(annualize.toDouble())
    val sharpe = if (vol > 0.0) (ret * annualize - rf) / (vol * annualizeSqrt) else 0.0
    return buildJsonObject {
        put("expected_return_ann_pct", JsonPrimitive(round3(ret * annualize * 100.0)))
        put("volatility_ann_pct", JsonPrimitive(round3(vol * annualizeSqrt * 100.0)))
        put("sharpe", JsonPrimitive(round3(sharpe)))
    }
}

/** Public rounded JSON value contract, field-for-field with `quant/markowitz.py`. */
fun markowitzOutput(
    returns: List<List<Double>>,
    assetNames: List<String>?,
    rf: Double = 0.05,
    annualize: Int = 252,
): JsonObject {
    if (returns.isEmpty()) throw IllegalArgumentException("no numeric data found")
    val nAssets = returns[0].size
    val names = assetNames ?: List(nAssets) { "asset_$it" }
    val (cov, mu) = covMatrix(returns)
    val periodicRf = rf / annualize
    val excess = mu.map { it - periodicRf }

    return buildJsonObject {
        put("n_assets", JsonPrimitive(nAssets))
        put("n_observations", JsonPrimitive(returns.size))
        put("asset_names", buildJsonArray { names.forEach { add(JsonPrimitive(it)) } })

        val minVarianceWeights = minVariancePortfolio(cov)
        put("min_variance_portfolio", portfolioBlock(names, minVarianceWeights, mu, cov, rf, annualize))

        // Reference omits the key entirely when the tangency normalizer is degenerate.
        maxSharpePortfolio(cov, excess)?.let { maxSharpeWeights ->
            put("max_sharpe_portfolio", portfolioBlock(names, maxSharpeWeights, mu, cov, rf, annualize))
        }

        val equalWeights = List(nAssets) { 1.0 / nAssets }
        put("equal_weight_benchmark", buildJsonObject {
            // Reference iterates ALL names here (not zip), so surplus names appear too.
            put("weights", buildJsonObject {
                names.forEach { put(it, JsonPrimitive(round4(1.0 / nAssets))) }
            })
            portfolioStats(equalWeights, mu, cov, rf, annualize).forEach { (key, value) -> put(key, value) }
        })
    }
}

// Python's zip(names, weights) truncates to the shorter sequence; duplicates overwrite.
private fun portfolioBlock(
    names: List<String>,
    weights: List<Double>,
    mu: List<Double>,
    cov: List<List<Double>>,
    rf: Double,
    annualize: Int,
): JsonObject = buildJsonObject {
    put("weights", buildJsonObject {
        names.zip(weights).forEach { (name, w) -> put(name, JsonPrimitive(round4(w))) }
    })
    portfolioStats(weights, mu, cov, rf, annualize).forEach { (key, value) -> put(key, value) }
}

/** Testable result of evaluating the Markowitz CLI contract. */
data class MarkowitzCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateMarkowitz(args: Array<String>): MarkowitzCliResult {
    return try {
        var csvPath: String? = null
        var assetNames: String? = null
        var rf = 0.05
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
                "--returns-csv" -> csvPath = optionValue(arg)
                "--asset-names" -> assetNames = optionValue(arg)
                "--rf" -> rf = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--rf must be a number")
                "--annualize" -> annualize = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--annualize must be an integer")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        val path = csvPath ?: throw IllegalArgumentException("need --returns-csv")
        val returns = parseReturnsCsv(File(path).readText())
        if (returns.isEmpty()) throw IllegalArgumentException("no numeric data found")
        val names = assetNames?.split(",")
        MarkowitzCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(
                JsonObject.serializer(),
                markowitzOutput(returns, names, rf, annualize),
            ),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        MarkowitzCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — CSV in / JSON out, matching the Python entrypoint. */
fun runMarkowitz(args: Array<String>) {
    val result = evaluateMarkowitz(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
