package io.github.koi2mkxsz.mucarbt200.transport

/**
 * Transport boundary between Android Bluetooth and diagnostic protocol layers.
 * Stage 1 deliberately exposes raw bytes so captured BT200 framing can be
 * implemented without coupling it to ECU/PID logic.
 */
interface Bt200Transport {
    val isConnected: Boolean
    suspend fun connect()
    suspend fun disconnect()
    suspend fun exchange(request: ByteArray, timeoutMs: Long = 1500): ByteArray
}
