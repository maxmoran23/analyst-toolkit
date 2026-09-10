package org.maxmoran.quant

import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class BoundaryRegressionTest {
    @Test
    fun `Kelly rejects invalid probabilities odds fractions and correlations`() {
        for (p in listOf(-0.1, 1.1, Double.NaN, Double.POSITIVE_INFINITY)) {
            assertThrows(IllegalArgumentException::class.java) { kellySingle(p, 2.0) }
        }
        for (odds in listOf(1.0, 0.0, Double.NaN, Double.POSITIVE_INFINITY)) {
            assertThrows(IllegalArgumentException::class.java) { kellySingle(0.5, odds) }
        }
        val edges = listOf(Edge("a", .6, 2.0), Edge("b", .6, 2.0))
        assertThrows(IllegalArgumentException::class.java) { kellyPortfolio(edges, -0.1) }
        assertThrows(IllegalArgumentException::class.java) { kellyPortfolio(edges, corrMatrix=mapOf("a" to mapOf("b" to 2.0))) }
        assertThrows(IllegalArgumentException::class.java) { kellyPortfolio(edges + edges[0]) }
    }

    @Test
    fun `negative correlations cannot increase capped exposure after rounding`() {
        val edges = listOf("a", "b", "c").map { Edge(it, 1.0, 2.0) }
        val result = kellyPortfolio(edges, 1.0, mapOf("a" to mapOf("b" to -1.0), "b" to mapOf("a" to -1.0)))
        assertTrue(result["total_exposure_pct"]!!.jsonPrimitive.content.toDouble() <= 50.0)
        val total = result["bets"]!!.jsonArray.sumOf { it.jsonObject["fractional_kelly_pct"]!!.jsonPrimitive.content.toDouble() }
        assertTrue(total <= 50.0)
    }

    @Test
    fun `correlation row with no diagonal uses actual peer count`() {
        val edges = listOf("a", "b", "c").map { Edge(it, .6, 2.0) }
        val result = kellyPortfolio(edges, corrMatrix=mapOf("a" to mapOf("b" to .4, "c" to .4)))
        assertEquals(.8, result["bets"]!!.jsonArray[0].jsonObject["correlation_shrink"]!!.jsonPrimitive.content.toDouble())
    }

    @Test
    fun `DCF rejects undefined and nonfinite valuations`() {
        assertThrows(IllegalArgumentException::class.java) { dcfValuation(emptyList(), .1, 0.0, 100.0) }
        assertThrows(IllegalArgumentException::class.java) { dcfValuation(listOf(100.0), .1, .1, 100.0) }
        assertThrows(IllegalArgumentException::class.java) { dcfValuation(listOf(100.0), .1, 0.0, 0.0) }
        assertThrows(IllegalArgumentException::class.java) { dcfValuation(listOf(Double.NaN), .1, 0.0, 100.0) }
        assertThrows(IllegalArgumentException::class.java) { dcfValuation(listOf(1e308), .1, 0.0, 100.0) }
    }

    @Test
    fun `Gaussian confidence is bounded and covariance preserves the input problem`() {
        for (confidence in listOf(0.0, 1.0, Double.NaN)) {
            assertThrows(IllegalArgumentException::class.java) { parametricVar(listOf(-.1, .1), confidence) }
            assertThrows(IllegalArgumentException::class.java) { historicalVar(listOf(-.1, .1), confidence) }
        }
        assertThrows(IllegalArgumentException::class.java) { covMatrix(listOf(listOf(1.0))) }
        assertThrows(IllegalArgumentException::class.java) { covMatrix(listOf(listOf(Double.NaN), listOf(0.0))) }
        assertThrows(IllegalArgumentException::class.java) { cholesky(listOf(listOf(1.0, 1.0), listOf(1.0, 1.0))) }
        assertNull(maxSharpePortfolio(listOf(listOf(1.0)), listOf(-.1)))
    }
}
