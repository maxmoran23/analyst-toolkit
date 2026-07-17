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
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

/** Executable parity contract for the unchanged `../quant/vol.py` reference. */
class VolParityTest {

    @Test
    fun `realized and ewma public JSON contracts exactly match Python`() {
        requirePython()
        val returns = mixedReturns()
        withTempJson(numbersJson(returns)) { path ->
            assertEquals(
                pythonVol("--returns-json", path, "--method", "realized"),
                kotlinVol("--returns-json", path, "--method", "realized"),
            )
            assertEquals(
                pythonVol(
                    "--returns-json", path, "--method", "ewma",
                    "--annualize", "365", "--ewma-lambda", "0.9",
                ),
                kotlinVol(
                    "--returns-json", path, "--method", "ewma",
                    "--annualize", "365", "--ewma-lambda", "0.9",
                ),
            )
        }
    }

    @Test
    fun `parkinson and garman_klass public JSON contracts exactly match Python`() {
        requirePython()
        withTempJson(ohlcJson(ohlcBars())) { path ->
            for (method in listOf("parkinson", "garman_klass")) {
                assertEquals(
                    pythonVol("--ohlc-json", path, "--method", method, "--annualize", "365"),
                    kotlinVol("--ohlc-json", path, "--method", method, "--annualize", "365"),
                    "method '$method' diverged",
                )
            }
        }
    }

    @Test
    fun `garch parity — full contract and the short-series exit-0 error merge`() {
        requirePython()
        withTempJson(numbersJson(mixedReturns())) { path ->
            assertEquals(
                pythonVol("--returns-json", path, "--method", "garch"),
                kotlinVol("--returns-json", path, "--method", "garch"),
            )
        }
        // Python merges {"error": ...} into the result and still exits 0 for < 20 returns.
        withTempJson(numbersJson(List(5) { 0.01 })) { path ->
            val python = pythonVol("--returns-json", path, "--method", "garch")
            val kotlin = kotlinVol("--returns-json", path, "--method", "garch")
            assertEquals(python, kotlin)
            assertTrue(kotlin.containsKey("error"), "short-series garch must carry the error field")
        }
    }

    @Test
    fun `raw estimator math agrees with imported Python helpers to 1e-10`() {
        requirePython()
        val returns = mixedReturns()
        val bars = ohlcBars()
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("vol_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data = json.loads(sys.stdin.read())
            returns = data["returns"]
            ohlc = data["ohlc"]
            pairs = [(bar[1], bar[2]) for bar in ohlc]
            print(json.dumps({
                "realized": module.realized_vol(returns, 252),
                "ewma": module.ewma_vol(returns, 0.9, 365),
                "parkinson": module.parkinson_vol(pairs, 252),
                "garman_klass": module.garman_klass_vol(ohlc, 252),
            }))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use {
            it.write("""{"returns": ${numbersJson(returns)}, "ohlc": ${ohlcJson(bars)}}""")
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        assertClose(python, "realized", realizedVol(returns, 252))
        assertClose(python, "ewma", ewmaVol(returns, 0.9, 365))
        assertClose(python, "parkinson", parkinsonVol(bars.map { it.high to it.low }, 252))
        assertClose(python, "garman_klass", garmanKlassVol(bars, 252))
    }

    @Test
    fun `estimator primitives pass unconditional hand checks`() {
        // Two returns, zero mean: sample variance 0.02, annualize=1.
        assertEquals(sqrt(0.02), realizedVol(listOf(0.1, -0.1), 1), 1e-15)
        assertEquals(0.0, realizedVol(listOf(0.1), 1), 0.0)
        // Single return seeds EWMA variance directly.
        assertEquals(0.1, ewmaVol(listOf(0.1), 0.94, 1), 1e-15)
        assertEquals(0.0, ewmaVol(emptyList(), 0.94, 252), 0.0)
        // One pair with log range 1: variance = 1 / (4 ln 2).
        assertEquals(sqrt(1.0 / (4.0 * ln(2.0))), parkinsonVol(listOf(exp(1.0) to 1.0), 1), 1e-15)
        // One bar, close == open: variance = 0.5 * ln(h/l)^2 = 0.5.
        assertEquals(sqrt(0.5), garmanKlassVol(listOf(OhlcBar(1.0, exp(1.0), 1.0, 1.0)), 1), 1e-15)
    }

    @Test
    fun `garch hand check — constant returns sit at the recursion fixed point`() {
        // r = 0.01 constant: unconditional = 1e-4 and the recursion is stationary at it,
        // so forecast, conditional, and unconditional vols coincide; persistence = 0.95.
        val result = simpleGarch(List(20) { 0.01 }, annualize = 252)
        val expected = round3(0.01 * sqrt(252.0) * 100.0)
        assertEquals(expected, result["garch_annualized_vol_pct"]?.jsonPrimitive?.content?.toDouble())
        assertEquals(expected, result["current_conditional_vol_pct"]?.jsonPrimitive?.content?.toDouble())
        assertEquals(expected, result["unconditional_annual_vol_pct"]?.jsonPrimitive?.content?.toDouble())
        assertEquals(0.95, result["persistence"]?.jsonPrimitive?.content?.toDouble())

        assertEquals("need >= 20 returns", simpleGarch(List(19) { 0.01 })["error"]?.jsonPrimitive?.content)
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val cases = listOf(
            evaluateVol(arrayOf("--method", "realized")),
            evaluateVol(arrayOf("--method", "parkinson")),
            evaluateVol(arrayOf("--returns-json", "/nonexistent/returns.json")),
            evaluateVol(arrayOf("--method", "not-a-method")),
            evaluateVol(arrayOf("--annualize", "not-a-number")),
        )
        for (result in cases) {
            assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
            val parsed = Json.parseToJsonElement(result.output).jsonObject
            assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
        }
    }

    // ----- helpers -----

    private fun mixedReturns(): List<Double> {
        val pattern = listOf(0.011, -0.008, 0.005, -0.019, 0.016, 0.0, 0.007, -0.004)
        return List(40) { index -> pattern[index % pattern.size] + (index % 7) * 0.0001 }
    }

    private fun ohlcBars(): List<OhlcBar> = List(30) { index ->
        val base = 100.0 + index * 0.7
        OhlcBar(
            open = base,
            high = base * (1.02 + (index % 3) * 0.004),
            low = base * (0.985 - (index % 4) * 0.003),
            close = base * (1.0 + (if (index % 2 == 0) 0.006 else -0.005)),
        )
    }

    private fun numbersJson(values: List<Double>): String =
        buildJsonArray { values.forEach { add(JsonPrimitive(it)) } }.toString()

    private fun ohlcJson(bars: List<OhlcBar>): String =
        bars.joinToString(",", "[", "]") { "[${it.open},${it.high},${it.low},${it.close}]" }

    private fun withTempJson(text: String, block: (String) -> Unit) {
        val input = File.createTempFile("vol-input-", ".json")
        input.writeText(text)
        try {
            block(input.absolutePath)
        } finally {
            input.delete()
        }
    }

    private fun kotlinVol(vararg args: String): JsonObject {
        val result = evaluateVol(arrayOf(*args))
        assertEquals(0, result.exitCode, result.output)
        return Json.parseToJsonElement(result.output).jsonObject
    }

    private fun pythonVol(vararg args: String): JsonObject {
        val process = ProcessBuilder("python3", pythonReference().absolutePath, *args)
            .redirectErrorStream(true).start()
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "python3 vol.py failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
    }

    private fun assertClose(python: JsonObject, key: String, kotlinValue: Double) {
        val pythonValue = python[key]?.jsonPrimitive?.content?.toDouble()
            ?: error("Python oracle omitted '$key': $python")
        val difference = abs(pythonValue - kotlinValue)
        assertTrue(
            difference < 1e-10,
            "$key parity failure: python=$pythonValue kotlin=$kotlinValue difference=$difference",
        )
    }

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/vol.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
