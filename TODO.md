# Mucar-BT200-CC TODO / continuity

## Completed

- Stage 1: Android/Kotlin skeleton, CI debug build, Delphi T11 KWP frame and odometer vector.
- Stage 2 groundwork: decoded DPU request/response transaction model and replay harness.
- Historical T11 capture: positive KWP 21 01 -> 61 01, odometer raw 00 0F 42 40 -> 100000.0 km.
- CHERY_OLD_RU.GGP has the odometer identifier 76010020; earlier EGR descriptor redirect failed to surface the hidden item.
- ELM327/KWP OSS architecture and licensing audit.
- Windows REA + Codex static-analysis runner and documented investigation tasks.
- Read-only APK/ELF inventory scanner and synthetic regression tests.
- Исправлен поиск adb.exe и добавлена установка официальных Google Platform-Tools по явному ключу -InstallAdb.
- User confirmed successful read-only ADB snapshot of four installed APKs (base + arm64-v8a + ru + xxhdpi) on 2026-11-22, with file sizes and SHA-256; see reverse/docs/INSTALLED_SNAPSHOT_20261122.md. This is a report of local execution, not a remotely rerun independent check.
- Added scripts/Analyze-DollarFix-Snapshot.ps1 to verify original four-file set against manifest and inventory each split separately, then run available JADX/Apktool/REA/Codex. Synthetic Windows CI passed: https://github.com/koi2mkXSZ/Mucar-BT200-CC/actions/runs/45003093353

## Not yet verified

- Original current installed APK bytes are preserved locally on the user's Windows computer; this ChatGPT runtime has only user-reported hashes/paths, not the actual binary contents.
- Real REA/Codex execution against DollarFix: local agents are not remotely exposed in this ChatGPT session.
- Bluetooth Classic/BLE choice, UUID, BT200 DPU framing and JNI call path.
- Delphi visible PID selection mechanism.
- Patched, rebuilt and signed APK, plus installation and on-vehicle test.

## Next concrete actions

1. Run scripts/Analyze-DollarFix-Snapshot.ps1 on the saved four APKs and capture tool-status.json / per-split inventory; add optional QIRUI ZIP if available.
2. Trace Android Bluetooth -> JNI -> Launch DPU with file/method/offset evidence.
3. Trace Delphi Data Stream selection/classification to hidden ID 76010020.
4. Implement minimal read-only display patch after exact target hash and control flow are confirmed.
5. Build/sign/test independently; preserve original app installation/data and maintain a rollback.
6. Update TODO.md after every iteration.

## Iteration 2026-11-22: successful APK hashing, next RE step

- Confirmed from user terminal: the four live extracted APK files exactly match their snapshot manifest sizes and SHA-256; no modifications to the originals.
- Reviewed user's tool-status.json: all four per-split inventories exit_code 0; JADX and Apktool not found; REA Doctor exit 1 (diagnostic detail not yet available); REA providers exit 0; Codex exit 1 with `Not inside a trusted directory` because the runner invoked Codex from the non-Git parent folder.
- Fixed Codex working directory to the tooling Git checkout and added output-only sandbox extra directories; do not bypass Git trust or disable sandbox.
- Added opt-in pinned JADX 1.5.7 / Apktool 3.0.3 installer with official GitHub asset SHA-256 verification, and local tool discovery.
- Added -SkipInventory to preserve previous successful inventories while still validating original APK hashes.
- Next verification: run Windows smoke CI on new changes; then run local installer and rerun split-aware script. Inspect per-tool logs and real REA Doctor report before assigning any binary offsets or writing patches.

## Iteration 2026-11-22: Codex/REA result review (user-provided reports)

- New tool-status confirms installed snapshot SHA-256 verification; Apktool base and all three splits exited 0; Codex exited 0 and generated four local authored documents.
- REA Doctor still reports healthy=false because optional Ghidra, native JADX MCP plugin, IDA, Hopper etc. are absent; the provider catalog and Codex summary confirm some Android static analysis calls were available/succeeded. Do NOT equate Doctor nonzero with global REA failure.
- JADX v1.5.7 CLI exited 3. No JADX error details have yet been provided: inspect reverse/reports/DollarFix-installed-20261122_112739/jadx-base.log before diagnosing.
- Codex summary reports candidate UI path PIDV -> PIDV.toBasicDataStreamBean() -> BasicDataStreamBean.id -> Data Stream UI and a read-only hook on ID 76010020. Detailed markdown reports have NOT yet been independently reviewed here; no code or binary patch is confirmed.
- Codex reports no libCHERY_OLD.so in arm64 APK split and QIRUI ZIP absent. This does not exclude a native driver in the separately downloaded QIRUI_TY diagnostic package.
- Added scripts/Backup-DollarFix-Qirui.ps1 (read-only ADB download of QIRUI_TY V10.22 from DollarFix external storage), updated Codex task for real split snapshots, and scripts/Export-DollarFix-Review.ps1 to package the four local markdown reports plus last 200 JADX log lines for private review.
- Next: review actual authored reports and JADX error excerpt; optionally retrieve QIRUI package from phone. Confirm exact class/method/line or smali signatures before any minimal read-only UI patch. No APK was modified, signed, executed or installed.

## Iteration 2026-11-22: full review ZIP analyzed

- Read user-uploaded DollarFix-review-20261122_121155.zip (4 technical reports, TODO, tool-status, last 200 JADX lines), not merely its filenames. Findings documented in reverse/docs/REVIEW_20261122.md.
- Codex documented installed version 1.9.4 (code 1940), native libSearchId, libSocket and JniX431File, and candidate PIDV.toBasicDataStreamBean(). The only observed selected-PID flow goes through ELMDataViewUtil/DataStreamScene, **not established as a proprietary Delphi UI path**. Do NOT patch BasicDataStreamBean based solely on this.
- JADX progress reached 99% of 27,411 classes but printed 443 aggregate errors. Individual failure details are missing from supplied tail, so root cause is not yet established; exploit available Apktool smali/REA evidence rather than blindly treating the whole codebase as decompiled.
- Added reverse/tools/trace_data_stream.py + synthetic tests, creating local structured marker locations without copying proprietary source lines.
- Added a review document summarizing exact gaps and an evidence-based plan to trace OEM/QIRUI item creation, selection and display.
- Next: run reference locator on local smali + partial JADX and share resulting JSON/Markdown; separately capture QIRUI driver package from phone (if accessible). Do not install any patched APK until exact code-level proof and package signing plan exist.

## Iteration 2026-11-22: source reference map from 111195 files

- User uploaded `source-reference-map.json` and `.md` from local Apktool/JADX scan; inspected complete structured JSON and marker/method groupings.
- 111195 text source files scanned; 14 skipped. Exact string `76010020` appears zero times among scanned text files. This is **not** proof it is absent from the device's QIRUI GGP or binary native code.
- Candidate OEM files confirmed by lexical signatures: `com.cnlaunch.diagnosemodule.DiagnoseLogicBusiness` (`dealDataStream`, `getDataStreamCount`); `DiagnoseUIDataBusiness` (`jsonUIDataStream`, `getDefDataStreamDatraFromJson`, `jsonUIDiagnoseSpecialDatastream`); `BasicDataStreamBean` (`clearMapDataStreamID2ChoicePos`); Thinkcar `UiDataStreamManager`.
- `PIDV.toBasicDataStreamBean` is in `com.dnd.dollarfix.elm327.bean.PIDV`; do not use ELM-based patch for OEM Chery Delphi without evidence.
- Most GGP literal hits refer to VIN/GGP metadata, and `IdSearch` literal hits to unrelated AndroidX Compose SearchBar. Avoid false-positive reverse engineering conclusions.
- Added `reverse/docs/TRACE_MAP_20261122.md` for evidence trail, `reverse/tools/extract_oem_trace.py` to produce bounded local-only Smali method excerpts with file and line anchors and synthetic tests. Fixed `elm327` filename classification in lexical scanner. CI passed at e718c040.
- Next: execute targeted OEM Smali extractor and review its output; separately capture device QIRUI files to determine if `76010020` is emitted/hidden. No APK patch has been created.


## Iteration 2026-11-22: OEM Smali deep review

- Reviewed local user upload oem-smali-evidence.json and .md (7 Smali files, 55 matched methods; target files all present).
- Confirmed concrete OEM callsites in DiagnoseUIDataBusiness.jsonUIDataStream: menudata array -> JSONObject -> BasicDataStreamBean(JSONObject) -> ArrayList.add, and conditional addDataStreamBeanInfo.
- Confirmed BasicDataStreamBean.Id is an optional **string** JSON field, while Const_Text_Item and SN are **integer** item numbers; getArrDefaultSelected stores integer selections.
- Confirmed the OEM selection pathway includes getShowIndexDataStream()[I for message type 801 and pageStreamFeedbackMask/getDatastreamMask; no direct 76010020-specific filter in available limited snippets.
- UI layer includes conversion in UiDataStreamManager and list data/observer handling in DataStreamManager. Still no causal evidence of a lost odometer item.
- Added reverse/docs/OEM_SMALI_REVIEW_20261122.md with exact Smali line references.
- Added reverse/tools/probe_qirui.py and synthetic reverse/tests/test_probe_qirui.py; GitHub Actions run 45007701740 passed. Tool only inventories and probes downloaded QIRUI binary package locally.
- Blocker: no QIRUI_TY V10.22 diagnostic-driver bytes or real-world OEM menudata JSON capture attached. Do not infer runtime Id == GGP key 76010020, nor claim ability to patch yet.
- Next: read-only QIRUI backup / binary probe. Compare actual OEM JSON Id/Item/SN, then locate an evidence-supported display-only change. Preserve installed original and never send ECU write commands.
