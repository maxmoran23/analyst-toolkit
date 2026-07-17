package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs

/** Executable parity contract for the unchanged `../quant/correlation.py` reference. */
class CorrelationParityTest {

    @Test
    fun `full JSON parity — named assets, crisis days present, rolling window active`() {
        requirePython()
        // Benchmark column dips below -0.05 more than 5 times so the crisis branch engages.
        val csv = crisisCsv()
        val args = arrayOf("--asset-names", "btc,eth,gold", "--window", "10", "--crisis-threshold", "-0.05")
        assertEquals(pythonCorrelation(csv, *args), kotlinCorrelation(csv, *args))
    }

    @Test
    fun `full JSON parity — default names, crisis and rolling branches gated off`() {
        requirePython()
        // Calm series: no crisis days, and a window larger than the sample disables rolling.
        val rows = List(12) { index ->
            listOf(0.001 * (index % 4 - 1), 0.002 * (index % 3 - 1), 0.0005 * (index % 5 - 2))
        }
        val csv = "x,y,z\n" + rows.joinToString("\n") { it.joinToString(",") }
        val args = arrayOf("--window", "30")
        val python = pythonCorrelation(csv, *args)
        val kotlin = kotlinCorrelation(csv, *args)
        assertEquals(python, kotlin)
        assertEquals(0, kotlin.jsonObject["crisis_correlation"]?.jsonObject?.size)
        assertEquals(0, kotlin.jsonObject["rolling_correlation_last_window"]?.jsonObject?.size)
    }

    @Test
    fun `raw corr agrees with the imported Python helper to 1e-10`() {
        requirePython()
        val x = listOf(0.012, -0.007, 0.004, -0.021, 0.018, 0.0, 0.009, -0.003, 0.014, -0.011)
        val y = listOf(-0.004, 0.006, -0.001, 0.017, -0.009, 0.002, -0.012, 0.008, -0.005, 0.01)
        val constant = List(10) { 0.01 }
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("correlation_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data = json.loads(sys.stdin.read())
            print(json.dumps({
                "xy": module.corr(data["x"], data["y"]),
                "xx": module.corr(data["x"], data["x"]),
                "zero_variance": module.corr(data["x"], data["constant"]),
                "short": module.corr([0.1], [0.2]),
            }))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use {
            it.write(
                """{"x": [${x.joinToString(",")}], "y": [${y.joinToString(",")}],""" +
                    """ "constant": [${constant.joinToString(",")}]}"""
            )
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        assertClose(python, "xy", corr(x, y))
        assertClose(python, "xx", corr(x, x))
        assertClose(python, "zero_variance", corr(x, constant))
        assertClose(python, "short", corr(listOf(0.1), listOf(0.2)))
    }

    @Test
    fun `corr primitives pass unconditional hand checks`() {
        assertEquals(1.0, corr(listOf(1.0, 2.0, 3.0), listOf(2.0, 4.0, 6.0)), 1e-15)
        assertEquals(-1.0, corr(listOf(1.0, 2.0, 3.0), listOf(6.0, 4.0, 2.0)), 1e-15)
        assertEquals(0.0, corr(listOf(1.0, 2.0, 3.0), listOf(5.0, 5.0, 5.0)), 0.0)
        assertEquals(0.0, corr(listOf(1.0), listOf(2.0)), 0.0)
        assertEquals(0.0, corr(emptyList(), emptyList()), 0.0)
    }

    @Test
    fun `CSV parsing skips headers and blank lines without Python`() {
        val csv = "asset_a,asset_b\n\n0.01,0.02\nnot,numeric\n0.03,-0.01\n"
        val cols = parseReturnsCsv(csv)
        assertEquals(listOf(listOf(0.01, 0.02), listOf(0.03, -0.01)), cols)

        val output = correlationOutput(cols, null, window = 2, crisisThreshold = -0.05)
        assertEquals("2", output["n_observations"]?.jsonPrimitive?.content)
        assertEquals("2", output["n_assets"]?.jsonPrimitive?.content)
        // Two perfectly anti-moving points in the window: rolling correlation is -1.
        assertEquals(
            "-1.0",
            output["rolling_correlation_last_window"]?.jsonObject
                ?.get("a1_vs_a0")?.jsonPrimitive?.content,
        )
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val ragged = File.createTempFile("corr-ragged-", ".csv")
        ragged.writeText("0.01,0.02,0.03\n0.04,0.05\n")
        val headerOnly = File.createTempFile("corr-header-", ".csv")
        headerOnly.writeText("a,b,c\n")
        try {
            val cases = listOf(
                evaluateCorrelation(emptyArray()),
                evaluateCorrelation(arrayOf("--returns-csv", "/nonexistent/returns.csv")),
                evaluateCorrelation(arrayOf("--returns-csv", ragged.absolutePath)),
                evaluateCorrelation(arrayOf("--returns-csv", headerOnly.absolutePath)),
                evaluateCorrelation(arrayOf("--window", "not-a-number")),
            )
            for (result in cases) {
                assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
                val parsed = Json.parseToJsonElement(result.output).jsonObject
                assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
            }
        } finally {
            ragged.delete()
            headerOnly.delete()
        }
    }

    // ----- helpers -----

    private fun crisisCsv(): String {
        val rows = List(24) { index ->
            val bench = if (index % 3 == 0) -0.06 - (index % 5) * 0.004 else 0.008 + (index % 4) * 0.002
            val second = bench * 0.7 + (index % 7) * 0.0015 - 0.004
            val third = -bench * 0.3 + (index % 5) * 0.001
            listOf(bench, second, third)
        }
        return "benchmark,alt,hedge\n" + rows.joinToString("\n") { it.joinToString(",") }
    }

    private fun kotlinCorrelation(csv: String, vararg args: String): JsonObject {
        val input = File.createTempFile("corr-kt-", ".csv")
        input.writeText(csv)
        try {
            val result = evaluateCorrelation(arrayOf("--returns-csv", input.absolutePath, *args))
            assertEquals(0, result.exitCode, result.output)
            return Json.parseToJsonElement(result.output).jsonObject
        } finally {
            input.delete()
        }
    }

    private fun pythonCorrelation(csv: String, vararg args: String): JsonObject {
        val input = File.createTempFile("corr-py-", ".csv")
        input.writeText(csv)
        try {
            val process = ProcessBuilder(
                "python3", pythonReference().absolutePath,
                "--returns-csv", input.absolutePath, *args,
            ).redirectErrorStream(true).start()
            val output = process.inputStream.bufferedReader().readText()
            check(process.waitFor() == 0) { "python3 correlation.py failed: $output" }
            return Json.parseToJsonElement(output).jsonObject
        } finally {
            input.delete()
        }
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
        File(System.getProperty("user.dir"), "../quant/correlation.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
