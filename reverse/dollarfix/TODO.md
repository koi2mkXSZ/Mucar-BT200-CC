# DollarFix Reverse Engineering — durable TODO

## Current stage: REA/Codex analysis harness prepared; real APK still required in the active analysis environment

### Established from earlier work
- [x] Confirmed vehicle ECU communication with KWP `21 01`, positive `61 01`.
- [x] Odometer four-byte formula and 100000.0 km known test vector.
- [x] Located stock hidden ODO descriptor `76010020` in prior GGP examination.
- [x] Tested label/formula pointer redirect from invisible EGR item; it failed to surface ODO in Data Stream.
- [x] Created independent Android project and transport-level research in this repository.

### Completed in current iteration
- [x] Reviewed available REA tool documentation and previous validated local REA/Codex toolchain report.
- [x] Located historical APK/QIRUI attachment metadata but the file backing bytes were not available to this session for analysis.
- [x] Added a reproducible, strictly read-only RE workbench, artifact inventory, GGP structural checker, archive diff, unit tests, and Codex instructions.

### Pending / blockers
- [ ] Obtain byte-accessible source APK and V10.22 GGP/ELF into ignored local `private/` directory (historical archive metadata alone is insufficient).
- [ ] Run actual REA `inspect_android_package` and record source SHA-256, package/manifest, DEX, JNI and signature evidence.
- [ ] Map Android Bluetooth UI/service/JNI to BT200 DPU (DPU transaction envelopes `SEQ 27 01` / `SEQ 67 01` seen previously).
- [ ] Trace Delphi Data Stream membership: `AddDataStreamItem`, `AddDataStreamClassificationSDefDSID`, `GeneralMain`, `XDSDATA.GAG`, system ID `0x80fc`.
- [ ] Identify reversible read-only patch with explicit original-vs-patched bytes/record and successful offline tests.
- [ ] Build and re-sign separately, diff all APK members, test install/launch/ECU read/ODO display/rollback on device.
- [ ] Only after demonstrated on-device success: release sanitized patch script and installation instructions, not proprietary APK.

### Acceptance
- Original and patched APK hashes and signing identities recorded.
- Existing 18 Delphi items retained; add odometer as separate visible item (target 19) with correct `Km` and conversion.
- On-car readout agrees with raw KWP `21 01`; no write commands.
- Unrelated vehicle functions unchanged (smoke-test), rollback works.
- Report references actual traces and code addresses, not predictions.
