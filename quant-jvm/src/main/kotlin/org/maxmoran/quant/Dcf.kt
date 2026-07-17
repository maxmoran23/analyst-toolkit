package org.maxmoran.quant

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlin.math.max
import kotlin.math.pow
import kotlin.system.exitProcess

private val PRETTY_JSON = Json { prettyPrint = true }

/**
 * Deterministic port of `quant/dcf.py` — token fee-capture DCF with scenario range and
 * discount-rate sensitivity. Plain §1.1 arithmetic (no solver, no RNG).
 *
 * Serialization note: dollar-scale magnitudes (>= 1e7) print in scientific notation on the
 * JVM where Python prints plain decimals. The numbers are identical; JSON text form is
 * non-contract per parity-contract.md §2.
 */

/** Unrounded valuation state; [degenerateTerminal] marks discount <= terminal growth. */
data class DcfResult(
    val pvFees: Double,
    val pvTerminal: Double,
    val degenerateTerminal: Boolean,
    val enterpriseValue: Double,
    val fairValuePerToken: Double,
)

/** Present value of explicit fees plus growing-perpetuity terminal, mirroring `dcf`. */
fun dcfValuation(
    feesYearly: List<Double>,
    discount: Double,
    terminalGrowth: Double,
    circulatingSupply: Double,
    captureRatio: Double = 1.0,
): DcfResult {
    val years = feesYearly.size
    var pvFees = 0.0
    for (t in 1..years) {
        pvFees += (feesYearly[t - 1] * captureRatio) / (1.0 + discount).pow(t)
    }
    val terminalFee = feesYearly.last() * (1.0 + terminalGrowth) * captureRatio
    val degenerate = !(discount > terminalGrowth)
    val pvTerminal = if (degenerate) {
        0.0
    } else {
        val tv = terminalFee / (discount - terminalGrowth)
        tv / (1.0 + discount).pow(years)
    }
    val enterpriseValue = pvFees + pvTerminal
    return DcfResult(
        pvFees = pvFees,
        pvTerminal = pvTerminal,
        degenerateTerminal = degenerate,
        enterpriseValue = enterpriseValue,
        fairValuePerToken = enterpriseValue / circulatingSupply,
    )
}

/**
 * Rounded JSON block for one valuation, field-for-field with the Python `dcf` dict.
 * In the degenerate branch Python's `round(0, 2)` keeps the int, hence the bare 0 here;
 * same for the `else 0` arm of the terminal weight.
 */
fun dcfJson(result: DcfResult): JsonObject = buildJsonObject {
    put("pv_of_explicit_fees", JsonPrimitive(round2(result.pvFees)))
    put(
        "pv_of_terminal",
        if (result.degenerateTerminal) JsonPrimitive(0) else JsonPrimitive(round2(result.pvTerminal)),
    )
    put("enterprise_value", JsonPrimitive(round2(result.enterpriseValue)))
    put("fair_value_per_token", JsonPrimitive(round4(result.fairValuePerToken)))
    put(
        "terminal_weight_pct",
        if (result.enterpriseValue > 0.0) {
            JsonPrimitive(round2(result.pvTerminal / result.enterpriseValue * 100.0))
        } else {
            JsonPrimitive(0)
        },
    )
}

private val SENSITIVITY_DISCOUNTS = listOf(0.10, 0.12, 0.15, 0.18, 0.20, 0.25)

/** Testable result of evaluating the DCF CLI contract. */
data class DcfCliResult(val exitCode: Int, val output: String)

/** Parse input and produce CLI output without terminating the process. */
fun evaluateDcf(args: Array<String>): DcfCliResult {
    return try {
        var feesJson: String? = null
        var discount = 0.15
        var terminalGrowth = 0.03
        var circulatingSupply: Double? = null
        var captureRatio = 1.0
        var currentPrice: Double? = null
        var index = 0

        fun optionValue(option: String): String {
            if (index + 1 >= args.size || args[index + 1].startsWith("--")) {
                throw IllegalArgumentException("$option requires a value")
            }
            index += 1
            return args[index]
        }

        while (index < args.size) {
            when (val arg = args[index]) {
                "--fees-yearly" -> feesJson = optionValue(arg)
                "--discount" -> discount = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--discount must be a number")
                "--terminal-growth" -> terminalGrowth = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--terminal-growth must be a number")
                "--circulating-supply" -> circulatingSupply = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--circulating-supply must be a number")
                "--capture-ratio" -> captureRatio = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--capture-ratio must be a number")
                "--current-price" -> currentPrice = optionValue(arg).toDoubleOrNull()
                    ?: throw IllegalArgumentException("--current-price must be a number")
                else -> throw IllegalArgumentException("unknown argument: $arg")
            }
            index += 1
        }

        // --fees-yearly is inline JSON on the command line, not a file path.
        val fees = parseNumberArray(
            feesJson ?: throw IllegalArgumentException("need --fees-yearly"),
            "fees",
        )
        val supply = circulatingSupply ?: throw IllegalArgumentException("need --circulating-supply")

        val base = dcfValuation(fees, discount, terminalGrowth, supply, captureRatio)
        val bear = dcfValuation(
            fees.map { it * 0.6 },
            discount + 0.05,
            max(0.01, terminalGrowth - 0.02),
            supply,
            captureRatio,
        )
        val bull = dcfValuation(
            fees.map { it * 1.4 },
            max(0.05, discount - 0.03),
            terminalGrowth + 0.02,
            supply,
            captureRatio,
        )

        val output = buildJsonObject {
            put("inputs", buildJsonObject {
                put("years", JsonPrimitive(fees.size))
                put("discount", JsonPrimitive(discount))
                put("terminal_growth", JsonPrimitive(terminalGrowth))
                put("circulating_supply", JsonPrimitive(supply))
                put("capture_ratio", JsonPrimitive(captureRatio))
            })
            put("base_case", dcfJson(base))
            put("bear_case", dcfJson(bear))
            put("bull_case", dcfJson(bull))
            put("sensitivity_per_token", buildJsonObject {
                for (d in SENSITIVITY_DISCOUNTS) {
                    // Key mirrors Python's f"discount_{d}" repr (0.20 prints as 0.2).
                    put(
                        "discount_$d",
                        JsonPrimitive(round4(round4(
                            dcfValuation(fees, d, terminalGrowth, supply, captureRatio).fairValuePerToken
                        ))),
                    )
                }
            })
            // Python gates on truthiness, so an explicit 0 price suppresses the block.
            if (currentPrice != null && currentPrice != 0.0) {
                val price = currentPrice
                put("current_price", JsonPrimitive(price))
                // Upside uses the already-rounded fair values, exactly like the reference.
                put("upside_base_pct", upsidePct(round4(base.fairValuePerToken), price))
                put("upside_bull_pct", upsidePct(round4(bull.fairValuePerToken), price))
                put("downside_bear_pct", upsidePct(round4(bear.fairValuePerToken), price))
            }
        }
        DcfCliResult(
            exitCode = 0,
            output = PRETTY_JSON.encodeToString(JsonObject.serializer(), output),
        )
    } catch (exception: Exception) {
        val message = exception.message?.lineSequence()?.firstOrNull()?.take(240) ?: "invalid input"
        DcfCliResult(
            exitCode = 1,
            output = buildJsonObject { put("error", JsonPrimitive(message)) }.toString(),
        )
    }
}

private fun upsidePct(roundedFairValue: Double, price: Double): JsonPrimitive =
    JsonPrimitive(round2((roundedFairValue / price - 1.0) * 100.0))

/** Module CLI runner — JSON in / JSON out, matching the Python entrypoint. */
fun runDcf(args: Array<String>) {
    val result = evaluateDcf(args)
    println(result.output)
    if (result.exitCode != 0) exitProcess(result.exitCode)
}
