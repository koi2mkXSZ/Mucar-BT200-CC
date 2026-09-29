package io.github.koi2mkxsz.mucarbt200

import io.github.koi2mkxsz.mucarbt200.transport.DpuTransaction
import org.junit.Assert.assertArrayEquals
import org.junit.Test

class DpuTransactionTest {
    @Test fun buildsObservedAdapterRequestPrefix() {
        val tx = DpuTransaction(0x02, byteArrayOf(0x60, 0x21))
        assertArrayEquals(byteArrayOf(0x02,0x27,0x01,0x60,0x21), tx.decodedRequest())
    }

    @Test fun parsesObservedAdapterResponsePrefix() {
        assertArrayEquals(
            byteArrayOf(0x00,0x07),
            DpuTransaction.parseDecodedResponse(
                byteArrayOf(0x02,0x67,0x01,0x00,0x07),
                0x02
            )
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsWrongSequence() {
        DpuTransaction.parseDecodedResponse(byteArrayOf(0x03,0x67,0x01,0x00),0x02)
    }
}
