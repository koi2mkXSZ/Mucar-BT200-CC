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
