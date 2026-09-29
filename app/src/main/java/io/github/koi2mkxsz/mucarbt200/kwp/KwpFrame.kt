package io.github.koi2mkxsz.mucarbt200.kwp

data class KwpFrame(val target: Int, val source: Int, val payload: ByteArray) {
    companion object {
        fun parsePhysical(bytes: ByteArray): KwpFrame {
            require(bytes.size >= 5) { "KWP frame too short" }
            require((bytes[0].toInt() and 0xFF) == 0x80) { "Unsupported KWP format byte" }
            val length = bytes[3].toInt() and 0xFF
            require(bytes.size == 5 + length) { "KWP length mismatch" }
            val expected = Kwp2000.checksum(bytes.copyOf(bytes.size - 1))
            require(bytes.last() == expected) { "KWP checksum mismatch" }
            return KwpFrame(bytes[1].toInt() and 0xFF, bytes[2].toInt() and 0xFF, bytes.copyOfRange(4, 4 + length))
        }
    }
}
