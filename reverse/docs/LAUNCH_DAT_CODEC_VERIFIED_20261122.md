# DollarFix T11 — LAUNCH .dat fully decoded (2026-11-22)

## Source and privacy

Private user-provided JADX Java source bundle `LAUNCH-codec-Java-20261122_140234.zip` (13 Java files), original two QIRUI_TY logs from 21 Nov and one from 20 Nov. Original logs and private identifiers are **not included in the public repository**. A verified Python decoder with the vendor's embedded matrices is furnished privately in the ChatGPT conversation, not committed publicly.

## Format established from original app code

- Class: `com.cnlaunch.diagnosemodule.utils.DiagnoseLogUtil`, nested `SafeMatrix`. `encryptionContent`, `decryptionContent`, `multiMatrix` implement fixed 8x8 block-matrix transforms with byte arithmetic modulo 256.
- Log writer: nested `LogRecordThread.writeLogRecordHead`, `writeContent`, and `writeToOutputStream`; producer: `com.ifoer.expedition.cto.CToJavaImplements.recordSendDataDiagnoseLog` and `recordReciveDataDiagnoseLog`; Android source `DiagnoseDataSrc` invokes them.
- On-disk layout: 6-byte `LAUNCH` magic, little-endian 32-bit header length (**104** in these files), independently encrypted 8-byte-aligned header plus body, version bytes **02 01**, 8-byte creation timestamp, variable-length strings, records `[type u8][format=1 u8][payload_length u16 BE][payload][record_timestamp u64 LE]`, terminating zero type, padding, footer of four length-prefixed strings and a u32 LE footer length.
- The header decrypts as `QIRUI_TY`, `V10.22`, `RU`, adapter component `V23.04`, app `1.9.4`. Footer validates `CHERY`, `Tiggo Series Tiggo 1/Tiggo 3(T11/T11FL/T11FL3)`; VIN and device serial redacted.
- Every decrypted 8-byte block encrypts back to its **original exact bytes**. All three files parse into records without errors, including correctly sized footer. Local synthetic tests: **6 of 6 passed**.

## Exact counts, events and data-stream results

| Log | Date/local time UTC+03 | Records | Type 1 UI request | Type 2 UI response | Type 3 adapter send | Type 4 adapter receive |
|---|---|---:|---:|---:|---:|---:|
| 21 Nov SpecificDiagnoseLog | 18:51:25.772 | 487 | 129 | 128 | 115 | 115 |
| 21 Nov DiagnoseLog | 18:55:45.942 | 491 | 131 | 130 | 115 | 115 |
| 20 Nov | 21:39:08.176 | 235 | 52 | 51 | 66 | 66 |

- The **first 487 records of both 21-Nov files are byte-identical** in type, payload and timestamp; the longer file adds four UI completion events. They are not two independent runs.
- Three UI type-1 payloads with opcode `0x11` contain a list of **18 exact `760100xx` IDs**. The IDs match the previously static-reconstructed `QR_InitialDelphi2` `DataStreamId[]` array. **76010020** (Mile meter) is absent.
- UI type-1 payloads with opcode `0x12` include actual displayed ID/value pairs: at 18:52:08.649 `76010013=92` mV; at 18:52:24.362 `76010013=623` mV; at 18:53:06.467 `7601000F=714` rpm and `76010013=468` mV. These are duplicated across the two 21-Nov logs, not independent measurements.
- A previously decoded `cloud_report.txt` separately contained `7601000F=728` rpm / `76010013=667` mV with a different earlier timestamp, 18:51:20.879. Do not combine unrelated measurements.
- UI history contains `Clear Fault Memory` followed by `Clear Code Successfully` around 18:51:55 (21 Nov); this is a **historical vehicle interaction**, not performed by our offline analysis. There are two recorded `ICM` communication error dialogs around 18:55.
- 3/4 adapter records contain a `55 AA ...` wrapper: these are **not automatically equivalent** to a raw KWP ECU response or a 60-byte driver-expanded buffer.
- Prior-day 20 Nov report has no type-1 `0x11` selector or type-1 `0x12` Data Stream value message, although it contains other diagnostic events.

## Status

**Codec resolved and complete LAUNCH record content parsed** (header, timestamp, app-side UI, adapter frames, footer). A reproducible offline Python decoder and privacy-minimized JSON/Markdown report were generated in the ChatGPT sandbox; shipped as `LAUNCH_T11_decoder_verified_20261122.zip` in the conversation. No proprietary `.dat`/APK/SO/GGP files or hardcoded vendor matrices are committed to the repo.

**Unresolved for odometer:** this session did not request/emit `76010020` as a UI stream item. The valid byte mapping between original ECU KWP traffic inside `55 AA` adapter frames, `QR_CommDelphi2`, and internal driver buffer `[56:60]` has not been established. Do not report any mileage from guesswork or make on-device patches before proving traffic impact. No ECU or APK changes have been performed.
