package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import kotlin.math.max
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/drawdown.py` — max drawdown, underwater curve, recovery
 * time distribution. Operation order matches the Python reference so raw doubles agree
 * to 1e-10 and the rounded public JSON contract matches exactly.
 */

/** Compound a unit start through periodic returns; mirrors `equity_from_returns`. */
fun equityFromReturns(returns: List<Double>, start: Double = 1.0): List<Double> {
    val equity = ArrayList<Double>(returns.size + 1)
    equity.add(start)
    for (r in returns) equity.add(equity.last() * (1.0 + r))
    return equity
}

/** Per-observation drawdown fractions from a running peak; zero when the peak is non-positive. */
fun drawdownSeries(equity: List<Double>): List<Double> {
    var peak = equity[0]
    return equity.map { value ->
        peak = max(peak, value)
        if (peak > 0.0) (peak - value) / peak else 0.0
    }
}

/**
 * One peak-to-trough-to-recovery episode. [ddPct] carries the Python episode dict's
 * rounded value (round3 of the percentage) because the reference sorts on the rounded field.
 * [recoveryIdx] and [durationToRecovery] are null for the unrecovered tail episode.
 */
data class DrawdownEpisode(
    val peakIdx: Int,
    val troughIdx: Int,
    val recoveryIdx: Int?,
    val ddPct: Double,
    val durationToTrough: Int,
    val durationToRecovery: Int?,
    val stillUnderwater: Boolean = false,
)

/** Sequential drawdown episodes, matching `recovery_episodes` including the unrecovered tail. */
fun recoveryEpisodes(equity: List<Double>): List<DrawdownEpisode> {
    val episodes = mutableListOf<DrawdownEpisode>()
    var peak = equity[0]
    var peakIdx = 0
    var inDrawdown = false
    var trough = peak
    var troughIdx = 0
    for ((i, value) in equity.withIndex()) {
        if (value >= peak) {
            if (inDrawdown && trough < peak) {
                episodes.add(
                    DrawdownEpisode(
                        peakIdx = peakIdx,
                        troughIdx = troughIdx,
                        recoveryIdx = i,
                        ddPct = round3((peak - trough) / peak * 100.0),
                        durationToTrough = troughIdx - peakIdx,
                        durationToRecovery = i - peakIdx,
                    )
                )
                inDrawdown = false
            }
            peak = value
            peakIdx = i
            trough = value
            troughIdx = i
        } else {
            inDrawdown = true
            if (value < trough) {
                trough = value
                troughIdx = i
            }
        }
    }
    if (inDrawdown && trough < peak) {
        episodes.add(
            DrawdownEpisode(
                peakIdx = peakIdx,
                troughIdx = troughIdx,
                recoveryIdx = null,
                ddPct = round3((peak - trough) / peak * 100.0),
                durationToTrough = troughIdx - peakIdx,
                durationToRecovery = null,
                stillUnderwater = true,
            )
        )
    }
    return episodes
}

/** Public rounded JSON value contract, field-for-field with `quant/drawdown.py`. */
fun drawdownOutput(equity: List<Double>, topN: Int = 5): JsonObject {
    require(equity.isNotEmpty()) { "equity series is empty" }
    val dds = drawdownSeries(equity)
    val episodes = recoveryEpisodes(equity)
    // Stable descending sort on the rounded field, matching Python's sorted(..., reverse=True).
    val sorted = episodes.sortedByDescending { it.ddPct }
    // Python filters with a truthy check, which drops both None and zero durations.
    val recoveries = episodes.mapNotNull { it.durationToRecovery }.filter { it != 0 }
    return buildJsonObject {
        put("n_observations", JsonPrimitive(equity.size))
        put("max_drawdown_pct", JsonPrimitive(round3(dds.max() * 100.0)))
        put("current_drawdown_pct", JsonPrimitive(round3(dds.last() * 100.0)))
        put("avg_drawdown_pct", JsonPrimitive(round3(dds.sum() / dds.size * 100.0)))
        put(
            "pct_time_underwater",
            JsonPrimitive(round2(dds.count { it > 0.001 }.toDouble() / dds.size * 100.0)),
        )
        put("n_drawdown_episodes", JsonPrimitive(episodes.size))
        put("top_drawdowns", buildJsonArray { sorted.take(topN).forEach { add(episodeToJson(it)) } })
        put(
            "avg_recovery_days",
            JsonPrimitive(round2(recoveries.sum().toDouble() / max(1, recoveries.size))),
        )
    }
}

private fun episodeToJson(e: DrawdownEpisode): JsonObject = buildJsonObject {
    put("peak_idx", JsonPrimitive(e.peakIdx))
    put("trough_idx", JsonPrimitive(e.troughIdx))
    put("recovery_idx", e.recoveryIdx?.let { JsonPrimitive(it) } ?: JsonNull)
    put("dd_pct", JsonPrimitive(e.ddPct))
    put("duration_to_trough", JsonPrimitive(e.durationToTrough))
    put("duration_to_recovery", e.durationToRecovery?.let { JsonPrimitive(it) } ?: JsonNull)
    if (e.stillUnderwater) put("still_underwater", JsonPrimitive(true))
}

/** Parse a JSON array of finite numbers; shared by the drawdown and vol CLI evaluators. */
internal fun parseNumberArray(text: String, label: String): List<Double> {
    val parsed = Json.parseToJsonElement(text)
    if (parsed !is JsonArray) throw IllegalArgumentException("$label JSON must be an array")
    return parsed.mapIndexed { index, element ->
        val primitive = element.jsonPrimitive
        if (primitive.isString) {
            throw IllegalArgumentException("$label value at index $index must be a number")
        }
        primitive.content.toDoubleOrNull()?.takeIf { it.isFinite() }
            ?: throw IllegalArgumentException("$label value at index $index must be finite")
    }
}

/** Testable result of evaluating the drawdown CLI contract. */
data class DrawdownCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateDrawdown(args: Array<String>): DrawdownCliResult {
    return try {
        var equityPath: String? = null
        var returnsPath: String? = null
        var topN = 5
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
                "--equity-json" -> equityPath = optionValue(arg)
                "--returns-json" -> returnsPath = optionValue(arg)
                "--top-n" -> topN = optionValue(arg).toIntOrNull()
                    ?: throw IllegalArgumentException("--top-n must be an integer")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        // Same precedence as Python: --equity-json wins if both are supplied.
        val equity = when {
            equityPath != null -> parseNumberArray(File(equityPath).readText(), "equity")
            returnsPath != null ->
                equityFromReturns(parseNumberArray(File(returnsPath).readText(), "returns"))
            else -> throw IllegalArgumentException("need --equity-json or --returns-json")
        }
        DrawdownCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(JsonObject.serializer(), drawdownOutput(equity, topN)),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        DrawdownCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

/** Module CLI runner — JSON in / JSON out, matching the Python entrypoint. */
fun runDrawdown(args: Array<String>) {
    val result = evaluateDrawdown(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
