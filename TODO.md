# Mucar-BT200-CC TODO / continuity

## Completed

- Stage 1: Android/Kotlin skeleton, CI debug build, Delphi T11 KWP frame and odometer vector.
- Stage 2 groundwork: decoded DPU request/response transaction model and replay harness.
- Historical T11 capture: positive KWP 21 01 -> 61 01, odometer raw 00 0F 42 40 -> 100000.0 km.
- CHERY_OLD_RU.GGP has the odometer identifier 76010020; earlier EGR descriptor redirect failed to surface the hidden item.
- ELM327/KWP OSS architecture and licensing audit.
- Windows REA + Codex static-analysis runner and documented investigation tasks.
- Read-only APK/ELF inventory scanner and synthetic regression tests.
- Исправлена ошибка поиска adb.exe в скрипте резервного копирования: дополнительные пути и установка официальных Google Platform-Tools по явному ключу -InstallAdb; резервное копирование на телефоне ещё не подтверждено.
- Added scripts/Backup-DollarFix-Apk.ps1 to preserve the currently installed phone APK set (base.apk plus split APKs), version metadata and SHA-256 under C:\REA\Project\DollarFix\reverse\input\; phone backup has NOT yet been executed in this ChatGPT environment.

## Not yet verified

- APK source bytes: the historic upload's metadata was found, but this session could not download original bytes.
- Real REA/Codex execution against DollarFix: local agents are not remotely exposed in this ChatGPT session.
- Bluetooth Classic/BLE choice, UUID, BT200 DPU framing and JNI call path.
- Delphi visible PID selection mechanism.
- Patched, rebuilt and signed APK, plus installation and on-vehicle test.

## Next concrete actions

1. On the connected Windows PC run scripts/Backup-DollarFix-Apk.ps1 against the installed com.dnd.dollarfix.df51 package; verify successful adb pulls and hashes.
2. Execute scripts/Start-DollarFix-REA.ps1 against the saved base.apk, optionally with QIRUI ZIP.
3. Trace Android Bluetooth -> JNI -> Launch DPU with file/method/offset evidence.
4. Trace Delphi Data Stream selection/classification to hidden ID 76010020.
5. Implement minimal read-only display patch after exact target hash and control flow are confirmed.
6. Build/sign/test independently; preserve original app installation/data and maintain a rollback.
7. Update TODO.md after every iteration.
