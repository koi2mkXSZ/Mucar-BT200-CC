package io.github.koi2mkxsz.mucarbt200.kwp

sealed interface KwpResponse {
    data class Positive(val service: Int, val data: ByteArray) : KwpResponse
    data class Negative(val requestedService: Int, val responseCode: Int) : KwpResponse
    companion object {
        fun fromPayload(payload: ByteArray): KwpResponse {
            require(payload.isNotEmpty()) { "Empty KWP payload" }
            val sid = payload[0].toInt() and 0xFF
            if (sid == 0x7F) {
                require(payload.size >= 3) { "Malformed negative response" }
                return Negative(payload[1].toInt() and 0xFF, payload[2].toInt() and 0xFF)
            }
            return Positive(sid, payload.copyOfRange(1, payload.size))
        }
    }
}
