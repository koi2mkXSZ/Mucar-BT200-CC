package io.github.koi2mkxsz.mucarbt200.ecu

object DelphiT11Profile {
    const val name = "Chery Tiggo T11 Delphi 2.0/2.4 (4G63/4G64)"

    /**
     * Odometer formula recovered independently from the diagnostic datasets:
     * unsigned big-endian 32-bit raw value * 0.1 km.
     */
    fun odometerKm(b0: Int, b1: Int, b2: Int, b3: Int): Double {
        val raw = ((b0.toLong() and 0xFF) shl 24) or
            ((b1.toLong() and 0xFF) shl 16) or
            ((b2.toLong() and 0xFF) shl 8) or
            (b3.toLong() and 0xFF)
        return raw * 0.1
    }
}
