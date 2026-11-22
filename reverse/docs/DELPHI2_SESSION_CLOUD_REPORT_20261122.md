# Verified actual 21 Nov 2026 QIRUI Delphi II session (cloud-report cache)

## Evidence and scope

- User-provided private `DollarFix-session-extra.zip` contains `cloud_report.txt` (2892 bytes), `dpu_info.txt` (56), `FunctionMainMenu.txt` (1589), and prior-day `QIRUI_previous.dat` (10522). Files checked individually; Android/ECU not accessed.
- `cloud_report.txt` is a **single Base64 string** decoding to a 2167-byte UTF-8 JSON document with `data` entries types 1, 2 and 3. Outer SHA256 `6d2d3f51c4c59712c9936046e443225df19fe46c8723b6452e77aa33c4d33815`, decoded JSON SHA256 `03e6ade43d49218443737a1af2e5e66e8190433f1ac2e20e00c72f5c5649766a`.
- This repository does NOT store the original report or any serial number, user ID, VIN, private path, adapter identifier or diagnostic account information.

## Actual selected vehicle and ECU menu

- Diagnosis path: `QIRUI_TY V10.22 > Tiggo Series > Tiggo 1/Tiggo 3(T11/T11FL/T11FL3) > System Selection > ECM (Engine Control Module) > Delphi System 2.0L/2.4L(4G63/4G64)`.
- `think_report_type=DATASTREAMS`; `name_id=fd050101`; **`system_uid=0000f11a`**; reported system `Delphi System 2.0L/2.4L(4G63/4G64)`; software V10.22, DollarFix app 1.9.4.
- Native `OldProEnter` static jump-table selector `0xF11A` maps to handler `0xE5CEC`, calling `CheryDelphiII` at `0xE5D2C` (see DELPHI2_DRIVER_BUFFER_GATE_20261122.md). The actual report UID now independently corroborates the **chosen native Delphi II case**. We still lack a raw ECU packet or traced live buffer.
- Report was formed at local time 2026-11-21 18:53:13. A separate DPU information file records V23.04 with 2026-11-21 18:51:20 UTC+3.

## Two saved OEM data-stream entries

| ID | Title | Value | Unit | Local timestamp UTC+3 |
|---|---|---:|---|---|
| `7601000f` | Engine speed | 728 | rpm | 2026-11-21 18:51:20.879 |
| `76010013` | O2 sensor | 667 | mV | 2026-11-21 18:51:20.879 |

- Both IDs are included in the **verified original 18-element** `QR_InitialDelphi2` `DataStreamId` array (DELPHI2_MENU_SELECTION_VERIFIED_20261122.md). This is strong cross-validation of the previously reconstructed display pipeline.
- The report contains **only two selected/saved items**; it does not claim to be an exhaustive list of the UI selectors.
- The report contains **no `76010020` datastream value**. This agrees with static initialization omitting the ID but does not prove the underlying ECU lacks the datum.
- In vehicle metadata section type 3, the field `mileage="0"`, `mileage_unit="MILES"` is **not a decoded odometer value**, and should NEVER be displayed as actual ECU mileage. Original GGP `76010020` has unit `Km`, creating an additional unit-conversion matter for any UI-only candidate.

## Other extracted files

- `FunctionMainMenu.txt` defines OILRESET/BRAKERESET/BMSRESET brand support lists; it does not contain the OEM Delphi ECM datastream selector.
- `dpu_info.txt` records the adapter download-binary version V23.04; not an ECU data capture.
- The 10522-byte prior-day `QIRUI_previous.dat` begins with `LAUNCH\x68\x00\x00\x00\x02`, matching the format family of the 21-Nov logs; its encrypted/compressed record payload remains undecoded. It contains no trustworthy human-readable ECU odometer measurement.

## Validation / patch gate

An offline stdlib parser `Analyze-DollarFix-CloudReport.py` was exercised on the actual file and passed 5 synthetic tests. It emits redacted Markdown and JSON but does not decode `.dat` or contact the vehicle.

**Major blocker resolved:** live selected Delphi II menu system UID 0000f11a now documented, corroborating the native F11A route.

**Remaining blocker:** obtain verified driver-expanded buffer bytes 56–59 or establish their mapping from native `SendRecvKwp` response to an already captured trace. Until then, adding 76010020 to the native 18-entry UI selector is an offline dry-run hypothesis; no modified APK/SO/GGP should be installed and no ECU write commands or odometer changes are appropriate.
