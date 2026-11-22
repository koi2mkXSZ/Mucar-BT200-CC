# Chery Delphi II — confirmed OEM Data Stream selection path (2026-11-22)

Source: original archived libCHERY_OLD.so, libSEARCHID.so, active and backup CHERY_OLD_RU.GGP, all hash verified. Offline disassembly, native ELF relocation checks and decoded GGP record lookups. No ECU calls or changes.

## Native control flow / exported symbol evidence

- CheryDelphiII at RVA `0x13F3F0` supplies callback pointers and calls GeneralMain at RVA `0x13F470`.
- The passed pointers resolve through ELF64 GOT relocations to QR_CommDelphi2, QR_InitialDelphi2, QR_DtcCalcDelphi2, GeneralStreamCalc and QR_SpecialDelphi2.
- GeneralMain at `0x28DA7C` invokes its initializer via `blr x1`, which is QR_InitialDelphi2 on this path.
- QR_InitialDelphi2 at `0x13F91C`/`0x13F924` establishes base ID `76010001`. At `0x13F92C` it sets count `18`, and at `0x13F93C` writes count into iDataStreamItem (GOT `0x331C78`).
- Nine `stp` instructions from `0x13F954` to `0x13F9A8` fill 18 slots of DataStreamId (GOT `0x3326B8`).
- GeneralMain reads iDataStreamItem at `0x28DD30`–`0x28DD38`, iterates DataStreamId at `0x28DD50`, and invokes AddStreamSelectBox at `0x28DD54` (GOT `0x332E38`). It forms a selected-ID list at `0x28DDC8`–`0x28DDD8`; later invokes GeneralStreamCalc at `0x28DE6C` and AddDataStreamItem at `0x28DE8C` (GOT `0x332DD0`).

These are verified **static** callsites, not a captured live DollarFix session.

## Original Delphi II selection array: 18 entries

| Index | ID | Description from DSTREAM_RU.GAG |
|---:|---|---|
| 0 | 76010001 | Battery voltage |
| 1 | 76010002 | MAP sensor |
| 2 | 76010003 | IAT |
| 3 | 76010004 | ECT |
| 4 | 76010005 | Spark advance |
| 5 | 7601000C | TPS (mV) |
| 6 | 7601000D | TPS (%) |
| 7 | 7601000E | VSS |
| 8 | 7601000F | Engine speed |
| 9 | 76010010 | Injection pulse width |
| 10 | 76010011 | Idle air control |
| 11 | 76010012 | Target idle speed |
| 12 | 76010013 | O2 sensor |
| 13 | 76010016 | O2 sensor cross-counter |
| 14 | 76010017 | Canister purge |
| 15 | 76010018 | A/F ratio |
| 16 | 7601001B | Barometric |
| 17 | 7601001C | Engine running time |

**Neither 76010019 (EGR in backup) nor 76010020 (Mile meter) appears in the initialized array.** The current GGP's three-byte redirection of 76010019 to the 76010020 payload therefore cannot add either as a new selector entry in this branch.

## Validation and output

- ELF SHA256: `74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79`.
- GGP SHA256: `be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1`.
- libSEARCHID.so SHA256: `cfd6c96802f75055415f4917d27d8e909ed2af4046d587574eeb5500637264d3`.
- QR_InitialDelphi2 832-byte code hash: `d936f359ff1a045f9c9b4177ac830fedf9c1e5829bbd6d164e25eef06708f064`.
- Local offline script DollarFix_T11_Delphi2_menu_verify.py verifies SHA, ELF64/AArch64 relocations and instruction bytes, reconstructs array from ARM64 ADD/STP opcodes, then uses the previously verified GGP decoder to resolve names/formulas. It produced local JSON and Markdown evidence.

## Safe next step

Confirm the exact installed DollarFix diagnostic navigation route to CheryDelphiII (catalogues list Delphi 2.0/2.4 4G63/4G64, but routing is not yet demonstrated by a live trace). Confirm already-captured read-only diagnostic frames populate the driver buffer positions 56–59; adding a stream item might change ECU traffic or fail without valid data. Only then plan a reversible UI-only offline test that preserves requests/values, signatures and installed original. No ECU writes, odometer storage changes or license bypass.
