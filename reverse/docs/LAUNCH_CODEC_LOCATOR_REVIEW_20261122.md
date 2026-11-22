# LAUNCH .dat codec locator review — 2026-11-22

Source: user-uploaded `launch-codec-candidates.json`, generated from the original backed-up DollarFix APK, ARM64 split and 238 JADX Java files. All paths and file names are from the supplied report. This is marker-based static searching only; no decoder has been identified or executed.

## Verified scan scope

- `base.apk`: SHA-256 `139ba36fb5a0d12f53494bfefdf1a7224ebb864d07d97b91a1d2aee8f6cccb23`; 9 code members scanned.
- `split_config.arm64_v8a.apk`: SHA-256 `703bf7b3222b3a43958aef2b5e963a2494408b7d201cf423293d810c17a663e9`; 24 native code members scanned.
- Java sources scanned: 238 under `.../jadx-base/sources/com/cnlaunch` **only**. This is a limited subtree, not the entire decompiled application.
- Exact binary marker `LAUNCH 68 00 00 00 02` (reported by earlier log forensics) did **not** occur in these scanned code members / Java sources. A dynamically constructed header would evade this search.

## Evidence ranking and interpretation

| Rank | Module/source | Supported observation | Interpretation limit |
|---|---|---|---|
| 1 | `base.apk!/classes7.dex` | `SpecificDiagnoseLog`, `DiagnoseLog`, `LAUNCH` literal matches; score 130 | Not a codec proof, DEX offsets are string occurrences |
| 2 | `com/cnlaunch/diagnosemodule/utils/DiagnoseLogUtil.java` | `DATA_TYPE_DSTRING=1`, `DATA_TYPE_D4STRING=2`, `mLogBuffer` from excerpt | Likely log orchestration/recording; structure and encryption unknown |
| 3 | `com/cnlaunch/diagnosemodule/newinterface/DiagnoseDataSrc.java` | `CToJavaImplements.recordSendDataDiagnoseLog(...)`, `recordReciveDataDiagnoseLog(...)` | Potential bridge from transport bytes to recorder |
| 4 | `com/cnlaunch/diagnosemodule/service/DiagnoseService.java` | `mDiagnoseLogPath`, `mIsCollect`, `mIsOnlyUiDataCollect` | Session / collection flags |
| 5 | `DiagnoseLogOfflineFeedbackManager.java`, `DiagnoseLogDBHelper.java` | Persistent log metadata and `diagnose_log_data.db` | Record registration and packaging rather than codec |
| 6 | ARM64 `libLICENSE.so` | Only generic `LAUNCH` literal; score 15 | No specific sign of `.dat` handling |

Also found `DiagnoseBusiness.java` and `DiagnoseLogicBusiness.java`, but their marker hits can simply be class-name strings, not format handlers.

## Actionable next step

Inspect actual bodies of these Java classes, including the exact implementation or native bindings for `CToJavaImplements.recordSendDataDiagnoseLog` and `recordReciveDataDiagnoseLog`; correlate class writers with `SpecificDiagnoseLog` file creation and the format identifier in bytes 0..17.

To avoid uploading a complete APK or app-data backup, a tested offline `collect_launch_codec_sources.py` was generated as a private chat attachment. It reads the existing full JADX `sources` root, selects up to 16 relevant `.java` files and writes a SHA-256 manifest and zipped source copies **only**. Three tests passed with synthetic sources. The real Windows collection has not been run by ChatGPT.

## Safety and unresolved

No original LAUNCH log plaintext, native transport packet, driver-expanded 60-byte buffer or real odometer value was obtained. Do not assume a patent cipher applies to DollarFix, or that `libLICENSE.so` is the logger merely because it contains `LAUNCH`. Avoid modifications to APK, SO, GGP, Android and ECU. All actual diagnostic data remains private and out of the repo.
