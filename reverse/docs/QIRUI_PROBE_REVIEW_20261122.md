# Installed QIRUI_TY V10.22 probe — 2026-11-22

Source: user-confirmed successful ADB read-only backup plus uploaded
qirui-probe.json and qirui-probe.md. Tool output represents literal
byte-pattern searching and SHA-256 hashing; the GGP binary format was
NOT decoded. No vehicle/ECU action was taken.

## Successful local capture

- The new ADB backup created locally is:
  C:\REA\Project\DollarFix\reverse\input\QIRUI-installed-20261122_123943.
- The user reported 79 pulled files, total 38,502,050 bytes.
- The uploaded probe refers to an EARLIER backup:
  QIRUI-installed-20261122_121203. That probe inventories 80 files,
  not 79, because the old probe included generated qirui-manifest.json
  (20,309 bytes): 38,502,050 + 20,309 = 38,522,359.
  The tool was corrected to skip that metadata.
- Before comparing copies, verify that the later local backup has the
  same hashes as the earlier report. Do not silently assume this.

## Reported binary files

| File under V10.22 | Bytes | SHA-256 |
|---|---:|---|
| CHERY_OLD_RU.GGP | 3,420,296 | be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1 |
| CHERY_OLD_RU.GGP.T11ODO.BAK | 3,420,296 | ac4d52ee5d7275066dd5df7f09f6f01532688c6d0d689914d46bbea36899890d |
| libCHERY_OLD.so | 3,296,304 | 74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79 |
| libCHERY_DIAGDSFUNC.so | 95,936 | 60e3b936199af35f25b1d6c310ed0ee03c77950b9de097643dba66430bd190cc |
| lib.cfg | 769 | 3bfc2b23c56de1eb66a4d67f4d6ad805297ed6c66f3632e7e5eeebe4a29e0d5b |

- libCHERY_OLD.so contains 24 ASCII Delphi hits and 3 ASCII
  CHERY_OLD hits according to the literal scan.
- DPUSYS.INI and DPUSYS_BAK.INI each contain two ASCII Delphi hits.
- lib.cfg contains an ASCII CHERY_OLD hit.
- 27 .so libraries and 4 .ggp files were listed by extension.
  The .T11ODO.BAK copy is counted under .bak.

## Uncertainties

- The GGPs have identical sizes but DIFFERENT SHA-256. Do not infer
  which one is vendor-original or what changed from the .BAK suffix.
- No literal 76010020 or Mile meter was found in the earlier probe's
  tested ASCII/UTF-16 and raw-byte representations. This does not
  establish the item's absence from GGP records or the runtime stream.
- The binary GGP format, OEM data-stream JSON and the menu selection
  mask have not been causally linked for 76010020 yet.

## Next step

Run reverse/tools/compare_chery_ggp.py on the user's latest snapshot to
produce read-only byte-difference offsets, changed-region sizes,
bounded hex previews and hash verification. Review actual changes before
attempting any patch, installation or vehicle connection. Preserve the
original files and avoid ECU writes, tampering with mileage or license paths.
