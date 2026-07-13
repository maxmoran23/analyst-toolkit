package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs
import kotlin.math.sqrt

/** Executable parity contract for the unchanged `../quant/sharpe.py` reference. */
class SharpeParityTest {

    @Test
    fun `raw mixed-return math agrees with imported Python helpers`() {
        requirePython()
        val returns = mixedReturns()
        val riskFreeRate = 0.0375
        val annualize = 365
        val python = rawPythonOracle(returns, riskFreeRate, annualize)
        val kotlin = calculateSharpeMetrics(returns, riskFreeRate, annualize)

        assertClose(python, "periodic_rf", kotlin.periodicRiskFreeRate)
        assertClose(python, "mean_excess", kotlin.meanExcessReturn)
        assertClose(python, "annualized_vol", kotlin.annualizedVolatility)
        assertClose(python, "cagr", kotlin.cagr)
        assertClose(python, "sharpe", kotlin.sharpe)
        assertClose(python, "sortino", kotlin.sortino)
        assertClose(python, "calmar", kotlin.calmar)
        assertClose(python, "omega", kotlin.omega)
        assertClose(python, "max_drawdown", kotlin.maximumDrawdown)
        assertClose(python, "win_rate", kotlin.winRate)
        assertClose(python, "avg_win", kotlin.averageWin)
        assertClose(python, "avg_loss", kotlin.averageLoss)
        assertClose(python, "profit_factor", kotlin.profitFactor)
    }

    @Test
    fun `public rounded JSON contract exactly matches Python`() {
        requirePython()
        val returns = mixedReturns()
        val python = publicPythonOutput(returns, 0.05, 252)
        val kotlin = sharpeOutput(returns, 0.05, 252)

        assertEquals(python.keys, kotlin.keys, "public field set changed")
        for (key in python.keys) {
            assertEquals(python[key], kotlin[key], "public field '$key' differs")
        }
    }

    @Test
    fun `zero volatility and downside preserve zero ratios and inf strings`() {
        requirePython()
        val returns = List(30) { 0.01 }
        val python = publicPythonOutput(returns, 0.0, 252)
        val kotlin = sharpeOutput(returns, 0.0, 252)

        assertEquals(python, kotlin)
        assertEquals("0.0", kotlin["sharpe"]?.jsonPrimitive?.content)
        assertEquals("0.0", kotlin["sortino"]?.jsonPrimitive?.content)
        assertEquals("inf", kotlin["omega"]?.jsonPrimitive?.content)
        assertEquals("inf", kotlin["profit_factor"]?.jsonPrimitive?.content)
    }

    @Test
    fun `drawdown and ratio primitives pass unconditional hand checks`() {
        assertEquals(2.0, mean(listOf(1.0, 2.0, 3.0)), 0.0)
        assertEquals(1.0, sampleStandardDeviation(listOf(1.0, 2.0, 3.0)), 1e-15)
        assertEquals(sqrt(0.005), downsideDeviation(listOf(-0.1, 0.1)), 1e-15)
        assertEquals(0.2, maxDrawdown(listOf(0.10, -0.20, 0.05)), 1e-15)
        assertEquals(2.0, sharpeRatio(0.01, 0.005, 1), 1e-15)
        assertEquals(2.0, sortinoRatio(0.01, 0.005, 1), 1e-15)
        assertEquals(2.0, calmarRatio(0.20, 0.10), 1e-15)
        assertEquals(2.0, omegaRatio(listOf(0.02, -0.01), 0.0), 1e-15)
        assertTrue(omegaRatio(List(30) { 0.01 }, 0.0).isInfinite())
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val cases = listOf(
            evaluateSharpe(emptyArray()),
            evaluateSharpe(arrayOf("--stdin"), "[0.01]"),
            evaluateSharpe(arrayOf("--stdin"), "not-json"),
            evaluateSharpe(arrayOf("--stdin"), "{\"return\": 0.1}"),
            evaluateSharpe(arrayOf("--stdin"), "[\"0.1\"]"),
            evaluateSharpe(arrayOf("--stdin", "--annualize", "0"), returnsJson(mixedReturns())),
            evaluateSharpe(arrayOf("--stdin", "--rf", "not-a-number"), returnsJson(mixedReturns())),
        )

        for (result in cases) {
            assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
            val parsed = Json.parseToJsonElement(result.output).jsonObject
            assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
        }
    }

    @Test
    fun `CLI evaluator accepts returns file and applies annualization options`() {
        val input = File.createTempFile("sharpe-returns-", ".json")
        input.writeText(returnsJson(mixedReturns()))
        try {
            val result = evaluateSharpe(arrayOf(
                "--returns-json", input.absolutePath,
                "--rf", "0.02",
                "--annualize", "365",
            ))
            assertEquals(0, result.exitCode, result.output)
            val output = Json.parseToJsonElement(result.output).jsonObject
            assertEquals("365", output["annualize_factor"]?.jsonPrimitive?.content)
            assertEquals("0.02", output["risk_free_rate"]?.jsonPrimitive?.content)
        } finally {
            input.delete()
        }
    }

    private fun mixedReturns(): List<Double> {
        val pattern = listOf(0.012, -0.007, 0.004, -0.021, 0.018, 0.0, 0.009, -0.003)
        return List(40) { index -> pattern[index % pattern.size] + (index % 5) * 0.0001 }
    }

    private fun returnsJson(returns: List<Double>): String =
        buildJsonArray { returns.forEach { add(JsonPrimitive(it)) } }.toString()

    private fun assertClose(python: JsonObject, key: String, kotlinValue: Double) {
        val pythonValue = python[key]?.jsonPrimitive?.content?.toDouble()
            ?: error("Python oracle omitted '$key': $python")
        val difference = abs(pythonValue - kotlinValue)
        assertTrue(
            difference < 1e-10,
            "$key parity failure: python=$pythonValue kotlin=$kotlinValue difference=$difference",
        )
    }

    private fun publicPythonOutput(
        returns: List<Double>,
        riskFreeRate: Double,
        annualize: Int,
    ): JsonObject {
        val process = ProcessBuilder(
            "python3", pythonReference().absolutePath,
            "--stdin", "--rf", riskFreeRate.toString(), "--annualize", annualize.toString(),
        ).redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { it.write(returnsJson(returns)) }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python public oracle failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
    }

    private fun rawPythonOracle(
        returns: List<Double>,
        riskFreeRate: Double,
        annualize: Int,
    ): JsonObject {
        val script = """
            import importlib.util, json, math, sys
            spec = importlib.util.spec_from_file_location("sharpe_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            returns = json.loads(sys.stdin.read())
            rf = float(sys.argv[2])
            annualize = int(sys.argv[3])
            n = len(returns)
            periodic_rf = (1 + rf) ** (1 / annualize) - 1
            excess = [r - periodic_rf for r in returns]
            mu = module.mean(excess)
            sigma = module.stdev(excess)
            downside = module.downside_stdev(returns, target=periodic_rf)
            sharpe = (mu / sigma) * math.sqrt(annualize) if sigma > 0 else 0.0
            sortino = (mu / downside) * math.sqrt(annualize) if downside > 0 else 0.0
            total_return = 1.0
            for value in returns:
                total_return *= 1 + value
            cagr = total_return ** (annualize / n) - 1
            drawdown = module.max_drawdown(returns)
            calmar = cagr / drawdown if drawdown > 0 else 0.0
            gains = sum(max(0, value - periodic_rf) for value in returns)
            losses = sum(max(0, periodic_rf - value) for value in returns)
            omega = gains / losses if losses > 0 else float("inf")
            wins = sum(1 for value in returns if value > 0)
            avg_win = module.mean([value for value in returns if value > 0]) if wins else 0.0
            avg_loss = module.mean([value for value in returns if value < 0]) if (n - wins) else 0.0
            profit_factor = abs(
                sum(value for value in returns if value > 0) /
                sum(value for value in returns if value < 0)
            ) if any(value < 0 for value in returns) else float("inf")
            print(json.dumps({
                "periodic_rf": periodic_rf,
                "mean_excess": mu,
                "annualized_vol": sigma * math.sqrt(annualize),
                "cagr": cagr,
                "sharpe": sharpe,
                "sortino": sortino,
                "calmar": calmar,
                "omega": omega,
                "max_drawdown": drawdown,
                "win_rate": wins / n,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "profit_factor": profit_factor,
            }))
        """.trimIndent()
        val process = ProcessBuilder(
            "python3", "-c", script,
            pythonReference().absolutePath,
            riskFreeRate.toString(), annualize.toString(),
        ).redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { it.write(returnsJson(returns)) }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
    }

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/sharpe.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
