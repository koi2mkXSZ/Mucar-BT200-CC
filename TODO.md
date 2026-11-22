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

## Iteration 2026-11-22: captured QIRUI and binary probe review

- User successfully read-only pulled QIRUI_TY V10.22 from Android with 79 files / 38,502,050 bytes; latest capture location is reverse/input/QIRUI-installed-20261122_123943.
- Received qirui-probe.json/md. They refer to an earlier capture ending _121203; scanned 80 files because the generated 20,309-byte qirui-manifest.json was included. Fixed reverse/tools/probe_qirui.py to skip that locally created metadata. Real diagnostic assets remain 79 files.
- Confirmed filenames and hashes: libCHERY_OLD.so and CHERY_OLD_RU.GGP present in on-device driver (not arm64 APK split). Second CHERY_OLD_RU.GGP.T11ODO.BAK has same length but different SHA256; there is NO proof which version is factory original.
- A simple literal scan of both GGP versions did NOT find 76010020 or Mile meter in tested byte encodings. Does not prove absence from decoded/indexed or compressed data.
- Added reverse/docs/QIRUI_PROBE_REVIEW_20261122.md and reverse/tools/compare_chery_ggp.py + synthetic tests to locate byte regions changed by earlier T11ODO experiment. Tool is local read-only, reports bounded offsets and previews.
- Next: run comparison on latest local capture; correlate changed offsets with GGP record format and Delphi driver's static code. Still no proven OEM menudata route for 76010020. Do not alter installed app or any ECU values.

## Iteration 2026-11-22: exact QIRUI GGP diff reviewed

- Reviewed user-uploaded ggp-diff.json and .md referring to latest QIRUI-installed-20261122_123943 backup.
- Both CHERY_OLD_RU.GGP and CHERY_OLD_RU.GGP.T11ODO.BAK are 3,420,296 bytes; SHA256 differ as documented in reverse/docs/GGP_DIFF_REVIEW_20261122.md.
- Exactly 3 modified bytes at decimal offsets 982385 (current 7B, backup 7A), 982386 (current 76, backup E7), 3224885 (current E8, backup 74); unchanged bytes 3,420,293. Two changed 8-byte contexts appear in patterned records but format is unknown.
- No literal `76010020` across the candidate encodings or ASCII `Mile meter`. This is a negative literal test only, not proof of absence from GGP.
- Latest next action: privately obtain both actual 3.42 MB GGP binary files plus libCHERY_OLD.so (3.30 MB), compare hashes, reverse GGP container and ELF readers; no more blind UI patches or phone changes.

## Iteration 2026-11-22: inspected actual uploaded GGP and ELF binary bytes

- Inspected DollarFix-T11-GGP-20261122_124621.zip offline and verified all three SHA256 hashes: active GGP be351e..., .T11ODO.BAK ac4d52..., and libCHERY_OLD.so 74e490....
- Both GGPs start with magic 47 47 50 00, are 3,420,296 bytes, and differ at exactly 982385, 982386, 3224885. Verified locally repeating 8-byte record patterns in both affected regions. Semantics of the record, and relationship to mileage, remain unproven.
- ELF is AArch64 ELF64 little-endian with Build-ID 5cf17ddd4dc2fac7e798a9f6ae58f980852336cb. Direct CheryDelphiII -> GeneralMain@plt, QR_CommDelphi2 -> SendRecvKwp@plt / QR_InitialDelphi2@plt, and GeneralStreamCalc -> getdata@plt callsites verified by llvm-objdump.
- GGP readers are exposed via callback pointers like SearchIdOpenFile, fseekGGP, GetGAGOffsetFromGGP. Need libSEARCHID.so from saved arm64 split for actual GGP parsing.
- Added reverse/docs/T11_GGP_ELF_ANALYSIS_20261122.md and a safe pinned parser extractor reverse/tools/extract_ggp_parser_libs.py plus synthetic tests. CI passed at https://github.com/koi2mkXSZ/Mucar-BT200-CC/actions/runs/45009546877.
- Next: inspect libSEARCHID.so and libx431file.so; link GGP record decoding to the OEM Delphi menu and 76010020. Do not modify original APK, patch GGP blindly, or send ECU writes.

## Iteration 2026-11-22: GGP search index completely decoded for target IDs

- Received GGP-parser-evidence.zip containing libSEARCHID.so and libx431file.so, extracted from original SHA-pinned arm64 split. Verified both native library checksums (see reverse/docs/GGP_INDEX_DECODE_20261122.md).
- Disassembled libSEARCHID.so: GGP files have a 1093-byte header with 15 encrypted 72-byte section entries. Reproduced Rijndael-256/256 section name decoding offline, validated all 15 names, and identified DSTREAM_RU.GAG and XDSDATA.GAG section ranges.
- Decoded 5.03 LAH GAG record index: DSTREAM_RU.GAG has 15,771 entries; XDSDATA.GAG has 375 entries, each a four-byte key + four-byte transformed offset. ID 76010020 is **present already** in both sections.
- Decoded data: 76010020 = 'Mile meter', 'Km' and equation F1=[56]1677721.6*[57]6553.6*+[58]25.6*+[59]0.1*+. Verified formula yields 100000 km for input 00 0F 42 40 interpreted as four driver-buffer bytes.
- Exactly three earlier edited GGP bytes redirect ID 76010019 (EGR position) pointers to the already-existing 76010020 (Mile meter) payload; original keys/index rows are unchanged. This confirms what earlier experiment changed and explains why redirection could not add a new selectable OEM menu entry.
- Generated read-only offline Python verification script and decoded JSON/Markdown reports. No APK/driver/ECU/phone changes.
- Persisted report reverse/docs/GGP_INDEX_DECODE_20261122.md. Next: inspect OEM menu selection emitted by vehicle-specific driver and trace to Android DiagnoseUIDataBusiness.jsonUIDataStream and numeric selection mask; do not blindly edit existing GGP pointer fields.

## Iteration 2026-11-22: proved CheryDelphiII stream selection omission

- Disassembled QR_InitialDelphi2 in original libCHERY_OLD.so and verified GOT relocation names via ELF64/AArch64. The function writes 18 IDs into DataStreamId and count 18 into iDataStreamItem; neither 76010019 (EGR) nor 76010020 (Mile meter) is included.
- Verified actual chain: CheryDelphiII -> GeneralMain -> QR_InitialDelphi2; GeneralMain reads iDataStreamItem/DataStreamId, invokes AddStreamSelectBox, and routes chosen IDs to GeneralStreamCalc and AddDataStreamItem. Critical static callsites recorded in reverse/docs/DELPHI2_MENU_SELECTION_VERIFIED_20261122.md.
- The prior GGP EGR pointer alias did not add a new selectable stream item because neither 76010019 nor 76010020 appears in this branch's 18-entry selector; this explains the ineffective change under the confirmed static branch semantics.
- Created and executed offline build-pinned DollarFix_T11_Delphi2_menu_verify.py, extracting all 18 entries directly from ARM64 ADD/STP instructions, checking dynsym/GOT relocations and matching each selected ID to its decrypted GGP title. Saved JSON/Markdown and a ZIP with scripts and proof; no proprietary ELF/firmware committed.
- External technical catalogues identify Chery Tiggo T11 2.4L 4G64 with Delphi MT20U / Chery diagnostic menu 2.0/2.4 4G63/4G64. Do NOT substitute earlier analyzed Delphi MT22U stream entry for this actual target. Branch CheryDelphiII is a strongly supported candidate but exact on-device navigation still needs confirmation.
- Next blockers: confirm live DollarFix branch CheryDelphiII; inspect previously saved **read-only** Delphi normal diagnostic frame and test whether driver data positions 56..59 are populated without new ECU requests. No ELF/APK patch or ECU action until this is verified.

## Iteration 2026-11-22: Delphi II native routing & driver-buffer validation gate

- Verified `OldProEnter` dispatch contains **two** direct `CheryDelphiII@plt` calls (ELF RVAs 0xE5CD0, 0xE5D2C), plus previously verified GeneralMain -> QR_InitialDelphi2 selection-chain. On-device actual menu choice still not proven.
- Decrypted exact GGP `TEXT_RU.GAG` menu label ID FD050101 `Delphi System 2.0L/2.4L(4G63/4G64)` and FD050102 Mitsubishi 2.0/2.4L. Presence of text alone is not proof of mapping to either callsite.
- More important: `QR_CommDelphi2` at 0x13F540 copies parameter x2 to x19; conditional debug code at 0x13F634, 0x13F648, 0x13F654, 0x13F660 reads four bytes [x19+56..59] following phase-specific SendRecvKwp operation. These are EXACT offsets of the already-decoded Mile meter GGP equation, but not a proof of real ECU values.
- Created and executed local `DollarFix_T11_Delphi2_trace_gate.py`: pinned ELF checksum + native symbol/opcode check for eight sites, rejects changed binaries and raw short frames; optional offline 60+-byte **existing driver buffer** evaluates `(uint32_be)/10`. Six local unit tests passed including synthetic 100000 km example. No live buffer was available.
- Packaged verifier with earlier two decoders, JSON evidence and report in `DollarFix_T11_DelphiII_offline_validation_20261122.zip`, supplied privately to the user. No proprietary binaries included. Uploaded report is `DollarFix_T11_DelphiII_trace_gate_20261122.md`.
- Repo technical summary: `reverse/docs/DELPHI2_DRIVER_BUFFER_GATE_20261122.md`. No binary patches or Android changes, no ECU/BT200 traffic, no odometer writes.
- Next blocking evidence: saved normal-usage diagnostic log of the *selected* Delphi 2.4L branch and internal driver buffer (>=60 bytes) mapped from received frame. Do not assume raw KWP message offsets equal the C driver buffer offsets. Only then do offline replay/transport invariance check and plan reversible display-only change.

## Iteration 2026-11-22: OldProEnter jump table decoded; offline-only candidate prepared

- Verified OldProEnter takes selector as W0, copies to W20 (0xE4F40), and indexes signed offset jump table at RVA 0x2C2DF8 with W20-0xF101. Switch values F119 and F11A point to handlers E5C90/E5CEC, which call CheryDelphiII at E5CD0/E5D2C.
- The encrypted GGP TEXT_RU label FD050101 is Delphi System 2.0L/2.4L(4G63/4G64), but **no proven runtime relation yet** between user UI label and F119/F11A native switch cases.
- Implemented offline source verifier that checks ELF SHA256, 9 opcode positions, 2 jump-table entries, and conditionally extracts [56..59] from an already captured internal driver buffer; 6 tests pass. Synthetic 00 0F 42 40 at those offsets evaluates to 100000.0 km, NOT actual mileage.
- Generated optional 19-entry **JSON-only dry run** preserving all original 18 stream IDs and appending 76010020; not a binary patch and NOT proven transport-invariant. Packaged verified Python scripts/report/JSON for user download.
- GitHub document reverse/docs/DELPHI2_DRIVER_BUFFER_GATE_20261122.md updated. Next blocker: no actual normal-usage diagnostic trace or 60+ byte mapped internal driver buffer. Do not modify installed APK, native SO, GGP or ECU. Validate which menu code is chosen, and whether adding a display item changes on-wire traffic before preparing a reversible patch.

## Iteration 2026-11-22: discover yesterday's actual Android diagnostic recording

- User states a real phone recording was made yesterday, 2026-11-21, and requests a search on the phone.
- ChatGPT cannot access the user's physical ADB/USB device directly. Prepared local Python read-only ADB inventory/copy tool `Find-DollarFix-Recordings.py` in conversation attachment; tested on synthetic file listings and Android shell fallback: 5/5 passed. This tool has NOT been run against the actual phone.
- Searches app-owned external storage recursively, captures actual device-local timestamps and identifies likely diagnostic log/recording files. Optional `--pull` copies up to 40 matching files, 100 MiB max, while excluding vendor .so/.GGP and photos. Doesn't request ECU data, modify Android, root device or patch APK.
- Instructions saved to reverse/docs/PHONE_RECORDING_DISCOVERY_20261122.md; private output root: reverse/reports/Phone-recordings-20261121.
- Next: run from user's Windows with authorized ADB, review `DollarFix-recordings-2026-11-21-inventory.json`/`.md` and saved record files. If genuine QR_CommDelphi2 driver buffer at least 60 bytes is present, decode at offsets 56..59, verify actual Delphi branch F119/F11A and compare with OEM GGP description. Do not treat raw KWP bytes as driver-expanded buffer.

## Iteration 2026-11-22: actual 21-Nov diagnostic logs collected and analyzed

- User uploaded Phone-recordings-20261121.7z; extracted safely with libarchive in model environment. Found 4 on-device files copied (2 QIRUI_TY proprietary LAUNCH .dat, one OBD text .dat, one gdscan.ini) plus inventory JSON/Markdown. Inventory saw 893 files, 21 date matches, 7 candidates; there was an `adb find` warning, so survey may be incomplete.
- QIRUI native .dat byte lengths 23546 and 23642; each begins with ASCII `LAUNCH` and a high-entropy body (~7.93 bits/byte). Bytes 18..23474 (23457 bytes) are identical, 11-byte leading header common, final 64-byte suffix common, file length differs by 96 bytes. Possible two states of a related recording; codec and semantics NOT decoded.
- OBD text .dat confirms BT200 AT setup and app event DIAG_CONNECTED, subsequent device.con.fail; adapter control frames 55AA are NOT verified ECU KWP data. No live `76010020` or driver-expanded 60-byte buffer found in accessible plaintext.
- Checked libx431file.so's fi_checkfile: its expected magic at byte 0 is X9LS, **not** LAUNCH. Do not mistake lsx_rec_* reader for this .dat format.
- High-priority omitted plaintext candidate: ThinkDiag/temp/cloud_report_cache/..._QIRUI_TY.txt (2892 bytes); also FunctionMainMenu.txt (1589 bytes), dpu_downloadbin_information.txt (56 bytes), and prior-day QIRUI log (10522 bytes). User's next step: `adb pull` these files only, without ECU operations, for menu and trace context.
- Technical summary committed to reverse/docs/PHONE_RECORDINGS_20261121_FORENSIC_REVIEW.md; locally generated downloadable Markdown/JSON in conversation. Blocker: LAUNCH data not decoded and selected Delphi route not proven at runtime. No app or car modifications.

## Iteration 2026-11-22: 21-Nov real cloud report decodes and confirms Delphi II route

- Fixed previous malformed nested-array PowerShell adb pull issue; user supplied `DollarFix-session-extra.zip` with exactly four intended files (cloud_report.txt, FunctionMainMenu.txt, dpu_info.txt, QIRUI_previous.dat). No recursive root filesystem read in this corrected run.
- `cloud_report.txt` was a 2892-byte Base64 JSON string. Decoded safely offline to 2167-byte JSON with 3 report records. Redacted parser verified by 5 synthetic tests; output artifacts include a JSON and Markdown summary, plus downloadable source script.
- **Major gate resolved:** actual diagnostic path is QIRUI_TY V10.22 > Tiggo T11 family > ECM > Delphi System 2.0L/2.4L (4G63/4G64), name_id=fd050101, system_uid=0000f11a. This matches native OldProEnter F11A jump table to CheryDelphiII, earlier only statically inferred.
- Real saved data streams at 2026-11-21 18:51:20.879 UTC+3: 7601000F Engine speed 728 rpm; 76010013 O2 sensor 667 mV. Both IDs belong to the 18 original DataStreamId values, independently corroborating list analysis.
- No 76010020 datum in this selected two-element report; `mileage="0"` in vehicle metadata (unit MILES) is not an ECU odometer measurement. Report is not a full 18-entry selector dump or ECU protocol trace.
- `dpu_info.txt` has adapter downloadbin V23.04; `FunctionMainMenu.txt` only concerns reset operations; QIRUI_previous.dat is a 10522-byte LAUNCH binary log but no plaintext ECU response decoded.
- Public repo summary saved at reverse/docs/DELPHI2_SESSION_CLOUD_REPORT_20261122.md with redacted output and no identifiers. Remaining gate: obtain a confirmed internal 60-byte driver-buffer sample or a validated trace mapping from LAUNCH log; no on-device patch or ECU write.

## Iteration 2026-11-22: real LAUNCH .dat forensic block structure and codec-locator

- User requested to continue decrypting actual 20-21 Nov LAUNCH diagnostic logs already extracted privately. Re-opened exact originals (both 21 Nov native logs and one 20 Nov log), independently confirmed SHA256 (see reverse/docs/LAUNCH_DAT_BLOCK_FORENSICS_20261122.md).
- Each .dat starts ASCII LAUNCH; LE bytes[6:10]=104; byte[10]=2; bytes[18:122] identical 104-byte opaque header; last 64 bytes identical. Candidate body range [122:L-64) length divisible by 8 and by 16 in all three, but real record boundaries and codec are still unverified.
- Compared 8-byte aligned body blocks: 21Nov log A vs B: 2919/2920 exact blocks, one final compared block changed, second file 12 blocks (+96 bytes) longer. 20Nov vs either 21Nov: 897/1292 aligned blocks equal, 57 common runs >=4 blocks, longest 175 blocks (1400 bytes) at offset 1786. No plaintext ECU answer was decoded.
- Independent external Launch patent CN108227579A describes encrypted file header + block-oriented diagnostic data and a Hill-cipher example; this is a **hypothesis/search direction only**, NOT proof that these files use that algorithm. Public x431-to-csv supports .x431/.dzx, not demonstrated for this LAUNCH .dat container.
- Created private downloadable bundle LAUNCH_T11_forensic_tools_20261122.zip with offline compare analyzer (5/5 tests), bounded marker-scanner find_launch_codec.py (3/3 tests), and verified MD/JSON reports. Scanner is to run on the existing original saved base.apk/arm64 split plus optional decompiled Java/Smali; it does not execute native code or transmit data.
- Document committed at reverse/docs/LAUNCH_DAT_BLOCK_FORENSICS_20261122.md. Next: run codec locator on Windows backup and upload candidate report; inspect the exact native writer/reader before attempting any decoding. Original phone/ECU/APKs/GGP untouched.

## Iteration 2026-11-22: static LAUNCH codec candidate triage from real APK

- User supplied `launch-codec-candidates.json` (scan of 9 members in base.apk, 24 ARM64 split members, and 238 JADX Java files under com/cnlaunch only). Verified base APK SHA256 prefix 139ba36... and split SHA256 703bf7....
- Strongest string match: classes7.dex score 130 (`SpecificDiagnoseLog`, `DiagnoseLog`, generic `LAUNCH`). Other DEX candidates mostly generic diagnose/log/vendor name hits; ARM64 `libLICENSE.so` only generic LAUNCH, no identified LAUNCH .dat codec. Exact log magic `LAUNCH 68 00 00 00 02` was not found in the scanned code.
- JADX candidates: `DiagnoseLogUtil.java` contains `DATA_TYPE_DSTRING=1`, `DATA_TYPE_D4STRING=2`, `mLogBuffer`; `DiagnoseDataSrc.java` calls `CToJavaImplements.recordSendDataDiagnoseLog` and `recordReciveDataDiagnoseLog`; `DiagnoseService.java` owns mDiagnoseLogPath and collection state; SQLite/offline feedback managers index/package the logs. None proves decoding or ECU byte contents yet.
- Added report reverse/docs/LAUNCH_CODEC_LOCATOR_REVIEW_20261122.md. Locally created offline, three-test-verified collector `collect_launch_codec_sources.py`, provided as private chat attachment (not yet committed to GitHub), to bundle up to 16 relevant JADX Java source files from the **entire** decompilation root while avoiding APK and user logs.
- Next action: user runs collector on Windows and shares compact Java evidence ZIP, especially DiagnoseLogUtil, CToJavaImplements, DiagnoseDataSrc. Trace record writer/header conversion and native method boundary; then test read-only decoder against existing LAUNCH .dat. No APK/ECU alterations.

## Iteration 2026-11-22: LAUNCH .dat codec fully reconstructed and 3 real diagnostic logs decoded

- User supplied `LAUNCH-codec-Java-20261122_140234.zip` containing 13 scored JADX source files. Inspected `com/cnlaunch/diagnosemodule/utils/DiagnoseLogUtil.java` and `CToJavaImplements.java`. **Proven codec:** SafeMatrix 8x8 fixed matrix cipher modulo 256, with `encryptionContent`, `decryptionContent` and writeToOutputStream. The real format is LAUNCH(6)+headerlen LE32(104)+encrypted 8-byte-block stream. Decode header V02.01 and 8-byte time, length-prefixed records, 0 terminator, four-field footer and u32 footer length.
- Implemented and exercised two private Python tools `decode_launch_dat.py`, `launch_t11_report.py`, with `test_launch_t11_decoder.py` synthetic unittest suite **6/6 PASSED**. Provided user privately as `LAUNCH_T11_decoder_verified_20261122.zip`. Avoid publishing vendor matrix values in public GitHub; no source app binaries/logs in repo.
- Fully decoded 3 original private QIRUI_TY .dat files; each file has correct CHERY/Tiggo footer, valid timestamps, exact re-encryption roundtrip and zero parsing errors: 21Nov 487 records (UI129+128, adapter115+115), second 21Nov 491 (UI131+130, adapter115+115), 20Nov 235 (UI52+51, adapter66+66). The first 487 entries across the 21Nov log copies are exactly equal; four completion events added in longer copy.
- Three 21Nov UI 0x11 selection messages each list precisely **18** previously recovered DataStreamId entries; no `76010020`. UI 0x12 values: O2 sensor 76010013=92 mV at 18:52:08.649, =623 mV at 18:52:24.362; at 18:53:06.467 engine speed 7601000F=714 rpm and O2=468 mV. These belong to a different interval than cloud report's 728rpm/667mV at 18:51:20.879.
- Log UI includes `Clear Fault Memory` and historical `Clear Code Successfully` on 21Nov at approximately 18:51:55, and two ICM communication error dialogs near 18:55. Decoder did not send any commands. Type3/4 `55 AA` frames are adapter envelopes, not proven raw KWP or 60-byte driver expanded data.
- Detailed non-sensitive report committed to reverse/docs/LAUNCH_DAT_CODEC_VERIFIED_20261122.md. **Remaining gate:** prove native mapping from 55AA response to QR_CommDelphi2 driver buffer[56..59] / actual ECU service, validate any 19th stream's effect on requests; avoid install/patch or odometer writes until offline verification.

## Iteration 2026-11-22: VERIFIED OEM Mile meter field from real KWP 21 01 data

- **Breakthrough**: recovered full 83-byte KWP `80 F1 11 4E 61 01 ...` response inside three original 21-Nov QIRUI LAUNCH events. Native BT200 wrapper `55AA F8F0` and 2701/6701 transport validated via Java `CToJavaImplements.WriteAndRead` / `DiagnoseDataSrc.sendReceive`. All 115 paired send/receive envelopes satisfy expected length, direction, seq/cmd matching and XOR checksum; the embedded 3 KWP responses pass additive checksum.
- Three distinct same-session readings at 18:52:08.645, 18:52:24.362, 18:53:06.467 UTC+03 have `KWP[56:60]=00 0F 42 40`. Unmodified OEM GGP `76010020` formula `(uint32_BE)/10` gives **100000.0 km**, stable across the three replies. The 21-Nov Specific and Diagnose logs duplicate these same readings; not six independent readings.
- **Cross-calibration fixes buffer mapping, no assumptions**: OEM RPM formula `[30][31]U` yields 714 rpm at 18:53:06; O2 formula `[37]4.42*` yields 92, 623, 468 mV at three timestamps, matching four actually logged UI display values. First two raw RPM bytes give 738/756 but were not displayed. The GGP names/formulas (7601000F, 76010013, 76010020), original library checksum and parser SHA were independently verified.
- 20-Nov log passes 66 matched envelope pairs and outer checksums, no qualifying KWP 21 01 response. 21-Nov 115 matched envelope pairs (113 2701, 1 2505, 1 2117). All input logs remain untouched; no BT200 or vehicle interaction.
- Verified user-private deliverable T11_KWP_ODOMETER_VERIFIED_20261122.zip: offline parser verify_t11_kwp_odometer.py, 9 synthetic unit tests PASS, existing private LAUNCH and GGP readers, and redacted JSON/Markdown evidence. No original private files / vendor matrices committed to public repo.
- Documented in reverse/docs/DELPHI2_KWP21_ODO_VERIFIED_20261122.md. The previously blocking **KWP-to-60-byte-buffer mapping and live Mile meter field are resolved**. Remaining: verify whether 100000.0 km represents actual dashboard mileage versus ECU default/placeholder; design a reversible display-only 19th selector entry with traffic-invariance checks before deploying any modified app. Do not alter ECU mileage or transmit any write commands.
