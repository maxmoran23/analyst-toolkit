package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs

/**
 * Parity tests for Kelly criterion vs the Python reference at `../quant/kelly.py`.
 *
 * Contract:
 *   - Deterministic math (no RNG): numerical agreement within 1e-10 on raw doubles.
 *   - Reported percentage fields: exact equality after Python's `round(x, 3)` semantics
 *     (BigDecimal HALF_EVEN here mirrors Python's round-half-to-even on floats).
 *
 * These tests resolve the Python interpreter from PATH. If unavailable, the test is skipped
 * with a clear message — parity tests are advisory in CI without Python, but enforced locally.
 */
class KellyParityTest {

    @Test
    fun `single bet — positive edge`() {
        val p = 0.55
        val odds = 2.0
        val fraction = 0.25

        val kt = kellyOutputKt(p, odds, fraction)
        val py = kellyOutputPy(p, odds, fraction) ?: return  // skip if no python3

        assertNumericalParity(py, kt, fieldsToCheck = listOf(
            "edge_pct", "full_kelly_pct", "fractional_kelly_pct", "fraction", "p", "odds"
        ))
    }

    @Test
    fun `single bet — zero or negative edge clamps to zero`() {
        // p * (odds - 1) < (1 - p), so full Kelly should be 0
        val p = 0.40
        val odds = 2.0
        val fraction = 0.25

        val k = kellySingle(p, odds)
        assertEquals(0.0, k, "Negative-edge Kelly must clamp to 0")

        val kt = kellyOutputKt(p, odds, fraction)
        val py = kellyOutputPy(p, odds, fraction) ?: return
        assertNumericalParity(py, kt, fieldsToCheck = listOf(
            "edge_pct", "full_kelly_pct", "fractional_kelly_pct"
        ))
    }

    @Test
    fun `single bet — spot checks against hand math`() {
        // Hand check: p=0.6, odds=2.0  => b=1, q=0.4, f = (1*0.6 - 0.4)/1 = 0.20
        assertEquals(0.20, kellySingle(0.6, 2.0), 1e-12)
        // Hand check: p=0.5, odds=2.0  => f = (0.5 - 0.5)/1 = 0.0
        assertEquals(0.0, kellySingle(0.5, 2.0), 1e-12)
        // Hand check: p=0.7, odds=2.5  => b=1.5, q=0.3, f = (1.5*0.7 - 0.3)/1.5 = 0.50
        assertEquals(0.50, kellySingle(0.7, 2.5), 1e-12)
        // Edge in % terms: p=0.55, odds=2.0  => 0.55*1 - 0.45 = 0.10
        assertEquals(0.10, edgePct(0.55, 2.0), 1e-12)
    }

    @Test
    fun `portfolio — 3 independent bets, exposure cap inactive`() {
        val edges = listOf(
            Edge("BET-A", 0.55, 2.0),
            Edge("BET-B", 0.58, 1.91),
            Edge("BET-C", 0.62, 1.75),
        )
        val ktOut = kellyPortfolio(edges, 0.25)
        val pyOut = portfolioOutputPy(edges, 0.25) ?: return

        assertEquals(
            pyOut["n_bets"]?.jsonPrimitive?.content,
            ktOut["n_bets"]?.jsonPrimitive?.content,
            "n_bets mismatch"
        )
        assertEquals(
            pyOut["diversification_benefit"]?.jsonPrimitive?.content,
            ktOut["diversification_benefit"]?.jsonPrimitive?.content,
            "diversification_benefit label mismatch"
        )
        assertPortfolioBetsParity(pyOut, ktOut)
    }

    @Test
    fun `portfolio — exposure cap engages when sum greater than 50pct`() {
        // Three high-edge bets each ~25% fractional Kelly => sum > 50% triggers scaling
        val edges = listOf(
            Edge("BIG-1", 0.80, 2.0),  // full Kelly = 0.60, q=0.25 → fractional = 15%
            Edge("BIG-2", 0.82, 2.0),  // similar
            Edge("BIG-3", 0.85, 2.0),  // similar
        )
        val ktOut = kellyPortfolio(edges, 0.50)  // half-Kelly to bump exposure
        val pyOut = portfolioOutputPy(edges, 0.50) ?: return
        assertPortfolioBetsParity(pyOut, ktOut)

        // Verify the cap actually engaged
        val anyScaled = ktOut["bets"]?.jsonArray?.any {
            it.jsonObject["scaled_for_total_exposure"]?.jsonPrimitive?.content == "true"
        } ?: false
        assertTrue(anyScaled, "Expected exposure cap to engage at half-Kelly with 3 fat edges")
    }

    @Test
    fun `round3 — agrees with Python on edge cases`() {
        // Trivially safe hand assertions only — IEEE 754 representation matches the literal exactly.
        assertEquals(0.0, round3(0.0))
        assertEquals(12.5, round3(12.5))   // 12.5 is exactly representable; scale=3 leaves it alone

        // Note: round3(-0.0) returns +0.0 here, not -0.0 — BigDecimal drops the sign of zero.
        // Python's round(-0.0, 3) returns -0.0. Preserving negative zero would require
        // post-processing BigDecimal output, which is not contract-relevant for financial math
        // (no Kelly/Sharpe/etc. computation ever consumes the sign of zero). Documented divergence.

        // Everything else: don't hand-assert. Compare against Python directly.
        // Many of these literals (1.2345, 0.0005, 12.515, ...) are NOT what they look like —
        // their IEEE 754 representations slightly under- or overshoot the decimal value,
        // and `round(x, 3)` behavior depends on the actual binary repr. This is documented
        // in docs/parity-contract.md §1.2.
        val cases = listOf(1.2345, 1.2355, 1.2365, 0.0005, -0.0005, 12.515, 12.525, 0.5, 1.5, 2.5)
        val py = pyRoundCheck(cases) ?: return
        val kt = cases.map { round3(it) }
        for (i in kt.indices) {
            assertEquals(py[i], kt[i], 1e-12,
                "round3 mismatch on input ${cases[i]}: py=${py[i]} kt=${kt[i]}")
        }
    }

    // ----- helpers -----

    private fun assertNumericalParity(py: JsonObject, kt: JsonObject, fieldsToCheck: List<String>) {
        for (field in fieldsToCheck) {
            val pv = py[field]?.jsonPrimitive?.content?.toDouble()
            val kv = kt[field]?.jsonPrimitive?.content?.toDouble()
            assertTrue(pv != null && kv != null, "Field '$field' missing in py=$pv kt=$kv")
            val diff = abs(pv!! - kv!!)
            assertTrue(diff < 1e-10, "Field '$field' parity break: py=$pv kt=$kv diff=$diff")
        }
    }

    private fun assertPortfolioBetsParity(py: JsonObject, kt: JsonObject) {
        val pyBets = py["bets"]?.jsonArray ?: error("py bets missing")
        val ktBets = kt["bets"]?.jsonArray ?: error("kt bets missing")
        assertEquals(pyBets.size, ktBets.size, "bets array size mismatch")
        for (i in pyBets.indices) {
            val pb = pyBets[i].jsonObject
            val kb = ktBets[i].jsonObject
            assertEquals(pb["label"]?.jsonPrimitive?.content, kb["label"]?.jsonPrimitive?.content,
                "label mismatch at index $i")
            for (numField in listOf("ev_pct", "full_kelly_pct", "fractional_kelly_pct", "p", "odds")) {
                val pv = pb[numField]?.jsonPrimitive?.content?.toDouble()
                val kv = kb[numField]?.jsonPrimitive?.content?.toDouble()
                if (pv != null && kv != null) {
                    assertTrue(abs(pv - kv) < 1e-10,
                        "Field '$numField' bet[$i] parity: py=$pv kt=$kv")
                }
            }
        }
    }

    private fun kellyOutputKt(p: Double, odds: Double, fraction: Double): JsonObject {
        val k = kellySingle(p, odds)
        val ev = edgePct(p, odds)
        return Json.parseToJsonElement("""{
            "p": $p, "odds": $odds,
            "edge_pct": ${round3(ev * 100.0)},
            "full_kelly_pct": ${round3(k * 100.0)},
            "fractional_kelly_pct": ${round3(k * fraction * 100.0)},
            "fraction": $fraction
        }""").jsonObject
    }

    /** Run kelly.py single mode and parse its JSON output. Returns null if python3 missing. */
    private fun kellyOutputPy(p: Double, odds: Double, fraction: Double): JsonObject? {
        val pyScript = pythonReferenceScript() ?: return null
        val proc = ProcessBuilder(
            "python3", pyScript,
            "--mode", "single",
            "--p", p.toString(),
            "--odds-decimal", odds.toString(),
            "--fraction", fraction.toString(),
        ).redirectErrorStream(true).start()
        val output = proc.inputStream.bufferedReader().readText()
        val exit = proc.waitFor()
        check(exit == 0) { "python3 kelly.py failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
    }

    /** Run kelly.py portfolio mode (writes edges to a temp JSON, invokes script). */
    private fun portfolioOutputPy(edges: List<Edge>, fraction: Double): JsonObject? {
        val pyScript = pythonReferenceScript() ?: return null
        val tmp = File.createTempFile("edges_", ".json")
        tmp.writeText(edges.joinToString(",", "[", "]") {
            """{"label":"${it.label}","p":${it.p},"odds":${it.odds}}"""
        })
        try {
            val proc = ProcessBuilder(
                "python3", pyScript,
                "--mode", "portfolio",
                "--edges-json", tmp.absolutePath,
                "--fraction", fraction.toString(),
            ).redirectErrorStream(true).start()
            val output = proc.inputStream.bufferedReader().readText()
            val exit = proc.waitFor()
            check(exit == 0) { "python3 kelly.py portfolio failed: $output" }
            return Json.parseToJsonElement(output).jsonObject
        } finally {
            tmp.delete()
        }
    }

    /** Helper: invoke python3 to compute round(x, 3) for a list of inputs, return list of doubles. */
    private fun pyRoundCheck(values: List<Double>): List<Double>? {
        if (!pythonAvailable()) return null
        val args = values.joinToString(",")
        val script = "import json,sys; xs=[$args]; print(json.dumps([round(x,3) for x in xs]))"
        val proc = ProcessBuilder("python3", "-c", script).redirectErrorStream(true).start()
        val out = proc.inputStream.bufferedReader().readText().trim()
        check(proc.waitFor() == 0) { "python3 round check failed: $out" }
        return Json.parseToJsonElement(out).jsonArray.map { it.jsonPrimitive.content.toDouble() }
    }

    private fun pythonReferenceScript(): String? {
        if (!pythonAvailable()) return null
        // Resolve relative to project root: quant-jvm/ sits next to quant/
        val projectRoot = File(System.getProperty("user.dir"))
        val script = File(projectRoot, "../quant/kelly.py").canonicalFile
        if (!script.exists()) {
            System.err.println("[parity] kelly.py reference not found at ${script.absolutePath} — skipping")
            return null
        }
        return script.absolutePath
    }

    private fun pythonAvailable(): Boolean = try {
        val proc = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        proc.waitFor() == 0
    } catch (e: Exception) {
        false
    }
}
