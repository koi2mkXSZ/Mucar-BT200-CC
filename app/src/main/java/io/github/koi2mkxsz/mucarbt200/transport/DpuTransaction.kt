package io.github.koi2mkxsz.mucarbt200.transport

/**
 * Evidence-based representation of the decoded Launch/MUCAR DPU transactions.
 *
 * Captures show:
 *   request  = sequence, 0x27, 0x01, command...
 *   response = sequence, 0x67, 0x01, status/data...
 *
 * This class intentionally does not implement the still-unknown outer Bluetooth
 * packet framing/checksum.
 */
data class DpuTransaction(
    val sequence: Int,
    val body: ByteArray
) {
    init { require(sequence in 0..255) }

    fun decodedRequest(): ByteArray =
        byteArrayOf(sequence.toByte(), 0x27, 0x01) + body

    companion object {
        fun parseDecodedResponse(bytes: ByteArray, expectedSequence: Int): ByteArray {
            require(bytes.size >= 4) { "DPU response too short" }
            require((bytes[0].toInt() and 0xFF) == expectedSequence) { "DPU sequence mismatch" }
            require((bytes[1].toInt() and 0xFF) == 0x67) { "Unexpected DPU response marker" }
            require((bytes[2].toInt() and 0xFF) == 0x01) { "Unexpected DPU protocol marker" }
            return bytes.copyOfRange(3, bytes.size)
        }
    }
}
