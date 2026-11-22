# DollarFix diagnostic files: 21 Nov 2026 on-device recordings

Source: user's privately uploaded `Phone-recordings-20261121.7z`; extracted using libarchive and SHA256 checked locally. All results are **read-only**; no smartphone or ECU access in this analysis.

## Collected evidence

- ADB inventory surveyed 893 files, of which 21 have a 2026-11-21 device-local modification date (UTC+03); 7 candidates identified and 4 copied. An ADB `find` warning was recorded, so the scan may not be complete.
- Two native QIRUI_TY logs were copied from `ThinkDiag/Log/SpecificDiagnoseLog` and `ThinkDiag/Log/DiagnoseLog`, with lengths 23,546 and 23,642 bytes.
- An OBD text log of 1,540 bytes was copied from `ThinkDiag/Log/DiagnoseLog`. Its adapter exchange includes `DIAG_CONNECTED`, several `AT` setup commands, proprietary BT adapter `55AA...` request/reply pairs, and a subsequent `device.con.fail` event. This does not establish an ECU-level Delphi KWP session.
- A 37-byte `gdscan.ini` contained only `CollectorType=96`.

## Exact SHA256 (private logs — no binary committed)

- Specific QIRUI recording: `6e3d80e028a5fd8c980d74fd7fa05aaa41ef84d09313007aa695ea5776888b0f`.
- DiagnoseLog QIRUI recording: `f4b215bda7e3d6edc7cf9c31bf192e79d529e38362f630922c74cc6e52362ca6`.
- OBD adapter log: `87b199fc9e3d956e0e442e6baa6903db93e2ff3291b7bc3d5f9d042f272ddb96`.

## Binary QIRUI file similarities

- Both have 11 identical leading bytes with ASCII signature `LAUNCH` (bytes `4c 41 55 4e 43 48 68 00 00 00 02`). Header bytes 11–17 differ.
- The exact 23,457-byte span from offsets 18–23,474 inclusive is identical between files.
- Both have an identical final 64-byte suffix, despite a 96-byte file-size difference. They therefore appear to share a substantial recording payload but may differ in an additional section; the format has NOT been decoded.
- Shannon entropy is ~7.93 bits/byte; high entropy alone does not distinguish compression from encryption.
- The existing `libx431file.so` parser expects `X9LS` at offset 0 in `fi_checkfile` (AArch64 instruction at RVA 0xC688 compares little-endian magic `0x534C3958`). These QIRUI `.dat` files instead begin `LAUNCH` and should not be assumed to use the `lsx_rec_*` format.

## Result and blocker

**No verified Delphi ECU data or odometer value was decoded.** The text log establishes an adapter connection, not an ECU response. The QIRUI binary logs require the correct LAUNCH format decoder before determining which diagnostic branch ran or obtaining a real driver-expanded buffer; byte offsets [56..59] from the GGP odometer formula must NOT be applied directly to these opaque .dat files.

## High-value files on phone not included in the uploaded archive

- `ThinkDiag/temp/cloud_report_cache/..._20261121_..._QIRUI_TY.txt` (2,892 bytes), from the inventory.
- `DollarFix/SpecialFunction/FunctionMainMenu.txt` (1,589 bytes).
- `ThinkDiag/dpu_downloadbin_information.txt` (56 bytes).
- Prior day's `ThinkDiag/Log/DiagnoseLog/*_QIRUI_TY_20261120213908.dat` (10,522 bytes).

The first is the highest-priority plaintext candidate for system / menu identification. Pull these files **read-only** over ADB into ignored local storage and inspect privately. Do not upload VIN/license data publicly, modify GGP/SO/APK, or issue ECU write commands.
