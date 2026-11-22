# DollarFix / QIRUI V10.22 — REA + Codex reverse engineering

## Exact target

- Android package: `com.dnd.dollarfix.df51`
- Prior research sample basename: `usDf_51Release-v1.3.0-25_03_21-com.doolarfix.bbs-release.apk`
- QIRUI module: `QIRUI_TY/V10.22`, including `CHERY_OLD_RU.GGP` and `libCHERY_OLD.so`
- Vehicle: Chery Tiggo T11 2.4L, Delphi ECM 2.0L/2.4L (4G63/4G64)
- Desired behavior: display an already-readable ECU odometer value in the stock Delphi Data Stream UI, without altering odometer data, activation, permissions, or other vehicle behavior.

## Previously established findings (must be revalidated against input hashes)

1. Real diagnosis sends KWP `21 01`, ECU address `0x11`, tester `0xF1`; response begins `61 01`.
2. The four odometer bytes `00 0F 42 40` decoded as big-endian unsigned `1,000,000 × 0.1 = 100000.0 km`.
3. The stock `CHERY_OLD_RU.GGP` contains hidden label/unit `76010020 = Mile meter / Km` and a valid odometer expression in its formula section.
4. The previous size-preserving experimental GGP pointer substitution `76010019 → 76010020` did **not** change the visible UI; `76010019` was absent from the selected 18-item Data Stream list.
5. Consequently, modifying the label/formula record alone is insufficient. Need to locate the actual Data Stream membership/classification logic or UI selection from native `GeneralMain`/`GeneralStreamCalc` and `XDSDATA.GAG`.
6. Candidate native symbols/addresses from previous analysis: `CheryDelphiII @ 0x13f3f0`, `GeneralMain @ 0x28da24`, `GeneralStreamCalc @ 0x28e868`; Delphi system identifier `0x80fc`. These addresses are build-specific and MUST be checked against the matching `.so` digest before use.

## Work products

- `tools/inventory_apk.py`: ZIP/DEX/ELF and characteristic-strings inventory without executing the APK.
- `tools/inspect_ggp.py`: structural GGP section inventory and validation, not a decoder.
- `tools/compare_apks.py`: explicit before/after ZIP member diff to catch unintended modifications.
- `tools/Collect-DollarFix.ps1`: Windows copy/hash of the actual authorized analysis inputs.
- `CODEX_PROMPT.md`: concrete REA/Codex investigation and patch acceptance contract.
- `TODO.md`: durable investigation status.

## First local invocation (PowerShell 5.1+)

```powershell
.\reverse\dollarfix\tools\Collect-DollarFix.ps1 -ApkPath 'C:\path\to\DollarFix.apk' -QiruiZipPath 'C:\path\to\DollarFix_QIRUI_FULL.zip'
python reverse\dollarfix\tools\inventory_apk.py reverse\dollarfix\private\DollarFix.apk -o reverse\dollarfix\output\apk-inventory.json
python reverse\dollarfix\tools\inspect_ggp.py reverse\dollarfix\private\QIRUI_FULL.zip -o reverse\dollarfix\output\ggp-structure.json
```

Then start local Codex with REA MCP configured; follow `CODEX_PROMPT.md`. Commit only analysis scripts, sanitized reports and independently written patch source. Do not commit the proprietary APK, GGP, license or keys.

### Critical limitation
This repository does not contain the APK or native QIRUI files. Creating these scripts is NOT equivalent to performing a full decompilation or delivering a working modified APK. Those require the original bytes on the analysis host, evidence-based patch location, rebuilt/re-signed package and on-device verification.
