# Codex / REA project instructions

Repository: Mucar-BT200-CC. Main goal: independent read-only Android diagnostics for MUCAR BT200 and evidence-based improvement of the locally installed DollarFix APK.

## Mandatory workflow

1. Read this file, `reverse/dollarfix/README.md`, and `reverse/dollarfix/TODO.md` before each reverse-engineering iteration.
2. Update `reverse/dollarfix/TODO.md` after EVERY iteration: achieved, evidence, checks, blockers, next executable task.
3. Cite evidence with original file SHA-256, path, class/method/signature or ELF address and function, and capture/log offsets as appropriate.
4. Keep original proprietary APK, QIRUI packages, diagnostics logs, serial numbers, license files, extracted native libraries and signing keys inside ignored `reverse/dollarfix/private/` or `reverse/dollarfix/output/`; NEVER commit them to public GitHub.
5. Never describe static hypotheses as observed runtime facts. Separate *observed*, *inferred*, and *unverified*.
6. No tampering with activation, licensing, certificate pinning, authentication, or security checks. Do not implement odometer writing, EEPROM programming, mileage modification or other write services. Focus on display/read-only interoperability.
7. Do not modify the original APK in place. Record hashes; produce a separate candidate; provide rollback.
8. Never claim APK installed, tested on vehicle, or a CI build passed without its exact evidence.
9. Android application tests and offline reverse-engineering tests must remain independent of unavailable vehicle/BT200 hardware.

## REA/Codex

On the user's Windows workstation, REA is an MCP server accessed by local Codex; it is NOT implicitly connected to this ChatGPT conversation. Inspect available tool schemas at runtime. Prefer `inspect_android_package`, `search_android_classes`, `inspect_android_class`, `inspect_android_method`, `trace_android_references`, `inspect_android_jni_bindings`, `decode_android_resources`, `inspect_apk_signature`; use Ghidra/REA tools for AArch64 ELF evidence.

Before patching: trace Android UI -> diagnosis SDK -> native driver -> GGP/XDSDATA classification -> active Delphi data stream ID list. Read `reverse/dollarfix/CODEX_PROMPT.md`.
