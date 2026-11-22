# DollarFix T11 Delphi II — native route and saved driver-buffer gate (2026-11-22)

Source: original user-provided QIRUI V10.22 GGP and pinned `libCHERY_OLD.so` (SHA-256 `74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79`). Static disassembly only; no ECU/Bluetooth/Android write or runtime diagnostic session.

## Verified code locations

- `OldProEnter` contains two direct `CheryDelphiII@plt` callsites at RVA `0xE5CD0` and `0xE5D2C`. These demonstrate native menu dispatch branches, but do not determine which case is actually selected in this car.
- GGP `TEXT_RU.GAG` entry `FD050101`: `Delphi System 2.0L/2.4L(4G63/4G64)`; neighbor `FD050102`: `Mitsubishi System 2.0L/2.4L(4G63/4G64)`. Presence of the text alone does not map an exact old-menu jump-table case.
- `QR_CommDelphi2` at RVA `0x13F540` saves function argument `x2` into `x19`. It makes phase-dependent `SendRecvKwp` calls (one at `0x13F580`).
- On a conditional diagnostic-print branch it reads `ldrb w1,[x19,#0x38]` at `0x13F634`, `ldrb w1,[x19,#0x39]` at `0x13F648`, `ldrb w1,[x19,#0x3A]` at `0x13F654`, and `ldrb w1,[x19,#0x3B]` at `0x13F660`.
- Those correspond to **zero-based buffer byte offsets 56–59**, matching operands in GGP Mile meter expression. The printed bytes are not proof of odometer semantics in an actual ECU session.
- `QR_InitialDelphi2` still initializes 18 DataStreamId entries; neither ID `76010019` nor `76010020` is included; this omission is separately verified in `DELPHI2_MENU_SELECTION_VERIFIED_20261122.md`.

## Offline proof and tests

- A standalone *local-only* bundle named `DollarFix_T11_DelphiII_offline_validation_20261122.zip` was generated in this conversation. It contains `DollarFix_T11_Delphi2_trace_gate.py`, the two previously verified source decoders, a Markdown report and JSON evidence; no vendor native binaries.
- The checker verifies the exact native ELF hash, ELF/AArch64 GOT metadata and 8 opcode bytes. It optionally evaluates `--buffer-hex` only when the argument is an **already captured internal driver buffer of 60+ bytes**, NOT a raw KWP frame.
- Six local unittest cases passed, including a checksum mismatch, a too-short KWP-like frame, and a **synthetic** 60-byte sample (`00 0F 42 40` at indices 56–59 -> 100000.0 km). Synthetic value is NOT a live vehicle reading.
- No saved real driver buffer, normal-usage log or direct evidence of this specific menu selection was attached; real mileage is **unverified**.

## Patch gate

Do not deploy a modified APK or `libCHERY_OLD.so` yet. The existing 18-element selector omission is proven for a static Delphi II path, but adding a new item may affect on-wire reads and request timing. Next, correlate an already captured normal-usage diagnostic trace or offline ECU replay with the actual selected branch and the 56–59 byte mapping. Compare transport behavior before/after any proposed display-only change. Preserve originals and never write ECU mileage or bypass license checks.
