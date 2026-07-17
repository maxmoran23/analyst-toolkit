package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * Executable parity contract for the unchanged `../quant/markowitz.py` reference.
 *
 * The solver is hand-rolled Cholesky + substitution replicated operation-for-operation, so
 * raw parity is asserted at the parity-contract.md §1.4 linear-algebra tolerance (1e-6).
 * Rounded JSON fields are compared as exact numeric values (not text) because large or tiny
 * magnitudes serialize differently across languages — non-contract per §2.
 */
class MarkowitzParityTest {

    @Test
    fun `full JSON parity — named assets with max-Sharpe present`() {
        requirePython()
        val csv = returnsCsv()
        val args = arrayOf("--asset-names", "btc,eth,gold", "--rf", "0.04", "--annualize", "365")
        assertJsonValueEquals(pythonMarkowitz(csv, *args), kotlinMarkowitz(csv, *args), "$")
    }

    @Test
    fun `full JSON parity — surplus name quirk (zip truncation vs equal-weight all names)`() {
        requirePython()
        // Four names for three assets: solver weight dicts truncate via zip, but the
        // equal-weight benchmark iterates every provided name.
        val csv = returnsCsv()
        val args = arrayOf("--asset-names", "a,b,c,ghost")
        val python = pythonMarkowitz(csv, *args)
        val kotlin = kotlinMarkowitz(csv, *args)
        assertJsonValueEquals(python, kotlin, "$")

        val minVarWeights = kotlin.jsonObject["min_variance_portfolio"]!!.jsonObject["weights"]!!.jsonObject
        val equalWeights = kotlin.jsonObject["equal_weight_benchmark"]!!.jsonObject["weights"]!!.jsonObject
        assertEquals(3, minVarWeights.size)
        assertEquals(4, equalWeights.size)
        assertTrue(equalWeights.containsKey("ghost"))
    }

    @Test
    fun `raw solver weights agree with imported Python helpers at the 1e-6 contract tolerance`() {
        requirePython()
        val returns = returnsMatrix()
        val script = """
            import importlib.util, json, sys
            spec = importlib.util.spec_from_file_location("markowitz_reference", sys.argv[1])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            returns = json.loads(sys.stdin.read())
            cov, mu = module.cov_matrix(returns)
            rf = 0.04 / 365
            excess = [m - rf for m in mu]
            print(json.dumps({
                "min_variance": module.min_variance_portfolio(cov),
                "max_sharpe": module.max_sharpe_portfolio(cov, excess),
                "cov_diag": [cov[i][i] for i in range(len(cov))],
            }))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script, pythonReference().absolutePath)
            .redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use { writer ->
            writer.write(returns.joinToString(",", "[", "]") { row -> row.joinToString(",", "[", "]") })
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        val (cov, mu) = covMatrix(returns)
        val periodicRf = 0.04 / 365
        val excess = mu.map { it - periodicRf }
        assertVectorClose(python["min_variance"]!!, minVariancePortfolio(cov), "min_variance")
        assertVectorClose(python["max_sharpe"]!!, maxSharpePortfolio(cov, excess)!!, "max_sharpe")
        assertVectorClose(python["cov_diag"]!!, cov.indices.map { cov[it][it] }, "cov_diag")
    }

    @Test
    fun `solver primitives pass unconditional hand checks`() {
        // Cholesky of [[4,2],[2,3]] is [[2,0],[1,sqrt(2)]].
        val l = cholesky(listOf(listOf(4.0, 2.0), listOf(2.0, 3.0)))
        assertEquals(2.0, l[0][0], 1e-15)
        assertEquals(0.0, l[0][1], 0.0)
        assertEquals(1.0, l[1][0], 1e-15)
        assertEquals(sqrt(2.0), l[1][1], 1e-15)

        // solveLinear recovers x for a known right-hand side: A * [1, 2] = [8, 8].
        val x = solveLinear(listOf(listOf(4.0, 2.0), listOf(2.0, 3.0)), listOf(8.0, 8.0))
        assertEquals(1.0, x[0], 1e-12)
        assertEquals(2.0, x[1], 1e-12)

        // Diagonal covariance: min-variance weights are inverse-variance normalized.
        val weights = minVariancePortfolio(listOf(listOf(0.04, 0.0), listOf(0.0, 0.01)))
        assertEquals(0.2, weights[0], 1e-12)
        assertEquals(0.8, weights[1], 1e-12)
    }

    @Test
    fun `degenerate tangency and pivot regularization hand checks`() {
        // Symmetric excess over an identity covariance sums to zero: tangency is undefined.
        assertNull(maxSharpePortfolio(listOf(listOf(1.0, 0.0), listOf(0.0, 1.0)), listOf(0.01, -0.01)))

        // Non-positive pivot regularizes to 1e-10, matching the Python guard.
        assertEquals(sqrt(1e-10), cholesky(listOf(listOf(0.0)))[0][0], 0.0)
        assertEquals(sqrt(1e-10), cholesky(listOf(listOf(-3.0)))[0][0], 0.0)
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val headerOnly = File.createTempFile("mkw-header-", ".csv")
        headerOnly.writeText("a,b,c\n")
        val ragged = File.createTempFile("mkw-ragged-", ".csv")
        ragged.writeText("0.01,0.02\n0.03\n")
        try {
            val cases = listOf(
                evaluateMarkowitz(emptyArray()),
                evaluateMarkowitz(arrayOf("--returns-csv", "/nonexistent/returns.csv")),
                evaluateMarkowitz(arrayOf("--returns-csv", headerOnly.absolutePath)),
                evaluateMarkowitz(arrayOf("--returns-csv", ragged.absolutePath)),
                evaluateMarkowitz(arrayOf("--rf", "not-a-number")),
            )
            for (result in cases) {
                assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
                val parsed = Json.parseToJsonElement(result.output).jsonObject
                assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
            }
            val emptyResult = evaluateMarkowitz(arrayOf("--returns-csv", headerOnly.absolutePath))
            assertEquals(
                "no numeric data found",
                Json.parseToJsonElement(emptyResult.output).jsonObject["error"]?.jsonPrimitive?.content,
            )
        } finally {
            headerOnly.delete()
            ragged.delete()
        }
    }

    // ----- helpers -----

    private fun returnsMatrix(): List<List<Double>> = List(40) { index ->
        val a = 0.01 * ((index % 5) - 2) + 0.0006
        val b = 0.006 * ((index % 4) - 1) - 0.0003 + a * 0.3
        val c = 0.004 * ((index % 7) - 3) + 0.0009 - a * 0.2
        listOf(a, b, c)
    }

    private fun returnsCsv(): String =
        "asset_1,asset_2,asset_3\n" + returnsMatrix().joinToString("\n") { it.joinToString(",") }

    private fun kotlinMarkowitz(csv: String, vararg args: String): JsonObject {
        val input = File.createTempFile("mkw-kt-", ".csv")
        input.writeText(csv)
        try {
            val result = evaluateMarkowitz(arrayOf("--returns-csv", input.absolutePath, *args))
            assertEquals(0, result.exitCode, result.output)
            return Json.parseToJsonElement(result.output).jsonObject
        } finally {
            input.delete()
        }
    }

    private fun pythonMarkowitz(csv: String, vararg args: String): JsonObject {
        val input = File.createTempFile("mkw-py-", ".csv")
        input.writeText(csv)
        try {
            val process = ProcessBuilder(
                "python3", pythonReference().absolutePath,
                "--returns-csv", input.absolutePath, *args,
            ).redirectErrorStream(true).start()
            val output = process.inputStream.bufferedReader().readText()
            check(process.waitFor() == 0) { "python3 markowitz.py failed: $output" }
            return Json.parseToJsonElement(output).jsonObject
        } finally {
            input.delete()
        }
    }

    /** Structural + numeric-value equality; text form of numbers is non-contract (§2). */
    private fun assertJsonValueEquals(python: JsonElement, kotlin: JsonElement, path: String) {
        when {
            python is JsonObject && kotlin is JsonObject -> {
                assertEquals(python.keys, kotlin.keys, "key set differs at $path")
                for (key in python.keys) {
                    assertJsonValueEquals(python[key]!!, kotlin[key]!!, "$path.$key")
                }
            }
            python is JsonArray && kotlin is JsonArray -> {
                assertEquals(python.size, kotlin.size, "array size differs at $path")
                for (i in python.indices) assertJsonValueEquals(python[i], kotlin[i], "$path[$i]")
            }
            python is JsonPrimitive && kotlin is JsonPrimitive -> {
                val pd = if (python.isString) null else python.content.toDoubleOrNull()
                val kd = if (kotlin.isString) null else kotlin.content.toDoubleOrNull()
                if (pd != null && kd != null) {
                    assertEquals(pd, kd, 0.0, "numeric value differs at $path")
                } else {
                    assertEquals(python, kotlin, "primitive differs at $path")
                }
            }
            else -> assertEquals(python, kotlin, "element kind differs at $path")
        }
    }

    private fun assertVectorClose(python: JsonElement, kotlin: List<Double>, label: String) {
        val values = (python as JsonArray).map { it.jsonPrimitive.content.toDouble() }
        assertEquals(values.size, kotlin.size, "$label length")
        for (i in values.indices) {
            val difference = abs(values[i] - kotlin[i])
            assertTrue(
                difference < 1e-6,
                "$label[$i] parity failure: python=${values[i]} kotlin=${kotlin[i]} difference=$difference",
            )
        }
    }

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/markowitz.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
