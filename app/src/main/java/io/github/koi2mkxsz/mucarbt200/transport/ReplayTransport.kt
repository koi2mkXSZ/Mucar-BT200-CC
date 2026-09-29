package io.github.koi2mkxsz.mucarbt200.transport

class ReplayTransport(private val exchanges: ArrayDeque<Exchange>) : Bt200Transport {
    data class Exchange(val request: ByteArray, val response: ByteArray)
    override var isConnected: Boolean = false
        private set
    override suspend fun connect() { isConnected = true }
    override suspend fun disconnect() { isConnected = false }
    override suspend fun exchange(request: ByteArray, timeoutMs: Long): ByteArray {
        check(isConnected) { "Replay transport is not connected" }
        check(exchanges.isNotEmpty()) { "No captured exchange remains" }
        val nextExchange = exchanges.removeFirst()
        require(request.contentEquals(nextExchange.request)) { "Replay request mismatch" }
        return nextExchange.response.copyOf()
    }
}
