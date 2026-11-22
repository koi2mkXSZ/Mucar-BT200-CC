# Repository instructions for Codex and other agents

Two workstreams: independent MUCAR BT200 Android client and evidence-based reverse engineering of the user's original DollarFix APK.

- Each claim about DollarFix must include direct evidence: original file hash, decompiled path/method or native address/offset.
- Use REA MCP dynamically when connected, record provider failures. A configuration registration does NOT prove an analysis happened.
- Use JADX for DEX, Apktool for resources/smali, REA/Ghidra for supported native ELF. Differentiate fact, inference and unknown.
- Preserve original APK and QIRUI unchanged. Use minimal reproducible patches and rollback.
- Never bypass license checks, DRM, signature or authentication. Report blockers.
- Read-only ECU diagnostics. No odometer writing, EEPROM writing, coding or destructive commands.
- Public repo: never commit proprietary APK/DEX/.so/.GGP, decompiled sources, device identifiers, raw logs, license files, private certificates or signing keys. Commit only authored tools, sanitized findings and tests.
- After every iteration update TODO.md: completed work, tests, blockers and next concrete steps.
- A rebuilt APK signed using a different certificate cannot be installed as an in-place update without handling signing compatibility and user data backups.
