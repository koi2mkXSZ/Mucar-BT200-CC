# OSS audit for Mucar-BT200-CC

Reviewed as architecture/protocol references. No third-party source code is copied into this project by this audit.

| Project | Useful for us | License / constraint | Decision |
|---|---|---|---|
| fr3ts0n/AndrOBD | Mature Android connection/service/UI separation, logging, multiple transports | GPL-3.0 | Architecture reference only unless project licensing is intentionally made GPL-compatible |
| barnhill/AndroidOBD | Small Android ELM327 library and transport separation | MIT | Patterns/code may be reused with attribution if needed; ELM AT layer itself is not BT200 |
| ETSoftwareStudio/obd-scanner-android | Modern Kotlin Android architecture and Bluetooth UX | Apache-2.0 | Good modern Android reference |
| bri3d/kwp2000 | Java KWP2000 state/protocol ideas | No license file found in audit | Read as reference; do not copy source |
| bri3d/kwp-android-logger | Android KWP logging design | License not established in audit | Read as reference; do not copy source |
| Ircama/ELM327-emulator | Deterministic ECU/emulator/replay testing concept | CC BY-NC-SA 4.0 | Concept reference only |
| muki01/OBD2_K-line_Reader | ISO9141/ISO14230 implementation reference | Verify repository terms before reuse | Protocol reference |
| muki01/OBD2_KLine_Library | ISO9141/ISO14230/KWP2000/K-Line implementation | Source-available; commercial use requires paid license | Do not copy; protocol/reference study only |

## Conclusion

ELM327 projects support separating physical transport, adapter protocol, diagnostic session, measurements and UI. MUCAR BT200 is not assumed to be ELM327-compatible. ELM AT commands do not belong in the BT200 implementation unless captured traffic proves otherwise.

Stage 2 architecture:

    Android Bluetooth
          |
    Bluetooth transport
          |
    BT200 envelope / DPU protocol   <-- unresolved boundary
          |
       KWP session
          |
    Chery/Delphi ECU profile
          |
    PID/measurement registry
          |
    Dashboard / logger

A replay transport is implemented first so protocol decoding and UI can be tested without the vehicle or adapter.

## Evidence required for the BT200 layer

1. Bluetooth Classic RFCOMM vs BLE/GATT.
2. Discovery/name/address selection.
3. Service/characteristic UUIDs or RFCOMM UUID/channel.
4. BT200/DPU request and response envelope.
5. Checksums, sequence numbers and fragmentation.
6. Adapter initialization and ISO14230 configuration commands.
7. Whether adapter authentication/licensing is required before raw diagnostic traffic.

Until these are supported by captured evidence, the app must not invent an ELM327 transport.
