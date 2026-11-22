# Codex + REA task: reproduce and extend DollarFix APK behavior

Goal: investigate the user's original DollarFix APK and prepare a minimal read-only modification that exposes the odometer value already observed in Chery Tiggo T11 Delphi 2.0/2.4 data.

## Inputs (local, not committed)

- reverse/input/DollarFix-original.apk
- reverse/input/DollarFix_QIRUI_FULL.zip (optional)
- reverse/reports/inventory.json
- reverse/work/jadx/ (JADX decompilation, if installed)
- reverse/work/apktool/ (Apktool extraction, if installed)
- reverse/reports/rea-doctor.json and rea-providers.json

If any tool/input is missing, record the limitation; never invent class names, addresses, BLE UUIDs, native function behavior or a completed patch.

## Phase A — identity and inventory

Hash original APK (SHA-256), list DEX and native libraries, certificate/signing schemes, manifest, app components, resources, obfuscation indicators. Do not execute the APK without explicit approval.

## Phase B — Android code

Use JADX to map app entrypoints, BluetoothDevice/BluetoothSocket/BluetoothGatt/scan APIs, callbacks, UUIDs, Launch/ThinkDiag DPU implementation, JNI declarations and DiagnoseLogUtil. Trace call hierarchy with precise paths and method names.

## Phase C — resources and UI

Use Apktool to map diagnostic menus, Delphi Data Stream item selection, localization, component ownership and JNI usage.

## Phase D — native

Inventory JNI exports/imports and ELF architectures. Use REA MCP/Ghidra when supported to link Android to native transport and QIRUI libCHERY_OLD.so, libSEARCHID.so. Verify exact binary SHA and offsets. Do not claim provider execution unless evidence exists.

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

Use available MCP tool schemas dynamically, confirm which providers actually respond, and cite REA evidence IDs in local reports if present.
Never infer tool success merely because an MCP config file exists. Record failures. Keep repository commits free of secrets and proprietary code.
