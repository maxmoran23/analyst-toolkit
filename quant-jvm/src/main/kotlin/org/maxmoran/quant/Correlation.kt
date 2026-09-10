package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import java.io.File
import kotlin.math.sqrt
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/correlation.py` — full-sample, crisis-only, and rolling
 * pairwise Pearson correlation with a compression flag.
 *
 * parity-contract.md §1.4 lists correlation under numerical linear algebra (1e-6), but the
 * reference performs no matrix decomposition — only pairwise sums — so this port meets the
 * stronger §1.1 deterministic regime (1e-10 raw doubles, exact rounded JSON).
 */

/** Pearson correlation; returns 0.0 for short series or zero variance, matching `corr`. */
fun corr(x: List<Double>, y: List<Double>): Double {
    require(x.size == y.size && x.all { it.isFinite() } && y.all { it.isFinite() }) { "paired series must be finite and have equal lengths" }
    val n = x.size
    if (n < 2 || x.all { it == x[0] } || y.all { it == y[0] }) return 0.0
    val mx = x.sum() / n
    val my = y.sum() / n
    var num = 0.0
    for (i in 0 until n) num += (x[i] - mx) * (y[i] - my)
    val dx = sqrt(x.sumOf { value ->
        val deviation = value - mx
        deviation * deviation
    })
    val dy = sqrt(y.sumOf { value ->
        val deviation = value - my
        deviation * deviation
    })
    require(dx != 0.0 && dy != 0.0) { "nonconstant variance is below floating-point resolution" }
    return (num / (dx * dy)).also { require(it.isFinite()) { "correlation overflow" } }
}

private fun correlationValue(x: List<Double>, y: List<Double>): Double? {
    val value = corr(x, y)
    if (x.size < 2 || x.all { it == x[0] } || y.all { it == y[0] }) return null
    return round4(value)
}

/** Accept one all-text header, then rectangular finite numeric rows; reject malformed data.
 * The line-oriented parser supports unquoted fields and quoted single-line fields without embedded commas.
 */
fun parseReturnsCsv(text: String): List<List<Double>> {
    val rows = mutableListOf<List<Double>>()
    var first = true
    for ((index, line) in text.lineSequence().withIndex()) {
        if (line.isEmpty()) continue
        val fields = line.split(",").map { it.trim().removeSurrounding("\"") }
        val values = fields.map { it.toDoubleOrNull() }
        if (first && values.all { it == null }) {
            first = false
            continue
        }
        first = false
        require(values.all { it != null && it.isFinite() }) { "malformed numeric CSV row ${index + 1}" }
        val numeric = values.filterNotNull()
        require(rows.isEmpty() || numeric.size == rows[0].size) { "ragged CSV row ${index + 1}" }
        rows.add(numeric)
    }
    return rows
}

/** Public rounded JSON value contract, field-for-field with `quant/correlation.py`. */
fun correlationOutput(
    cols: List<List<Double>>,
    assetNames: List<String>?,
    window: Int = 30,
    crisisThreshold: Double = -0.05,
): JsonObject {
    require(cols.size >= 2 && cols[0].size >= 2 && cols.all { row -> row.size == cols[0].size && row.all { it.isFinite() } }) { "need finite rectangular data with two observations and two assets" }
    require(window >= 2 && crisisThreshold.isFinite()) { "window must be >= 2 and crisis threshold finite" }
    val nRows = cols.size
    val nAssets = cols[0].size
    val names = assetNames ?: List(nAssets) { "a$it" }
    require(names.size == nAssets && names.all { it.isNotBlank() } && names.toSet().size == names.size) { "asset names must be nonempty, unique and match columns" }
    val series = List(nAssets) { j -> cols.map { it[j] } }

    val fullCorr = LinkedHashMap<String, Double?>()
    for (i in 0 until nAssets) {
        for (j in i + 1 until nAssets) {
            fullCorr["${names[i]}__${names[j]}"] = correlationValue(series[i], series[j])
        }
    }

    val crisisIdx = (0 until nRows).filter { series[0][it] < crisisThreshold }
    val crisisCorr = LinkedHashMap<String, Double?>()
    if (crisisIdx.size > 5) {
        for (i in 0 until nAssets) {
            for (j in i + 1 until nAssets) {
                crisisCorr["${names[i]}__${names[j]}"] = correlationValue(crisisIdx.map { series[i][it] }, crisisIdx.map { series[j][it] })
            }
        }
    }

    // The reference subtracts the already-rounded values, then rounds the difference again.
    val compression = LinkedHashMap<String, Double>()
    for ((key, full) in fullCorr) {
        if (full == null) continue
        val crisis = crisisCorr[key] ?: continue
        compression[key] = round4(crisis - full)
    }

    val rolling = LinkedHashMap<String, Double?>()
    if (nRows >= window) {
        for (i in 1 until nAssets) {
            rolling["${names[i]}_vs_${names[0]}"] =
                correlationValue(series[0].takeLast(window), series[i].takeLast(window))
        }
    }

    return buildJsonObject {
        put("n_observations", JsonPrimitive(nRows))
        put("n_assets", JsonPrimitive(nAssets))
        put("assets", buildJsonArray { names.forEach { add(JsonPrimitive(it)) } })
        put("window", JsonPrimitive(window))
        put("crisis_threshold", JsonPrimitive(crisisThreshold))
        put("n_crisis_days", JsonPrimitive(crisisIdx.size))
        put("undefined_correlation_convention", JsonPrimitive("null means insufficient observations or zero variance; excluded from compression"))
        put("full_sample_correlation", mapToJson(fullCorr))
        put("crisis_correlation", mapToJson(crisisCorr))
        put("correlation_compression", mapToJson(compression))
        put("rolling_correlation_last_window", mapToJson(rolling))
        put(
            "interpretation_hint",
            JsonPrimitive(
                "Compression > 0.2 is a descriptive review flag, not a calibrated threshold or proof that diversification fails."
            ),
        )
    }
}

private fun mapToJson(values: Map<String, Double?>): JsonObject = buildJsonObject {
    values.forEach { (key, value) -> put(key, value?.let { JsonPrimitive(it) } ?: JsonNull) }
}

/** Testable result of evaluating the correlation CLI contract. */
data class CorrelationCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateCorrelation(args: Array<String>): CorrelationCliResult {
    return try {
        var csvPath: String? = null
        var assetNames: String? = null
        var window = 30
        var crisisThreshold = -0.05
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
                "--window" -> window = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--window must be an integer")
                "--crisis-threshold" -> crisisThreshold = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--crisis-threshold must be a number")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        val path = csvPath ?: throw IllegalArgumentException("need --returns-csv")
        // Python's "".split(",") yields [""], so an empty names flag still produces one name.
        val names = assetNames?.split(",")
        val output = correlationOutput(parseReturnsCsv(File(path).readText()), names, window, crisisThreshold)
        CorrelationCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(JsonObject.serializer(), output),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        CorrelationCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — CSV in / JSON out, matching the Python entrypoint. */
fun runCorrelation(args: Array<String>) {
    val result = evaluateCorrelation(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
