package org.maxmoran.quant

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.jsonObject
import java.io.File
import java.util.Random
import kotlin.math.exp

class SeriesBoundaryTest {
    @Test
    fun `volatility rejects invalid samples frequency and coefficients`() {
        for (annualize in listOf(0, -1)) {
            assertThrows(IllegalArgumentException::class.java) { realizedVol(listOf(.1, -.1), annualize) }
        }
        assertThrows(IllegalArgumentException::class.java) { realizedVol(listOf(.1, Double.NaN)) }
        assertThrows(IllegalArgumentException::class.java) { ewmaVol(listOf(.1), lam = 1.1) }
        assertThrows(IllegalArgumentException::class.java) { simpleGarch(List(20) { .01 }, alpha = .2, beta = .8) }
        assertThrows(IllegalArgumentException::class.java) { simpleGarch(List(20) { .01 }, omega = -.1) }
        assertThrows(IllegalArgumentException::class.java) { sampleStandardDeviation(listOf(1.0, 2.0), ddof = 2) }
    }

    @Test
    fun `invalid OHLC bars cannot dilute estimates`() {
        assertThrows(IllegalArgumentException::class.java) { parkinsonVol(listOf(2.0 to 0.0)) }
        assertThrows(IllegalArgumentException::class.java) { parkinsonVol(listOf(1.0 to 2.0)) }
        assertThrows(IllegalArgumentException::class.java) { garmanKlassVol(listOf(OhlcBar(3.0, 2.0, 1.0, 1.0))) }
        assertThrows(IllegalArgumentException::class.java) { garmanKlassVol(emptyList()) }
    }

    @Test
    fun `complete loss is valid but negative equity and returns beyond total loss are not`() {
        assertEquals(listOf(1.0, .5, 0.0, 0.0), equityFromReturns(listOf(-.5, -1.0, .2)))
        assertEquals(listOf(0.0, 1.0, 1.0), drawdownSeries(listOf(100.0, 0.0, 0.0)))
        assertThrows(IllegalArgumentException::class.java) { equityFromReturns(listOf(-1.01)) }
        assertThrows(IllegalArgumentException::class.java) { equityFromReturns(listOf(.1), start = 0.0) }
        assertThrows(IllegalArgumentException::class.java) { drawdownOutput(listOf(100.0, 99.0), topN = -1) }
        assertThrows(IllegalArgumentException::class.java) { calculateSharpeMetrics(List(30) { .01 }, riskFreeRate = -1.0) }
        assertThrows(IllegalArgumentException::class.java) { calculateSharpeMetrics(List(30) { -1.01 }) }
    }

    @Test
    fun `correlation rejects alignment labels and malformed CSV rows`() {
        assertThrows(IllegalArgumentException::class.java) { corr(listOf(1.0), listOf(1.0, 2.0)) }
        assertThrows(IllegalArgumentException::class.java) { corr(listOf(1.0, Double.NaN), listOf(1.0, 2.0)) }
        for (csv in listOf("a,b\n1,2\nbad,row\n3,4", "1,2\n3\n", "1,2\nNaN,4", "a,2\n1,2\n3,4")) {
            assertThrows(IllegalArgumentException::class.java) { parseReturnsCsv(csv) }
        }
        val rows = parseReturnsCsv("a,b\n\"1\",\"2\"\n3,4")
        assertEquals(listOf(listOf(1.0, 2.0), listOf(3.0, 4.0)), rows)
        assertThrows(IllegalArgumentException::class.java) { correlationOutput(rows, listOf("a", "a")) }
        assertThrows(IllegalArgumentException::class.java) { correlationOutput(rows, listOf("a", "b", "c")) }
        assertThrows(IllegalArgumentException::class.java) { correlationOutput(rows, null, window = 0) }
    }

    @Test
    fun `simulation deterministic limits and invalid input checks`() {
        assertEquals(listOf(100.0), gbmPath(100.0, .1, .2, 0, rng = Random(1)))
        assertEquals(100 * exp(.1), gbmPath(100.0, .1, 0.0, 2, dt = .5, rng = Random(1)).last(), 1e-12)
        assertThrows(IllegalArgumentException::class.java) { gbmPath(0.0, 0.0, .1, 1, rng = Random(1)) }
        assertThrows(IllegalArgumentException::class.java) { gbmPath(100.0, 0.0, -.1, 1, rng = Random(1)) }
        assertThrows(IllegalArgumentException::class.java) { gbmPath(100.0, 0.0, .1, -1, rng = Random(1)) }
        assertThrows(IllegalArgumentException::class.java) { jumpGbmPath(100.0, 0.0, .1, 1, jumpIntensity = 366.0, rng = Random(1)) }
        assertThrows(IllegalArgumentException::class.java) { simulate(100.0, .1, paths = 0) }
        assertThrows(IllegalArgumentException::class.java) { percentile(listOf(2.0, 1.0), .5) }
        assertThrows(IllegalArgumentException::class.java) { monteCarloSummary(listOf(100.0), emptyList(), 100.0, .1, 0.0, 1, 1, false) }
    }

    @Test
    fun `extreme OHLC and constant crisis subset cannot produce favorable false zeros`() {
        val value = garmanKlassVol(listOf(OhlcBar(1e-308, 1e308, 1e-308, 1e308)), 1)
        assertTrue(value.isFinite() && value > 0)
        assertThrows(IllegalArgumentException::class.java) { downsideDeviation(listOf(-1e308), 1e308) }
        val rows = List(6) { listOf(-.125, -.25) } + listOf(listOf(.125, .25), listOf(.25, .5))
        val result = correlationOutput(rows, null)
        assertEquals(JsonNull, result["crisis_correlation"]!!.jsonObject["a0__a1"])
        assertTrue(result["correlation_compression"]!!.jsonObject.isEmpty())
    }

    @Test
    fun `nonconstant correlation underflow is rejected`() {
        assertThrows(IllegalArgumentException::class.java) { corr(listOf(1e-200, 2e-200), listOf(1e-200, 2e-200)) }
    }

    @Test
    fun `Markowitz accepts one asset but rejects malformed numeric rows`() {
        val file = File.createTempFile("single-asset-", ".csv")
        try {
            file.writeText("asset\n0.01\n0.02\n-0.01\n")
            assertEquals(0, evaluateMarkowitz(arrayOf("--returns-csv", file.path)).exitCode)
            file.writeText("asset\n0.01\nbad\n0.02\n-0.01\n")
            assertTrue(evaluateMarkowitz(arrayOf("--returns-csv", file.path)).exitCode != 0)
        } finally {
            file.delete()
        }
    }

    @Test
    fun `Python and Kotlin reject invalid CLI inputs in both languages`() {
        val root = File(System.getProperty("user.dir"), "../quant").canonicalFile
        val returns = File.createTempFile("series-contract-", ".json")
        val csv = File.createTempFile("series-contract-", ".csv")
        try {
            returns.writeText(List(30) { .01 }.joinToString(",", "[", "]"))
            csv.writeText("1,2\n3,4\n")
            val cases = listOf(
                Triple("sharpe", arrayOf("--returns-json", returns.path, "--rf", "-1"), ::evaluateSharpeCode),
                Triple("vol", arrayOf("--returns-json", returns.path, "--annualize", "0"), ::evaluateVolCode),
                Triple("monte_carlo", arrayOf("--spot", "100", "--vol", ".1", "--paths", "0"), ::evaluateMcCode),
                Triple("correlation", arrayOf("--returns-csv", csv.path, "--window", "0"), ::evaluateCorrCode),
                Triple("correlation", arrayOf("--returns-csv", csv.path, "--asset-names", "a,a"), ::evaluateCorrCode),
                Triple("drawdown", arrayOf("--returns-json", returns.path, "--top-n", "-1"), ::evaluateDdCode),
            )
            for ((module, args, evaluate) in cases) {
                val process = ProcessBuilder("python3", File(root, "$module.py").path, *args).redirectErrorStream(true).start()
                process.inputStream.bufferedReader().readText()
                assertTrue(process.waitFor() != 0, "$module Python accepted invalid input")
                assertTrue(evaluate(args) != 0, "$module Kotlin accepted invalid input")
            }
        } finally {
            returns.delete()
            csv.delete()
        }
    }

    private fun evaluateSharpeCode(args: Array<String>) = evaluateSharpe(args).exitCode
    private fun evaluateVolCode(args: Array<String>) = evaluateVol(args).exitCode
    private fun evaluateMcCode(args: Array<String>) = evaluateMonteCarlo(args).exitCode
    private fun evaluateCorrCode(args: Array<String>) = evaluateCorrelation(args).exitCode
    private fun evaluateDdCode(args: Array<String>) = evaluateDrawdown(args).exitCode
}
