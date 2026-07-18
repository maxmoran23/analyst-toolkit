package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.max
import kotlin.math.sqrt

/**
 * Parity contract for `../quant/monte_carlo.py`, split by regime:
 *
 * - Deterministic skeleton (`percentile`, path max drawdown, output shaping) — exact §1.1
 *   parity against a Python oracle on fixed injected samples.
 * - Stochastic core (GBM / jump-GBM sampling) — §1.3 distributional agreement at N=10,000.
 *   Seeds are not cross-language comparable (different RNGs by design; see contract §1.3),
 *   so the comparison is between independent samples of the same process.
 *
 * Distributional tolerance: each statistic is compared within 6 * sqrt(2) * SE, where SE is
 * the sampling standard error estimated from the Kotlin sample (quantile SE via the
 * density-inverse method) and sqrt(2) accounts for both samples being noisy. Under
 * normality the per-statistic false-failure probability is ~2e-9 (6-sigma two-sided);
 * across the 18 statistics compared in this class that compounds to roughly 4e-8 per run —
 * comfortably under the 1e-6 flakiness budget, while a real process bug (wrong drift sign,
 * missing 0.5*vol^2 correction, mis-scaled dt) sits tens to hundreds of SE away. The
 * contract's 2 SE + retry scheme is deliberately traded for a wider no-retry bound: a CI
 * gate that flakes ~5% of the time is worse than one that detects only >6-sigma drift.
 */
class MonteCarloParityTest {

    @Test
    fun `percentile picks agree exactly with the imported Python helper`() {
        requirePython()
        val sorted = List(40) { 10.0 + it * 2.5 }
        val ps = listOf(0.0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1.0)
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("mc_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data = json.loads(sys.stdin.read())
            print(json.dumps([module.percentile(data["sorted"], p) for p in data["ps"]]))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use {
            it.write("""{"sorted": [${sorted.joinToString(",")}], "ps": [${ps.joinToString(",")}]}""")
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python percentile oracle failed: $output" }
        val pythonPicks = Json.parseToJsonElement(output).jsonArray
            .map { it.jsonPrimitive.content.toDouble() }

        for (i in ps.indices) {
            assertEquals(pythonPicks[i], percentile(sorted, ps[i]), 0.0, "percentile p=${ps[i]}")
        }
    }

    @Test
    fun `deterministic output shaping matches a Python oracle exactly on fixed samples`() {
        requirePython()
        // Unsorted on purpose: sorting is part of the shaping under test.
        val ep = List(40) { 100.0 + ((it * 37) % 41) * 3.7 - 60.0 }
        val dd = List(40) { (((it * 29) % 37).toDouble() / 40.0) }
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("mc_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data = json.loads(sys.stdin.read())
            spot, vol, drift, days, paths, jumps = 100.0, 0.6, 0.05, 30, 40, False
            ep = sorted(data["ep"])
            dd = sorted(data["dd"])
            mean_ending = sum(ep) / len(ep)
            percentile = module.percentile
            out = {
                "inputs": {"spot": spot, "vol": vol, "drift": drift, "days": days, "paths": paths, "jumps": jumps},
                "ending_price_distribution": {
                    "p05": round(percentile(ep, 0.05), 4),
                    "p25": round(percentile(ep, 0.25), 4),
                    "p50": round(percentile(ep, 0.50), 4),
                    "p75": round(percentile(ep, 0.75), 4),
                    "p95": round(percentile(ep, 0.95), 4),
                    "mean": round(mean_ending, 4),
                    "vs_spot_pct_p50": round((percentile(ep, 0.50) / spot - 1) * 100, 3),
                    "vs_spot_pct_p05": round((percentile(ep, 0.05) / spot - 1) * 100, 3),
                    "vs_spot_pct_p95": round((percentile(ep, 0.95) / spot - 1) * 100, 3),
                },
                "max_drawdown_distribution": {
                    "p50_max_dd_pct": round(percentile(dd, 0.50) * 100, 3),
                    "p75_max_dd_pct": round(percentile(dd, 0.75) * 100, 3),
                    "p95_max_dd_pct": round(percentile(dd, 0.95) * 100, 3),
                    "p99_max_dd_pct": round(percentile(dd, 0.99) * 100, 3),
                },
                "prob_below_spot": round(sum(1 for p in ep if p < spot) / len(ep) * 100, 2),
                "prob_halving": round(sum(1 for p in ep if p < spot * 0.5) / len(ep) * 100, 2),
                "prob_doubling": round(sum(1 for p in ep if p > spot * 2) / len(ep) * 100, 2),
            }
            print(json.dumps(out))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use {
            it.write("""{"ep": [${ep.joinToString(",")}], "dd": [${dd.joinToString(",")}]}""")
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python shaping oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        val kotlin = monteCarloSummary(ep, dd, 100.0, 0.6, 0.05, 30, 40, false)
        assertEquals(python, kotlin)
    }

    @Test
    fun `GBM distribution agrees with Python within 6 sqrt2 SE at N=10000`() {
        requirePython()
        val spot = 100.0
        val vol = 0.6
        val drift = 0.05
        val days = 30
        val paths = 10000
        val python = pythonMonteCarlo(
            "--spot", "$spot", "--vol", "$vol", "--drift", "$drift",
            "--days", "$days", "--paths", "$paths",
        )
        val kotlin = simulate(spot, vol, drift, days, paths, jumps = false, seed = 42L)
        assertDistributionsAgree(python, kotlin, spot)
    }

    @Test
    fun `jump-diffusion distribution agrees with Python within 6 sqrt2 SE at N=10000`() {
        requirePython()
        val spot = 100.0
        val vol = 0.8
        val days = 60
        val paths = 10000
        val python = pythonMonteCarlo(
            "--spot", "$spot", "--vol", "$vol", "--days", "$days", "--paths", "$paths", "--jumps",
        )
        val kotlin = simulate(spot, vol, 0.0, days, paths, jumps = true, seed = 42L)
        assertDistributionsAgree(python, kotlin, spot)
    }

    @Test
    fun `closed-form GBM moments hold for the Kotlin sampler (fixed seed)`() {
        // E[S_T] = spot * exp(drift * T) and median = spot * exp((drift - vol^2/2) * T)
        // for T = days * dt. Fixed seed makes this deterministic; the 6 SE bound is the
        // same detection margin used cross-language.
        val spot = 100.0
        val vol = 0.5
        val drift = 0.10
        val days = 60
        val paths = 10000
        val t = days * (1.0 / 365.0)
        val result = simulate(spot, vol, drift, days, paths, jumps = false, seed = 4242L)
        val ep = result.endingPrices.sorted()

        val mean = ep.sum() / ep.size
        val meanSe = sampleSd(ep) / sqrt(ep.size.toDouble())
        val expectedMean = spot * exp(drift * t)
        assertTrue(
            abs(mean - expectedMean) < 6.0 * meanSe,
            "GBM mean off closed form: sample=$mean expected=$expectedMean se=$meanSe",
        )

        val median = percentile(ep, 0.50)
        val medianSe = quantileSe(ep, 0.50)
        val expectedMedian = spot * exp((drift - 0.5 * vol * vol) * t)
        assertTrue(
            abs(median - expectedMedian) < 6.0 * medianSe,
            "GBM median off closed form: sample=$median expected=$expectedMedian se=$medianSe",
        )
    }

    @Test
    fun `skeleton primitives pass unconditional hand checks`() {
        val sorted = listOf(1.0, 2.0, 3.0, 4.0)
        assertEquals(3.0, percentile(sorted, 0.5), 0.0)   // idx = int(2.0) = 2
        assertEquals(1.0, percentile(sorted, 0.0), 0.0)
        assertEquals(4.0, percentile(sorted, 1.0), 0.0)   // idx 4 clamps to 3
        assertEquals(1.0, percentile(sorted, 0.24), 0.0)  // int(0.96) truncates to 0
        assertEquals(1.0, percentile(sorted, -0.5), 0.0)  // negative clamps to 0

        assertEquals(0.25, pathMaxDrawdown(listOf(100.0, 120.0, 90.0, 130.0, 110.0)), 1e-15)
        assertEquals(0.0, pathMaxDrawdown(listOf(1.0, 2.0, 3.0)), 0.0)

        val summary = monteCarloSummary(
            listOf(50.0, 80.0, 120.0, 250.0), listOf(0.1, 0.2, 0.3, 0.4),
            spot = 100.0, vol = 0.5, drift = 0.0, days = 5, paths = 4, jumps = false,
        )
        assertEquals("50.0", summary["prob_below_spot"]?.jsonPrimitive?.content)
        assertEquals("0.0", summary["prob_halving"]?.jsonPrimitive?.content)
        assertEquals("25.0", summary["prob_doubling"]?.jsonPrimitive?.content)
        assertEquals(
            "30.0",
            summary["max_drawdown_distribution"]?.jsonObject?.get("p50_max_dd_pct")?.jsonPrimitive?.content,
        )
    }

    @Test
    fun `fixed seed reproduces identical output and a new seed changes it`() {
        val args = arrayOf("--spot", "100", "--vol", "0.8", "--days", "20", "--paths", "300", "--seed", "7")
        val first = evaluateMonteCarlo(args)
        val second = evaluateMonteCarlo(args)
        assertEquals(0, first.exitCode, first.output)
        assertEquals(first.output, second.output, "same seed must reproduce identical output")

        val reseeded = evaluateMonteCarlo(
            arrayOf("--spot", "100", "--vol", "0.8", "--days", "20", "--paths", "300", "--seed", "8"),
        )
        assertNotEquals(first.output, reseeded.output, "different seed should perturb the sample")
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val cases = listOf(
            evaluateMonteCarlo(emptyArray()),
            evaluateMonteCarlo(arrayOf("--vol", "0.5")),
            evaluateMonteCarlo(arrayOf("--spot", "100")),
            evaluateMonteCarlo(arrayOf("--spot", "100", "--vol", "0.5", "--paths", "0")),
            evaluateMonteCarlo(arrayOf("--spot", "0", "--vol", "0.5", "--paths", "50")),
            evaluateMonteCarlo(arrayOf("--spot", "100", "--vol", "0.5", "--paths", "abc")),
        )
        for (result in cases) {
            assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
            val parsed = Json.parseToJsonElement(result.output).jsonObject
            assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
        }
    }

    // ----- distributional helpers -----

    private fun assertDistributionsAgree(python: JsonObject, kotlin: SimulationResult, spot: Double) {
        val ep = kotlin.endingPrices.sorted()
        val dd = kotlin.maxDrawdowns.sorted()
        val pythonEp = python["ending_price_distribution"]!!.jsonObject
        val pythonDd = python["max_drawdown_distribution"]!!.jsonObject

        for ((key, q) in listOf("p05" to 0.05, "p25" to 0.25, "p50" to 0.50, "p75" to 0.75, "p95" to 0.95)) {
            assertWithinBound(
                "ending $key",
                pythonEp[key]!!.jsonPrimitive.content.toDouble(),
                percentile(ep, q),
                quantileSe(ep, q),
                roundingHalfStep = 0.5e-4,
            )
        }
        assertWithinBound(
            "ending mean",
            pythonEp["mean"]!!.jsonPrimitive.content.toDouble(),
            ep.sum() / ep.size,
            sampleSd(ep) / sqrt(ep.size.toDouble()),
            roundingHalfStep = 0.5e-4,
        )
        // dd p99 is excluded: density-inverse SE estimation is unreliable that deep in the
        // tail; p50/p75/p95 provide the drawdown-shape coverage.
        for ((key, q) in listOf("p50_max_dd_pct" to 0.50, "p75_max_dd_pct" to 0.75, "p95_max_dd_pct" to 0.95)) {
            assertWithinBound(
                "drawdown $key",
                pythonDd[key]!!.jsonPrimitive.content.toDouble(),
                percentile(dd, q) * 100.0,
                quantileSe(dd, q) * 100.0,
                roundingHalfStep = 0.5e-3,
            )
        }
        // Sanity anchor, not a statistical bound: both sides must see a nontrivial spread.
        assertTrue(percentile(ep, 0.95) > percentile(ep, 0.05), "degenerate Kotlin sample")
        assertTrue(pythonEp["p95"]!!.jsonPrimitive.content.toDouble() > pythonEp["p05"]!!.jsonPrimitive.content.toDouble())
        assertTrue(spot > 0.0)
    }

    private fun assertWithinBound(
        label: String,
        pythonValue: Double,
        kotlinValue: Double,
        se: Double,
        roundingHalfStep: Double,
    ) {
        val bound = 6.0 * sqrt(2.0) * se + roundingHalfStep
        val difference = abs(pythonValue - kotlinValue)
        assertTrue(
            difference < bound,
            "$label distributional break: python=$pythonValue kotlin=$kotlinValue " +
                "difference=$difference bound=$bound",
        )
    }

    /** Quantile standard error via the density-inverse (slope) method on the sample. */
    private fun quantileSe(sorted: List<Double>, q: Double): Double {
        val n = sorted.size
        val delta = 0.02
        val slope = (percentile(sorted, q + delta) - percentile(sorted, q - delta)) / (2.0 * delta)
        return max(slope * sqrt(q * (1.0 - q) / n), 1e-12)
    }

    private fun sampleSd(xs: List<Double>): Double {
        val mean = xs.sum() / xs.size
        return sqrt(xs.sumOf { (it - mean) * (it - mean) } / (xs.size - 1))
    }

    // ----- process helpers -----

    private fun pythonMonteCarlo(vararg args: String): JsonObject {
        val process = ProcessBuilder("python3", pythonReference().absolutePath, *args)
            .redirectErrorStream(true).start()
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "python3 monte_carlo.py failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
    }

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/monte_carlo.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
