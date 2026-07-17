package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs

/** Executable parity contract for the unchanged `../quant/drawdown.py` reference. */
class DrawdownParityTest {

    @Test
    fun `equity input parity — full JSON including episodes and unrecovered tail`() {
        requirePython()
        // Two recovered episodes plus an unrecovered tail; single-point series as a degenerate case.
        val equity = listOf(100.0, 105.0, 98.0, 90.0, 104.0, 110.0, 107.0, 111.0, 108.0, 102.0, 109.0)
        assertEquals(pythonDrawdown("--equity-json", numbersJson(equity)), kotlinDrawdown(equity))

        val single = listOf(100.0)
        assertEquals(pythonDrawdown("--equity-json", numbersJson(single)), kotlinDrawdown(single))
    }

    @Test
    fun `returns input parity — compounding, sort order, and top-n truncation`() {
        requirePython()
        // Each dip is out-earned by the following up-legs, so every cycle closes an episode.
        val pattern = listOf(0.05, -0.02, 0.04, -0.03, 0.06, -0.01)
        val returns = List(48) { index -> pattern[index % pattern.size] + (index % 5) * 0.0002 }
        val python = pythonDrawdown("--returns-json", numbersJson(returns), topN = 2)
        val kotlin = kotlinDrawdownFromReturns(returns, topN = 2)

        assertEquals(python, kotlin)
        assertEquals(2, kotlin.jsonObject["top_drawdowns"]?.jsonArray?.size)
    }

    @Test
    fun `raw drawdown series agrees with imported Python helper to 1e-10`() {
        requirePython()
        val equity = listOf(1.0, 1.04, 0.97, 0.91, 1.02, 1.11, 1.05, 1.13, 1.06, 0.99)
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("drawdown_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            equity = json.loads(sys.stdin.read())
            print(json.dumps(module.drawdown_series(equity)))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { it.write(numbersJson(equity)) }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonArray.map { it.jsonPrimitive.content.toDouble() }
        val kotlin = drawdownSeries(equity)

        assertEquals(python.size, kotlin.size)
        for (i in python.indices) {
            val difference = abs(python[i] - kotlin[i])
            assertTrue(difference < 1e-10, "dds[$i]: python=${python[i]} kotlin=${kotlin[i]}")
        }
    }

    @Test
    fun `hand-math spot check runs without Python`() {
        // equity [100, 120, 90, 130, 110]: one recovered episode (25% dd, 2 days), one open tail.
        val equity = listOf(100.0, 120.0, 90.0, 130.0, 110.0)
        val output = Json.parseToJsonElement(evaluate(equity)).jsonObject

        assertEquals("25.0", output["max_drawdown_pct"]?.jsonPrimitive?.content)
        assertEquals("15.385", output["current_drawdown_pct"]?.jsonPrimitive?.content)
        assertEquals("8.077", output["avg_drawdown_pct"]?.jsonPrimitive?.content)
        assertEquals("40.0", output["pct_time_underwater"]?.jsonPrimitive?.content)
        assertEquals("2", output["n_drawdown_episodes"]?.jsonPrimitive?.content)
        assertEquals("2.0", output["avg_recovery_days"]?.jsonPrimitive?.content)

        val top = output["top_drawdowns"]!!.jsonArray
        val first = top[0].jsonObject
        assertEquals("25.0", first["dd_pct"]?.jsonPrimitive?.content)
        assertEquals("3", first["recovery_idx"]?.jsonPrimitive?.content)
        val tail = top[1].jsonObject
        assertEquals("true", tail["still_underwater"]?.jsonPrimitive?.content)
        assertEquals("null", tail["recovery_idx"].toString())
    }

    @Test
    fun `episode primitives pass unconditional hand checks`() {
        assertEquals(listOf(1.0, 1.1, 0.99), equityFromReturns(listOf(0.1, -0.1)).map { round3(it) })
        assertEquals(emptyList<DrawdownEpisode>(), recoveryEpisodes(listOf(1.0, 2.0, 3.0)))
        assertEquals(listOf(0.0), drawdownSeries(listOf(1.0)))
        // Non-positive running peak collapses drawdown to zero, matching the Python guard.
        assertEquals(listOf(0.0, 0.0), drawdownSeries(listOf(-1.0, -2.0)))
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val emptyEquity = File.createTempFile("drawdown-empty-", ".json")
        emptyEquity.writeText("[]")
        try {
            val cases = listOf(
                evaluateDrawdown(emptyArray()),
                evaluateDrawdown(arrayOf("--equity-json", emptyEquity.absolutePath)),
                evaluateDrawdown(arrayOf("--equity-json", "/nonexistent/equity.json")),
                evaluateDrawdown(arrayOf("--unknown-flag", "1")),
            )
            for (result in cases) {
                assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
                val parsed = Json.parseToJsonElement(result.output).jsonObject
                assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
            }
        } finally {
            emptyEquity.delete()
        }
    }

    // ----- helpers -----

    private fun evaluate(equity: List<Double>, topN: Int = 5): String {
        val input = File.createTempFile("drawdown-equity-", ".json")
        input.writeText(numbersJson(equity))
        try {
            val result = evaluateDrawdown(
                arrayOf("--equity-json", input.absolutePath, "--top-n", topN.toString())
            )
            assertEquals(0, result.exitCode, result.output)
            return result.output
        } finally {
            input.delete()
        }
    }

    private fun kotlinDrawdown(equity: List<Double>, topN: Int = 5) =
        Json.parseToJsonElement(evaluate(equity, topN)).jsonObject

    private fun kotlinDrawdownFromReturns(returns: List<Double>, topN: Int = 5): kotlinx.serialization.json.JsonObject {
        val input = File.createTempFile("drawdown-returns-", ".json")
        input.writeText(numbersJson(returns))
        try {
            val result = evaluateDrawdown(
                arrayOf("--returns-json", input.absolutePath, "--top-n", topN.toString())
            )
            assertEquals(0, result.exitCode, result.output)
            return Json.parseToJsonElement(result.output).jsonObject
        } finally {
            input.delete()
        }
    }

    private fun pythonDrawdown(flag: String, jsonText: String, topN: Int = 5): kotlinx.serialization.json.JsonObject {
        val input = File.createTempFile("drawdown-py-", ".json")
        input.writeText(jsonText)
        try {
            val process = ProcessBuilder(
                "python3", pythonReference().absolutePath,
                flag, input.absolutePath, "--top-n", topN.toString(),
            ).redirectErrorStream(true).start()
            val output = process.inputStream.bufferedReader().readText()
            check(process.waitFor() == 0) { "python3 drawdown.py failed: $output" }
            return Json.parseToJsonElement(output).jsonObject
        } finally {
            input.delete()
        }
    }

    private fun numbersJson(values: List<Double>): String =
        buildJsonArray { values.forEach { add(JsonPrimitive(it)) } }.toString()

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/drawdown.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
