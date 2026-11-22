# DollarFix T11 — offline structure of LAUNCH .dat diagnostic archives (22 Nov 2026)

Analysis of three **private** native QIRUI_TY diagnostic `.dat` files captured 20–21 Nov 2026, together with the previously verified original Delphi II QIRUI V10.22 driver. Original logs and identifiers remain in the user's private local storage / chat; no proprietary content is added to this repo.

## Sources verified by SHA-256

| Source | Date / type | Bytes | SHA-256 |
|---|---|---:|---|
| log_1 | 21-Nov, SpecificDiagnoseLog | 23546 | 6e3d80e028a5fd8c980d74fd7fa05aaa41ef84d09313007aa695ea5776888b0f |
| log_2 | 21-Nov, DiagnoseLog | 23642 | f4b215bda7e3d6edc7cf9c31bf192e79d529e38362f630922c74cc6e52362ca6 |
| log_3 | 20-Nov, DiagnoseLog | 10522 | b0d5122109cd7f68ee1ded24051931f4564a75d6ede3f5d4ec045bf59eb78fc9 |

## Reproducible structural facts

- Every file starts with ASCII `LAUNCH` (6 bytes). Bytes 6–9 interpreted as an LE unsigned integer equal **104** (hex `68 00 00 00`); byte 10 is **2**. Actual field semantics are not independently proven.
- Bytes **18..121** inclusive (104 bytes) are **identical** across all three logs. Bytes **11..17** vary between files. Bytes 122 (00) coincides across all three.
- The final **64 bytes** of each original file are exactly the same.
- For each length L, `(L - 122 - 64) % 8 == 0` and `%16 == 0`, suggesting a candidate encoded segment from absolute position 122 through L-65. These offsets are **structural hypotheses**, not a verified parser.
- The candidate encoded body has Shannon entropy approximately **7.9034–7.9267 bits per byte**. High entropy alone cannot distinguish compression, encryption or mixed encoding.

## 8-byte aligned comparisons

| Comparison | Aligned blocks equal | Blocks compared | Long matching runs (>=4 blocks) | Longest run |
|---|---:|---:|---:|---|
| log_1 vs log_2 | 2919 | 2920 | 1 | 23352 bytes starting offset 122 |
| log_1 vs log_3 | 897 | 1292 | 57 | 1400 bytes starting offset 1786 |
| log_2 vs log_3 | 897 | 1292 | 57 | 1400 bytes starting offset 1786 |

Comparing the two logs from 21 Nov: the first **2,919** common 8-byte candidate blocks match, then the last comparable block changes; the second file contains **12 extra** blocks (96 bytes), and the final 64-byte tail is unchanged. This is compatible with two saved stages of one diagnostic session but is not definitive proof of identical capture windows.

Comparing 20 vs 21 Nov: 897 of 1292 blocks (about 69.4%) coincide at aligned positions; this supports deterministic repeated metadata/records rather than an entirely independent random stream. It does not reveal plaintext.

## External contextual research (not proof of implementation)

- LAUNCH patent CN108227579A, https://patents.google.com/patent/CN108227579A/en, describes encrypted vehicle diagnostic files with a separate file header, multiple encrypted blocks and a possible modified Hill cipher, as a conceptual example. It does **not** show that DollarFix's LAUNCH-v2 records use that exact cipher, key, or header interpretation.
- Open-source x431-to-csv (https://github.com/ucukertz/x431-to-csv) targets `.x431` / `.dzx` recording formats and **does not claim support** for these proprietary `LAUNCH`-header `.dat` files. Do not rename .dat to .x431 or treat X9LS as the same format.

## Research artifacts and next action

- Generated private `LAUNCH_T11_offline_comparison_20261122.{json,md}` from original binary logs using a read-only stdlib Python script `analyze_launch_dat.py`. Five synthetic tests passed.
- Created `find_launch_codec.py`, scanning original saved APK `.dex/.so` ZIP members and optional decompiled Java/Smali, for `LAUNCH` format, `SpecificDiagnoseLog`, and related record/encryption markers. Three synthetic tests passed. Script outputs a bounded local JSON candidate report, **not** proprietary executables.
- The code and synthetic tests are contained in the private conversation deliverable `LAUNCH_T11_forensic_tools_20261122.zip`.
- The appropriate next action is running this locator on the original backed-up `base.apk` and ARM64 split and on existing JADX output in user's Windows workspace. After identifying the actual codec implementation and verifying its handling, attempt **offline read-only decoding** of the saved logs.

## Unresolved

- **No validated LAUNCH .dat decoder**; **no ECU read frames** extracted; **no real odometer bytes** obtained. Never interpret file offsets 56..59 as driver-buffer byte offsets.
- We already have an independently verified live app cloud-report proving 21-Nov selected system UID `0000f11a` (native CheryDelphiII) and two displayed streams: 728 rpm, 667 mV. This does not by itself establish the mileage value.
- Preserve original APKs, .dat, .GGP and .so. Do not modify installed application or ECU, issue odometer writes, or bypass licensing.
