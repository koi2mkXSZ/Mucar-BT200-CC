package io.github.koi2mkxsz.mucarbt200

import io.github.koi2mkxsz.mucarbt200.ecu.DelphiT11Profile
import io.github.koi2mkxsz.mucarbt200.kwp.Kwp2000
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class KwpAndPidTest {
    @Test fun capturedReadRequestMatches() {
        assertArrayEquals(
            byteArrayOf(0x80.toByte(),0x11,0xF1.toByte(),0x02,0x21,0x01,0xA6.toByte()),
            Kwp2000.readData21_01()
        )
    }

    @Test fun odometerKnownVectorIs100000Km() {
        assertEquals(100000.0, DelphiT11Profile.odometerKm(0x00,0x0F,0x42,0x40), 0.0001)
    }

    @Test fun positiveResponseDetection() {
        assertTrue(Kwp2000.hasPositive2101(byteArrayOf(0x61,0x01,0x00)))
    }
}
