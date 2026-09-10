package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlin.math.max
import kotlin.system.exitProcess

/**
 * Kelly criterion — single-bet, fractional, and multi-bet correlated (Markowitz-Kelly).
 *
 * Parity contract: numerical agreement with [analyst-toolkit/quant/kelly.py] to within 1e-10
 * on the underlying math, and exact agreement on the percentage fields after Python's
 * `round(..., 3)` semantics (half-to-even, matched via BigDecimal HALF_EVEN here).
 *
 * Usage (single bet):
 *   ./gradlew run --args="kelly --mode single --p 0.55 --odds 2.0 --fraction 0.25"
 *
 * Usage (portfolio):
 *   ./gradlew run --args="kelly --mode portfolio --edges-json edges.json --fraction 0.25"
 */

/** A single betting opportunity. Mirrors the JSON schema accepted by `kelly.py`. */
data class Edge(val label: String, val p: Double, val odds: Double)

/** Internal per-bet result, mutable during exposure-cap + correlation-shrink adjustments. */
data class KellyRow(
    val label: String,
    val p: Double,
    val odds: Double,
    val evPct: Double,
    val fullKellyPct: Double,
    var fractionalKellyPct: Double,
    var scaledForTotalExposure: Boolean = false,
    var correlationShrink: Double? = null,
)

/** Optimal full-Kelly fraction for a binary bet at decimal odds. */
fun kellySingle(p: Double, oddsDecimal: Double): Double {
    require(p.isFinite() && p in 0.0..1.0) { "probability must be in [0, 1]" }
    require(oddsDecimal.isFinite() && oddsDecimal > 1.0) { "decimal odds must exceed 1" }
    val b = oddsDecimal - 1.0
    val q = 1.0 - p
    val f = if (b > 0.0) (b * p - q) / b else 0.0
    return max(0.0, f)
}

/** Expected value as % of stake (decimal, e.g. 0.052 = 5.2% edge). */
fun edgePct(p: Double, oddsDecimal: Double): Double {
    kellySingle(p, oddsDecimal)
    return p * (oddsDecimal - 1.0) - (1.0 - p)
}

/**
 * Naive multi-bet Kelly assuming low correlation by default. Optional correlation matrix
 * applies diversification shrinkage with a 50% floor. Total-exposure cap (50% of bankroll)
 * applies regardless. Sequencing matches `kelly.py` exactly: exposure cap first, then
 * correlation shrink.
 */
fun kellyPortfolio(
    edges: List<Edge>,
    fraction: Double = 0.25,
    corrMatrix: Map<String, Map<String, Double>>? = null,
): JsonObject {
    require(fraction.isFinite() && fraction in 0.0..1.0) { "fraction must be in [0, 1]" }
    val labels = edges.mapIndexed { i, edge -> edge.label.ifBlank { "bet_$i" } }
    require(labels.toSet().size == labels.size) { "bet labels must be unique" }
    corrMatrix?.forEach { (label, row) ->
        require(label in labels) { "unknown correlation row" }
        row.forEach { (other, correlation) ->
            require(other in labels && correlation.isFinite() && correlation in -1.0..1.0) { "invalid correlation" }
            require(label != other || correlation == 1.0) { "correlation diagonal must equal 1" }
            val reverse = corrMatrix[other]?.get(label)
            require(reverse == null || kotlin.math.abs(reverse - correlation) <= 1e-12) { "correlations must be symmetric" }
        }
    }
    val results = edges.mapIndexed { i, e ->
        val k = kellySingle(e.p, e.odds)
        val ev = edgePct(e.p, e.odds)
        KellyRow(
            label = e.label.ifBlank { "bet_$i" },
            p = e.p,
            odds = e.odds,
            evPct = round3(ev * 100.0),
            fullKellyPct = round3(k * 100.0),
            fractionalKellyPct = round3(k * fraction * 100.0),
        )
    }

    val totalRaw = edges.sumOf { kellySingle(it.p, it.odds) * fraction } * 100.0
    if (totalRaw > 50.0) {
        val scale = 50.0 / totalRaw
        results.forEach {
            it.fractionalKellyPct = round3(it.fractionalKellyPct * scale)
            it.scaledForTotalExposure = true
        }
    }

    if (corrMatrix != null) {
        results.forEach { r ->
            val row = corrMatrix[r.label] ?: return@forEach
            val others = row.filterKeys { it != r.label }
            if (row.isNotEmpty()) {
                val avgCorr = if (others.isEmpty()) 0.0 else others.values.sum() / others.size
                val shrink = max(0.5, 1.0 - max(0.0, avgCorr) * 0.5)
                r.fractionalKellyPct = round3(r.fractionalKellyPct * shrink)
                r.correlationShrink = round3(shrink)
            }
        }
    }

    var excessUnits = max(0L, results.sumOf { kotlin.math.round(it.fractionalKellyPct * 1000).toLong() } - 50000L)
    results.sortedByDescending { it.fractionalKellyPct }.forEach {
        val reduction = minOf(excessUnits, kotlin.math.round(it.fractionalKellyPct * 1000).toLong())
        it.fractionalKellyPct = round3(it.fractionalKellyPct - reduction / 1000.0)
        excessUnits -= reduction
    }
    val totalExposure = round3(results.sumOf { it.fractionalKellyPct })

    return buildJsonObject {
        put("fraction", JsonPrimitive(fraction))
        put("bets", buildJsonArray { results.forEach { add(rowToJson(it)) } })
        put("total_exposure_pct", JsonPrimitive(totalExposure))
        put("n_bets", JsonPrimitive(results.size))
        put("diversification_benefit",
            JsonPrimitive(if (corrMatrix != null) "applied" else "not_applied"))
    }
}

private fun rowToJson(r: KellyRow): JsonObject = buildJsonObject {
    put("label", JsonPrimitive(r.label))
    put("p", JsonPrimitive(r.p))
    put("odds", JsonPrimitive(r.odds))
    put("ev_pct", JsonPrimitive(r.evPct))
    put("full_kelly_pct", JsonPrimitive(r.fullKellyPct))
    put("fractional_kelly_pct", JsonPrimitive(r.fractionalKellyPct))
    if (r.scaledForTotalExposure) put("scaled_for_total_exposure", JsonPrimitive(true))
    r.correlationShrink?.let { put("correlation_shrink", JsonPrimitive(it)) }
}

/**
 * Match Python's `round(value, 3)` half-to-even (banker's rounding). Python uses HALF_EVEN
 * for `round()` on floats; we mirror via BigDecimal HALF_EVEN. NaN/Infinity are passed through.
 */
fun round3(value: Double): Double {
    if (value.isNaN() || value.isInfinite()) return value
    return java.math.BigDecimal(value).setScale(3, java.math.RoundingMode.HALF_EVEN).toDouble()
}

/** Module CLI runner — JSON in / JSON out, matches `kelly.py`'s contract. Invoked from Cli.kt. */
fun runKelly(args: Array<String>) {
    val parsed = parseArgs(args)
    val mode = parsed["mode"] ?: errorOut("need --mode single|portfolio")
    val json = Json { prettyPrint = true; encodeDefaults = false }

    val output: JsonElement = when (mode) {
        "single" -> {
            val p = parsed["p"]?.toDoubleOrNull() ?: errorOut("need --p")
            val odds = (parsed["odds-decimal"] ?: parsed["odds"])?.toDoubleOrNull()
                ?: errorOut("need --odds-decimal (or --odds)")
            val fraction = parsed["fraction"]?.toDoubleOrNull() ?: 0.25
            require(fraction.isFinite() && fraction in 0.0..1.0) { "fraction must be in [0, 1]" }
            val k = kellySingle(p, odds)
            val ev = edgePct(p, odds)
            buildJsonObject {
                put("p", JsonPrimitive(p))
                put("odds", JsonPrimitive(odds))
                put("edge_pct", JsonPrimitive(round3(ev * 100.0)))
                put("full_kelly_pct", JsonPrimitive(round3(k * 100.0)))
                put("fractional_kelly_pct", JsonPrimitive(round3(k * fraction * 100.0)))
                put("fraction", JsonPrimitive(fraction))
            }
        }
        "portfolio" -> {
            val edgesPath = parsed["edges-json"] ?: errorOut("need --edges-json")
            val fraction = parsed["fraction"]?.toDoubleOrNull() ?: 0.25
            val edges = parseEdgesJson(java.io.File(edgesPath).readText())
            val corr = parsed["correlation-matrix"]?.let {
                parseCorrJson(java.io.File(it).readText())
            }
            kellyPortfolio(edges, fraction, corr)
        }
        else -> errorOut("unknown mode: $mode")
    }
    println(json.encodeToString(JsonElement.serializer(), output))
}

private fun parseArgs(args: Array<String>): Map<String, String> {
    val m = mutableMapOf<String, String>()
    var i = 0
    while (i < args.size) {
        val a = args[i]
        if (a.startsWith("--")) {
            val key = a.removePrefix("--")
            val value = if (i + 1 < args.size && !args[i + 1].startsWith("--")) {
                i += 1; args[i]
            } else "true"
            m[key] = value
        }
        i += 1
    }
    return m
}

private fun parseEdgesJson(text: String): List<Edge> =
    Json.parseToJsonElement(text).jsonArray.map { el ->
        val o = el.jsonObject
        Edge(
            label = o["label"]?.jsonPrimitive?.content ?: "",
            p = o["p"]!!.jsonPrimitive.content.toDouble(),
            odds = o["odds"]!!.jsonPrimitive.content.toDouble(),
        )
    }

private fun parseCorrJson(text: String): Map<String, Map<String, Double>> =
    Json.parseToJsonElement(text).jsonObject.mapValues { (_, v) ->
        v.jsonObject.mapValues { (_, vv) -> vv.jsonPrimitive.content.toDouble() }
    }

private fun errorOut(msg: String): Nothing {
    println("""{"error": "$msg"}""")
    exitProcess(1)
}
