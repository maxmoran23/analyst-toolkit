package org.maxmoran.quant

import kotlinx.serialization.json.Json
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
    val n = x.size
    if (n < 2) return 0.0
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
    if (dx == 0.0 || dy == 0.0) return 0.0
    return num / (dx * dy)
}

/**
 * Parse CSV text the way the Python reference does: empty rows are skipped, and any row
 * containing a value that fails float() (e.g. a header) is skipped whole. The reference
 * uses csv.reader; quoted numeric fields are a non-contract divergence (skipped here).
 */
fun parseReturnsCsv(text: String): List<List<Double>> {
    val cols = mutableListOf<List<Double>>()
    for (line in text.lineSequence()) {
        if (line.isEmpty()) continue
        val values = line.split(",").map { it.trim().toDoubleOrNull() }
        if (values.any { it == null }) continue
        cols.add(values.filterNotNull())
    }
    return cols
}

/** Public rounded JSON value contract, field-for-field with `quant/correlation.py`. */
fun correlationOutput(
    cols: List<List<Double>>,
    assetNames: List<String>?,
    window: Int = 30,
    crisisThreshold: Double = -0.05,
): JsonObject {
    if (cols.isEmpty()) throw IllegalArgumentException("no numeric rows in CSV")
    val nRows = cols.size
    val nAssets = cols[0].size
    // The reference echoes the full provided name list even when longer than the asset count.
    val names = assetNames ?: List(nAssets) { "a$it" }
    val series = List(nAssets) { j -> cols.map { it[j] } }

    val fullCorr = LinkedHashMap<String, Double>()
    for (i in 0 until nAssets) {
        for (j in i + 1 until nAssets) {
            fullCorr["${names[i]}__${names[j]}"] = round4(corr(series[i], series[j]))
        }
    }

    val crisisIdx = (0 until nRows).filter { series[0][it] < crisisThreshold }
    val crisisCorr = LinkedHashMap<String, Double>()
    if (crisisIdx.size > 5) {
        for (i in 0 until nAssets) {
            for (j in i + 1 until nAssets) {
                crisisCorr["${names[i]}__${names[j]}"] = round4(
                    corr(crisisIdx.map { series[i][it] }, crisisIdx.map { series[j][it] })
                )
            }
        }
    }

    // The reference subtracts the already-rounded values, then rounds the difference again.
    val compression = LinkedHashMap<String, Double>()
    for ((key, full) in fullCorr) {
        val crisis = crisisCorr[key] ?: continue
        compression[key] = round4(crisis - full)
    }

    val rolling = LinkedHashMap<String, Double>()
    if (nRows >= window) {
        for (i in 1 until nAssets) {
            rolling["${names[i]}_vs_${names[0]}"] =
                round4(corr(tailSlice(series[0], window), tailSlice(series[i], window)))
        }
    }

    return buildJsonObject {
        put("n_observations", JsonPrimitive(nRows))
        put("n_assets", JsonPrimitive(nAssets))
        put("assets", buildJsonArray { names.forEach { add(JsonPrimitive(it)) } })
        put("window", JsonPrimitive(window))
        put("crisis_threshold", JsonPrimitive(crisisThreshold))
        put("n_crisis_days", JsonPrimitive(crisisIdx.size))
        put("full_sample_correlation", mapToJson(fullCorr))
        put("crisis_correlation", mapToJson(crisisCorr))
        put("correlation_compression", mapToJson(compression))
        put("rolling_correlation_last_window", mapToJson(rolling))
        put(
            "interpretation_hint",
            JsonPrimitive(
                "If compression > 0.2, diversification collapses in crashes. " +
                    "Treat 'uncorrelated' tag with suspicion."
            ),
        )
    }
}

// Python's xs[-window:] semantics: window 0 yields the whole list, negative drops from the front.
private fun tailSlice(xs: List<Double>, window: Int): List<Double> = when {
    window > 0 -> xs.takeLast(window)
    window == 0 -> xs
    else -> xs.drop(minOf(-window, xs.size))
}

private fun mapToJson(values: Map<String, Double>): JsonObject = buildJsonObject {
    values.forEach { (key, value) -> put(key, JsonPrimitive(value)) }
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
