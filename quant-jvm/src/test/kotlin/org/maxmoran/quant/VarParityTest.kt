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

/** Executable parity contract for the unchanged `../quant/var.py` reference. */
class VarParityTest {

    @Test
    fun `both-methods public JSON contract exactly matches Python at 95pct`() {
        requirePython()
        val returns = mixedReturns()
        withReturnsFile(returns) { path ->
            assertEquals(
                pythonVar("--returns-json", path),
                kotlinVar(arrayOf("--returns-json", path)),
            )
        }
    }

    @Test
    fun `single methods, dollar scaling, and off-table confidence match Python`() {
        requirePython()
        val returns = mixedReturns()
        withReturnsFile(returns) { path ->
            assertEquals(
                pythonVar("--returns-json", path, "--method", "historical", "--confidence", "0.99"),
                kotlinVar(arrayOf("--returns-json", path, "--method", "historical", "--confidence", "0.99")),
            )
            assertEquals(
                pythonVar(
                    "--returns-json", path, "--method", "parametric",
                    "--confidence", "0.975", "--portfolio-value", "100000",
                ),
                kotlinVar(arrayOf(
                    "--returns-json", path, "--method", "parametric",
                    "--confidence", "0.975", "--portfolio-value", "100000",
                )),
            )
            // 0.97 is not in the z-table: both sides must take the 1.645 fallback.
            assertEquals(
                pythonVar("--returns-json", path, "--confidence", "0.97"),
                kotlinVar(arrayOf("--returns-json", path, "--confidence", "0.97")),
            )
        }
    }

    @Test
    fun `stdin input path matches Python stdin invocation`() {
        requirePython()
        val returns = mixedReturns()
        val process = ProcessBuilder(
            "python3", pythonReference().absolutePath, "--stdin", "--confidence", "0.95",
        ).redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { it.write(returnsJson(returns)) }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "python3 var.py --stdin failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        val kotlin = evaluateVar(arrayOf("--stdin", "--confidence", "0.95"), returnsJson(returns))
        assertEquals(0, kotlin.exitCode, kotlin.output)
        assertEquals(python, Json.parseToJsonElement(kotlin.output).jsonObject)
    }

    @Test
    fun `raw VaR math agrees with imported Python helpers to 1e-10`() {
        requirePython()
        val returns = mixedReturns()
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("var_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            returns = json.loads(sys.stdin.read())
            hv, hc = module.historical_var(returns, 0.95)
            pv, pc = module.parametric_var(returns, 0.95)
            pv99, pc99 = module.parametric_var(returns, 0.99)
            print(json.dumps({
                "hist_var": hv, "hist_cvar": hc,
                "param_var": pv, "param_cvar": pc,
                "param_var_99": pv99, "param_cvar_99": pc99,
            }))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { it.write(returnsJson(returns)) }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        val (hv, hc) = historicalVar(returns, 0.95)
        val (pv, pc) = parametricVar(returns, 0.95)
        val (pv99, pc99) = parametricVar(returns, 0.99)
        assertClose(python, "hist_var", hv)
        assertClose(python, "hist_cvar", hc)
        assertClose(python, "param_var", pv)
        assertClose(python, "param_cvar", pc)
        assertClose(python, "param_var_99", pv99)
        assertClose(python, "param_cvar_99", pc99)
    }

    @Test
    fun `historical hand check — quantile index and tail average`() {
        // 20 returns, confidence 0.95: idx = floor(0.05 * 20) = 1, so VaR is the
        // second-worst return and CVaR averages the two worst.
        val returns = listOf(-0.10, -0.05) + List(18) { 0.01 * (it % 3 + 1) }
        val (varValue, cvar) = historicalVar(returns, 0.95)
        assertEquals(0.05, varValue, 1e-15)
        assertEquals(0.075, cvar, 1e-15)

        // Confidence 0.99: idx = floor(0.2) = 0 — worst return only, CVaR equals VaR.
        val (worst, worstCvar) = historicalVar(returns, 0.99)
        assertEquals(0.10, worst, 1e-15)
        assertEquals(0.10, worstCvar, 1e-15)
    }

    @Test
    fun `parametric hand check — z-table lookup and round3 key quirk`() {
        // Alternating +-1% has zero mean, so VaR = z * sigma with sigma = sqrt(20e-4 / 19).
        val returns = List(20) { if (it % 2 == 0) 0.01 else -0.01 }
        val sigma = sqrt(20.0 * 1e-4 / 19.0)
        val (varValue, _) = parametricVar(returns, 0.95)
        assertEquals(1.645 * sigma, varValue, 1e-15)

        // round(0.9501, 3) = 0.95 hits the table; the same z makes the same VaR.
        val (quirkVar, _) = parametricVar(returns, 0.9501)
        assertEquals(varValue, quirkVar, 0.0)

        // Off-table confidence falls back to z = 1.645, matching the Python default.
        val (fallbackVar, _) = parametricVar(returns, 0.97)
        assertEquals(1.645 * sigma, fallbackVar, 1e-15)
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val cases = listOf(
            evaluateVar(emptyArray()),
            evaluateVar(arrayOf("--stdin"), returnsJson(List(19) { 0.01 })),
            evaluateVar(arrayOf("--stdin"), "{\"not\": \"an array\"}"),
            evaluateVar(arrayOf("--stdin"), "[\"0.1\"]"),
            evaluateVar(arrayOf("--stdin", "--method", "montecarlo"), returnsJson(mixedReturns())),
            // Python raises ZeroDivisionError for parametric CVaR at confidence 1.0.
            evaluateVar(arrayOf("--stdin", "--confidence", "1.0"), returnsJson(mixedReturns())),
        )
        for (result in cases) {
            assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
            val parsed = Json.parseToJsonElement(result.output).jsonObject
            assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
        }
    }

    // ----- helpers -----

    private fun mixedReturns(): List<Double> {
        val pattern = listOf(0.013, -0.026, 0.007, -0.041, 0.019, 0.002, -0.008, 0.011)
        return List(60) { index -> pattern[index % pattern.size] + (index % 9) * 0.0003 }
    }

    private fun returnsJson(returns: List<Double>): String =
        buildJsonArray { returns.forEach { add(JsonPrimitive(it)) } }.toString()

    private fun withReturnsFile(returns: List<Double>, block: (String) -> Unit) {
        val input = File.createTempFile("var-returns-", ".json")
        input.writeText(returnsJson(returns))
        try {
            block(input.absolutePath)
        } finally {
            input.delete()
        }
    }

    private fun kotlinVar(args: Array<String>): JsonObject {
        val result = evaluateVar(args)
        assertEquals(0, result.exitCode, result.output)
        return Json.parseToJsonElement(result.output).jsonObject
    }

    private fun pythonVar(vararg args: String): JsonObject {
        val process = ProcessBuilder("python3", pythonReference().absolutePath, *args)
            .redirectErrorStream(true).start()
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "python3 var.py failed: $output" }
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
        File(System.getProperty("user.dir"), "../quant/var.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
