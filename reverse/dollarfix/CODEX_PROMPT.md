# Copy into local Codex on the Windows REA host

You are engineering a reproducible read-only interop patch for the user's locally installed DollarFix APK. Repository: Mucar-BT200-CC. Do not invent outcomes. Read AGENTS.md, reverse/dollarfix/README.md, reverse/dollarfix/TODO.md first.

Existing local toolchain was previously validated as Codex MCP + REA 6.8.0 with Ghidra, JADX, Apktool, JDK and ADB. Verify **current** tool availability; do not assume a past validation guarantees current state. Use the advertised tool signatures rather than guessing JSON schemas.

Input paths: reverse/dollarfix/private/DollarFix.apk and private/QIRUI_FULL.zip (or a caller-approved local equivalent). If missing, first ask whether the authorized phone with installed DollarFix is connected over ADB. With that device, use REA list_adb_devices then pull_adb_package (read-only acquisition of all split APKs) for package com.dnd.dollarfix.df51, preserving every original APK and SHA256. If the QIRUI archive is unavailable, use previously approved local backup; do not manufacture missing bytes. If not available, stop binary-specific analysis and report exact missing files; do not download unofficial/proprietary APK copies.

## Required evidence-first work

1. Run REA inspect_android_package on DollarFix.apk. Save the file SHA256, manifest, original signing cert fingerprint, DEX and ELF inventory, package and declared Bluetooth permissions. Check provider health with rea doctor --provider jadx --json if REA reports an unavailable JADX provider.
2. Search classes, inspect classes and selected methods, trace references around:
   - com.cnlaunch.diagnosemodule.utils.DiagnoseLogUtil;
   - BluetoothAdapter, BluetoothGatt, BluetoothSocket, RFCOMM, BLE/GATT UUIDs;
   - Launch DPU transport, ThinkDiag/BT200, diagnose messages, `27 01` and `67 01`;
   - loadLibrary/JNI registration and native communication libraries.
3. Inspect_android_jni_bindings for observed Java/native boundaries. Follow each verified AArch64 target into Ghidra using the REA native tools; save exact ELF SHA and RVA/evidence.
4. In the native QIRUI module, trace `CheryDelphiII` entry, `GeneralMain`, `GeneralStreamCalc`, `XDSDATA.GAG`, Data Stream UI membership and callback code. Previous addresses `0x13f3f0`, `0x28da24`, `0x28e868` are hypotheses until hashes match.
5. Revalidate the GGP label `76010020`, formula, and active classification/list matching Delphi system ID `0x80fc`. Explicitly account for failed `76010019` redirect experiment; do NOT repeat that unsuccessful patch.
6. Design the smallest reversible patch to show existing read-only Mile meter / Km in the Delphi Data Stream list while preserving all existing entries. Prefer a data-only patch if validated; use APK smali/resource changes only if necessary. No license, signature, subscription, activation, auth bypass, odometer writes or control-service changes.
7. Build candidate from untouched original plus a recorded patch manifest, re-sign with a dedicated local **test** key, and verify via Android SDK apksigner verify --verbose --print-certs (REA inspect_apk_signature reads signatures and digest consistency but does not independently establish full cryptographic/platform verification). Re-signing changes Android signature identity and may break app data/update compatibility: test on spare profile/device and preserve the original installation/backups. No auto-uninstall of original.
8. Compare original/candidate with compare_apks.py and report all modified members. Verify no unexpected classes/libs/config edited.
9. Test without car first: unit, resource, launch and recorded KWP replay; then with authorized phone/BT200: install, Tiggo -> ECM Delphi -> Data Stream, 19th ODO item, stable km value, no regression in 18 existing readings. Produce rollback procedure.
10. Update TODO.md after every step with evidence IDs, SHA, source/method and next unresolved hypothesis. Place only sanitized findings into the public repository.

Required outputs: `ARCHITECTURE.md`, `BLUETOOTH_TRACE.md`, `DATASTREAM_MEMBERSHIP.md`, `PATCH_MANIFEST.json`, `VERIFICATION.md`, and a repeatable local patch script (only after evidence is sufficient).

Do not assert that JADX/smali/Ghidra output is complete when decompilation or reflection/dynamic loading leaves gaps. No guessing UUIDs, CRCs, offsets, PID lists or packet meanings.
