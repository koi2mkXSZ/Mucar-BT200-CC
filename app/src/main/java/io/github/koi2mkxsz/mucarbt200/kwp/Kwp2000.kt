package io.github.koi2mkxsz.mucarbt200.kwp

object Kwp2000 {
    const val ECU: Int = 0x11
    const val TESTER: Int = 0xF1

    fun checksum(bytes: ByteArray): Byte =
        (bytes.fold(0) { acc, b -> acc + (b.toInt() and 0xFF) } and 0xFF).toByte()

    /** Captured fast-init/start-communication request: 81 11 F1 81 04. */
    fun startCommunication(): ByteArray =
        byteArrayOf(0x81.toByte(), ECU.toByte(), TESTER.toByte(), 0x81.toByte(), 0x04)

    /** Captured physical KWP request wrapper for service 21, local ID 01. */
    fun readData21_01(): ByteArray {
        val body = byteArrayOf(0x80.toByte(), ECU.toByte(), TESTER.toByte(), 0x02, 0x21, 0x01)
        return body + checksum(body)
    }

    fun hasPositive2101(payload: ByteArray): Boolean =
        payload.indices.any { i ->
            i + 1 < payload.size &&
                (payload[i].toInt() and 0xFF) == 0x61 &&
                (payload[i + 1].toInt() and 0xFF) == 0x01
        }
}
