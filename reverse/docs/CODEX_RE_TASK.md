# Codex + REA task: reproduce and extend DollarFix APK behavior

Goal: investigate the user's original DollarFix APK and prepare a minimal read-only modification that exposes the odometer value already observed in Chery Tiggo T11 Delphi 2.0/2.4 data.

## Inputs (local, not committed)

- PRIMARY original snapshot: `C:\REA\Project\DollarFix\reverse\input\DollarFix-installed-20261122_112739\` (base.apk + three split APKs; preserve all four byte-for-byte).
- Snapshot manifest and SHA-256 verification are in the corresponding snapshot directory and reports subdirectory.
- The obsolete legacy path `reverse/input/DollarFix-original.apk` is NOT REQUIRED. Do not call the original APK absent merely because that legacy path is missing.
- Optional: QIRUI_TY V10.22 from the phone's DollarFix external data, to be copied via `scripts/Backup-DollarFix-Qirui.ps1` if still present. It is not expected inside `split_config.arm64_v8a.apk`.
- `C:\REA\Project\DollarFix\reverse\work\DollarFix-installed-20261122_112739\`: JADX/Apktool/native output.
- `C:\REA\Project\DollarFix\reverse\reports\DollarFix-installed-20261122_112739\`: REA evidence, per-tool logs, snapshot verification.

If any tool/input is missing, record the limitation; never invent class names, addresses, BLE UUIDs, native function behavior or a completed patch.

## Phase A — identity and inventory

Hash original APK (SHA-256), list DEX and native libraries, certificate/signing schemes, manifest, app components, resources, obfuscation indicators. Do not execute the APK without explicit approval.

## Phase B — Android code

Use JADX to map app entrypoints, BluetoothDevice/BluetoothSocket/BluetoothGatt/scan APIs, callbacks, UUIDs, Launch/ThinkDiag DPU implementation, JNI declarations and DiagnoseLogUtil. Trace call hierarchy with precise paths and method names.

## Phase C — resources and UI

Use Apktool to map diagnostic menus, Delphi Data Stream item selection, localization, component ownership and JNI usage.

## Phase D — native

Inventory JNI exports/imports and ELF architectures. Use REA MCP/Ghidra when supported to link Android to native transport and QIRUI libCHERY_OLD.so, libSEARCHID.so. Verify exact binary SHA and offsets. Do not claim provider execution unless evidence exists.

## Current evidence versus verification gaps

- A previous Codex summary reports the apparent UI path `PIDV` selection → `PIDV.toBasicDataStreamBean()` → `BasicDataStreamBean.id` → data-stream UI.
- That summary proposes matching identifier `76010020` for the read-only odometer display.
- Treat these as **hypotheses pending exact file/method evidence** from the authored reports, disassembly and APK bytes.
- The current saved base APK SHA-256 is `139ba36fb5a0d12f53494bfefdf1a7224ebb864d07d97b91a1d2aee8f6cccb23`. Always verify local actual input against manifest before any patch.
- JADX finished with exit code 3 in one investigation. Read the specific `jadx-base.log` first. Apktool succeeded for all four installed files, and some REA static calls succeeded even though `rea doctor` reports optional engines missing.
- `libCHERY_OLD.so` was not found in the installed ARM64 split; do not infer absence from the dynamically downloaded QIRUI package.
- None of the four authored detailed reports are available in the remote GitHub repository until separately reviewed and pushed by the local user or explicitly uploaded; do not invent evidence from report filenames.

## Phase E — GGP

Reproduce list/formula parsing. Explain why the previously tried EGR descriptor pointer redirect did NOT surface the odometer. Identify the true visible classification/selection path for 76010020.

## Phase F — patch

Prepare the smallest demonstrably effective read-only patch and exact target SHA. Provide source diff, unit test, build, signature compatibility, rollback and test result. Do not bypass license checks, anti-tamper, DRM or authentication, and do not implement ECU odometer writing or destructive services.

## Expected artifacts (original authored documents)

- reverse/docs/APK_ARCHITECTURE.md
- reverse/docs/BLUETOOTH_DPU.md
- reverse/docs/DELPHI_DATA_STREAM.md
- reverse/docs/PATCH_PROPOSAL.md
- TODO.md updated with verification and blockers.
- Patch source/tests only in the repo; proprietary binaries stay in ignored local reverse/input, reverse/work, reverse/output, reverse/reports.

## REA and Codex

Use available MCP tool schemas dynamically, confirm which providers actually respond, and cite REA evidence IDs in local reports if present. Collect the concrete JADX/Apktool evidence showing the full PIDV selection path and determine whether the actual id type is string/int before suggesting a smali hook.
Never infer tool success merely because an MCP config file exists. Record failures. Keep repository commits free of secrets and proprietary code.
