package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test
import java.io.File
import kotlin.math.abs
import kotlin.math.max

/**
 * Executable parity contract for the unchanged `../quant/dcf.py` reference.
 *
 * Rounded JSON fields are compared as exact numeric values (not text): dollar magnitudes
 * >= 1e7 serialize in scientific notation on the JVM and plain decimal in Python — same
 * numbers, non-contract text form per parity-contract.md §2. Raw-double oracles use a
 * relative 1e-10 tolerance because absolute 1e-10 is below one ulp at 1e8 dollar scale.
 */
class DcfParityTest {

    @Test
    fun `full JSON parity — base, scenarios, sensitivity, and current-price upside block`() {
        requirePython()
        val args = arrayOf(
            "--fees-yearly", "[120e6,150e6,180e6,200e6,210e6]",
            "--discount", "0.15", "--terminal-growth", "0.04",
            "--circulating-supply", "1e9", "--capture-ratio", "0.8",
            "--current-price", "0.5",
        )
        assertJsonValueEquals(pythonDcf(*args), kotlinDcf(*args), "$")
    }

    @Test
    fun `full JSON parity — degenerate terminal emits Python's integer zero`() {
        requirePython()
        // terminal growth above the discount rate zeroes the terminal in base and bull.
        val args = arrayOf(
            "--fees-yearly", "[50e6,60e6]",
            "--discount", "0.15", "--terminal-growth", "0.2",
            "--circulating-supply", "5e8",
        )
        val python = pythonDcf(*args)
        val kotlin = kotlinDcf(*args)
        assertJsonValueEquals(python, kotlin, "$")

        for (case in listOf("base_case", "bull_case")) {
            val pv = kotlin.jsonObject[case]!!.jsonObject["pv_of_terminal"]!!.jsonPrimitive
            assertEquals("0", pv.content, "$case pv_of_terminal must be the bare int 0")
        }
        // Bear raises discount to 0.20 and floors terminal growth at 0.18 < 0.20: not degenerate.
        assertTrue(
            kotlin.jsonObject["bear_case"]!!.jsonObject["pv_of_terminal"]!!
                .jsonPrimitive.content.toDouble() > 0.0
        )
    }

    @Test
    fun `raw valuation math agrees with a Python oracle at relative 1e-10`() {
        requirePython()
        val fees = listOf(120e6, 150e6, 180e6, 200e6, 210e6)
        // Reconstructs dcf.py's arithmetic in the same operation order to expose the
        // unrounded intermediates its public dict hides behind round().
        val script = """
            import json, sys
            data = json.loads(sys.stdin.read())
            fees, discount, tg, supply, capture = (
                data["fees"], data["discount"], data["tg"], data["supply"], data["capture"])
            pv_fees = 0.0
            for t, fee in enumerate(fees, start=1):
                pv_fees += (fee * capture) / ((1 + discount) ** t)
            terminal_fee = fees[-1] * (1 + tg) * capture
            if discount > tg:
                tv = terminal_fee / (discount - tg)
                pv_tv = tv / ((1 + discount) ** len(fees))
            else:
                pv_tv = 0
            ev = pv_fees + pv_tv
            print(json.dumps({
                "pv_fees": pv_fees, "pv_tv": pv_tv, "ev": ev, "fair": ev / supply,
            }))
        """.trimIndent()
        val process = ProcessBuilder("python3", "-c", script).redirectErrorStream(true).start()
        process.outputStream.bufferedWriter().use {
            it.write(
                """{"fees": [${fees.joinToString(",")}], "discount": 0.15,""" +
                    """ "tg": 0.04, "supply": 1e9, "capture": 0.8}"""
            )
        }
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "Python raw oracle failed: $output" }
        val python = Json.parseToJsonElement(output).jsonObject

        val result = dcfValuation(fees, 0.15, 0.04, 1e9, 0.8)
        assertRelativeClose(python, "pv_fees", result.pvFees)
        assertRelativeClose(python, "pv_tv", result.pvTerminal)
        assertRelativeClose(python, "ev", result.enterpriseValue)
        assertRelativeClose(python, "fair", result.fairValuePerToken)
    }

    @Test
    fun `hand check — one-year growing perpetuity closes to a round enterprise value`() {
        // fees [100], d = 0.10, g = 0: pv_fees = 100/1.1, tv = 1000, pv_tv = 1000/1.1,
        // enterprise = 1100/1.1 = 1000 exactly, fair value = 10 on 100 tokens.
        val result = dcfValuation(listOf(100.0), 0.10, 0.0, 100.0)
        val json = dcfJson(result)
        assertEquals("90.91", json["pv_of_explicit_fees"]?.jsonPrimitive?.content)
        assertEquals("909.09", json["pv_of_terminal"]?.jsonPrimitive?.content)
        assertEquals("1000.0", json["enterprise_value"]?.jsonPrimitive?.content)
        assertEquals("10.0", json["fair_value_per_token"]?.jsonPrimitive?.content)
        assertEquals("90.91", json["terminal_weight_pct"]?.jsonPrimitive?.content)

        // Degenerate branch: bare int 0 terminal, weight still a float.
        val degenerate = dcfJson(dcfValuation(listOf(100.0), 0.05, 0.05, 100.0))
        assertEquals("0", degenerate["pv_of_terminal"]?.jsonPrimitive?.content)
        assertEquals("0.0", degenerate["terminal_weight_pct"]?.jsonPrimitive?.content)
    }

    @Test
    fun `sensitivity keys mirror Python float repr and scenario shifts are clamped`() {
        requirePython()
        val args = arrayOf(
            "--fees-yearly", "[10e6,12e6]", "--discount", "0.06",
            "--terminal-growth", "0.02", "--circulating-supply", "1e8",
        )
        val kotlin = kotlinDcf(*args)
        val keys = kotlin.jsonObject["sensitivity_per_token"]!!.jsonObject.keys
        assertEquals(
            setOf("discount_0.1", "discount_0.12", "discount_0.15", "discount_0.18",
                "discount_0.2", "discount_0.25"),
            keys,
        )
        // Bull clamps discount at max(0.05, 0.06 - 0.03) = 0.05; bear floors growth at 0.01.
        // Full-object parity is the authoritative check for those shifted inputs.
        assertJsonValueEquals(pythonDcf(*args), kotlin, "$")
    }

    @Test
    fun `zero current price is falsy and suppresses the upside block, like Python`() {
        val base = arrayOf(
            "--fees-yearly", "[10e6,12e6]", "--circulating-supply", "1e8",
        )
        val withZero = evaluateDcf(base + arrayOf("--current-price", "0"))
        assertEquals(0, withZero.exitCode, withZero.output)
        val output = Json.parseToJsonElement(withZero.output).jsonObject
        assertTrue("current_price" !in output.keys)
        assertTrue("upside_base_pct" !in output.keys)

        val withPrice = evaluateDcf(base + arrayOf("--current-price", "0.25"))
        val priced = Json.parseToJsonElement(withPrice.output).jsonObject
        assertTrue("upside_base_pct" in priced.keys && "downside_bear_pct" in priced.keys)
    }

    @Test
    fun `CLI evaluator emits JSON errors and nonzero status for invalid input`() {
        val cases = listOf(
            evaluateDcf(emptyArray()),
            evaluateDcf(arrayOf("--fees-yearly", "[1e6,2e6]")),
            evaluateDcf(arrayOf("--fees-yearly", "[]", "--circulating-supply", "1e8")),
            evaluateDcf(arrayOf("--fees-yearly", "{\"y1\": 1e6}", "--circulating-supply", "1e8")),
            evaluateDcf(arrayOf("--fees-yearly", "[1e6]", "--circulating-supply", "abc")),
        )
        for (result in cases) {
            assertTrue(result.exitCode != 0, "invalid input unexpectedly succeeded: ${result.output}")
            val parsed = Json.parseToJsonElement(result.output).jsonObject
            assertTrue(parsed["error"]?.jsonPrimitive?.content?.isNotBlank() == true)
        }
    }

    // ----- helpers -----

    private fun kotlinDcf(vararg args: String): JsonObject {
        val result = evaluateDcf(arrayOf(*args))
        assertEquals(0, result.exitCode, result.output)
        return Json.parseToJsonElement(result.output).jsonObject
    }

    private fun pythonDcf(vararg args: String): JsonObject {
        val process = ProcessBuilder("python3", pythonReference().absolutePath, *args)
            .redirectErrorStream(true).start()
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor() == 0) { "python3 dcf.py failed: $output" }
        return Json.parseToJsonElement(output).jsonObject
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

    private fun assertRelativeClose(python: JsonObject, key: String, kotlinValue: Double) {
        val pythonValue = python[key]?.jsonPrimitive?.content?.toDouble()
            ?: error("Python oracle omitted '$key': $python")
        val difference = abs(pythonValue - kotlinValue)
        val bound = 1e-10 * max(1.0, abs(pythonValue))
        assertTrue(
            difference < bound,
            "$key parity failure: python=$pythonValue kotlin=$kotlinValue difference=$difference",
        )
    }

    private fun requirePython() {
        assumeTrue(pythonAvailable(), "python3 unavailable; cross-language parity test skipped")
        assertTrue(pythonReference().isFile, "Python reference missing: ${pythonReference()}")
    }

    private fun pythonReference(): File =
        File(System.getProperty("user.dir"), "../quant/dcf.py").canonicalFile

    private fun pythonAvailable(): Boolean = try {
        val process = ProcessBuilder("python3", "--version").redirectErrorStream(true).start()
        process.inputStream.bufferedReader().readText()
        process.waitFor() == 0
    } catch (_: Exception) {
        false
    }
}
