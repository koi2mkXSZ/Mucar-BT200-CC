package io.github.koi2mkxsz.mucarbt200

import io.github.koi2mkxsz.mucarbt200.kwp.Kwp2000
import io.github.koi2mkxsz.mucarbt200.kwp.KwpFrame
import io.github.koi2mkxsz.mucarbt200.kwp.KwpResponse
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class KwpFrameTest {
    private fun frame(payload: ByteArray): ByteArray {
        val body = byteArrayOf(0x80.toByte(), 0xF1.toByte(), 0x11, payload.size.toByte()) + payload
        return body + Kwp2000.checksum(body)
    }
    @Test fun parsesPositivePhysicalFrame() {
        val parsed = KwpFrame.parsePhysical(frame(byteArrayOf(0x61, 0x01, 0x12, 0x34)))
        assertEquals(0xF1, parsed.target); assertEquals(0x11, parsed.source)
        val response = KwpResponse.fromPayload(parsed.payload)
        assertTrue(response is KwpResponse.Positive)
        response as KwpResponse.Positive
        assertEquals(0x61, response.service); assertEquals(0x01, response.data[0].toInt() and 0xFF)
    }
    @Test fun parsesNegativeResponse() {
        val response = KwpResponse.fromPayload(byteArrayOf(0x7F, 0x21, 0x12))
        assertTrue(response is KwpResponse.Negative)
        response as KwpResponse.Negative
        assertEquals(0x21, response.requestedService); assertEquals(0x12, response.responseCode)
    }
    @Test(expected = IllegalArgumentException::class)
    fun rejectsBadChecksum() {
        KwpFrame.parsePhysical(byteArrayOf(0x80.toByte(),0xF1.toByte(),0x11,0x02,0x61,0x01,0x00))
    }
}
