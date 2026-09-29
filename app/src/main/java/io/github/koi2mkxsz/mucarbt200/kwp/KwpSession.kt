package io.github.koi2mkxsz.mucarbt200.kwp

import io.github.koi2mkxsz.mucarbt200.transport.Bt200Transport

class KwpSession(private val transport: Bt200Transport) {
    suspend fun readLocalIdentifier01(): KwpResponse {
        val raw = transport.exchange(Kwp2000.readData21_01())
        val frame = KwpFrame.parsePhysical(raw)
        require(frame.target == Kwp2000.TESTER) { "Unexpected KWP target" }
        require(frame.source == Kwp2000.ECU) { "Unexpected KWP source" }
        return KwpResponse.fromPayload(frame.payload)
    }
}
