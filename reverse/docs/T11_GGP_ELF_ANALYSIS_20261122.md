# DollarFix T11 — verified binary GGP + ELF analysis (2026-11-22)

Source: privately uploaded `DollarFix-T11-GGP-20261122_124621.zip`, inspected byte-for-byte locally.
No proprietary binary is committed to the repository; the user's installed APK/phone were not modified.

## SHA-256 verified

| File | Bytes | SHA-256 |
|---|---:|---|
| `CHERY_OLD_RU.GGP` | 3420296 | `be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1` |
| `CHERY_OLD_RU.GGP.T11ODO.BAK` | 3420296 | `ac4d52ee5d7275066dd5df7f09f6f01532688c6d0d689914d46bbea36899890d` |
| `libCHERY_OLD.so` | 3296304 | `74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79` |

Both GGPs begin with four-byte magic `47 47 50 00` (`GGP\0`). Their binary schema is still unknown.

## Exact changed bytes

| Offset decimal | Offset hex | Active GGP | .BAK |
|---:|---|---|---|
| 982385 | `0x0EFD71` | `7B` | `7A` |
| 982386 | `0x0EFD72` | `76` | `E7` |
| 3224885 | `0x313535` | `E8` | `74` |

These are the only three different bytes across 3,420,296-byte files.
Each altered locus lies in a repeating 8-byte sequence:

- At 982385 the 8-byte record (active) is `7b 76 04 2a e8 b9 ce 9f`; backup `7a e7 04 2a e8 b9 ce 9f`.
- At 3224884 the record (active) is `bd e8 d0 43 64 92 b7 1e`; backup `bd 74 d0 43 64 92 b7 1e`.
- In both neighborhoods the sixth byte increments by one across nine consecutive records (8 of 8 neighbor pairs). This is a local structural observation, NOT proof of which field means ID, hash, pointer, checksum or availability.

## Native ELF facts

- ELF64, AArch64, little-endian, SHA-1 GNU Build-ID `5cf17ddd4dc2fac7e798a9f6ae58f980852336cb`.
- Exported function `CheryDelphiII` RVA `0x13F3F0`; direct call at `0x13F470` to `GeneralMain@plt`.
- `QR_CommDelphi2` RVA `0x13F4D4` directly calls `SendRecvKwp@plt` multiple times and `QR_InitialDelphi2@plt` at `0x13F5C4`.
- `QR_InitialDelphi2` RVA `0x13F6A4`; `GeneralMain` RVA `0x28DA24`; `GeneralStreamCalc` RVA `0x28E868`.
- In `GeneralStreamCalc`, direct `getdata@plt` calls at `0x28EA50`, `0x28ED4C`, `0x28EDB4`.
- Exported callback-pointer symbols include `SearchIdOpenFile`, `fseekGGP`, `GetGAGOffsetFromGGP`, `GetGAGSizeFromGGP`, `ShowDataStream`, and `ShowStreamSelect`.

These exact calls do not prove which KWP service, GGP record, or screen is active for the vehicle under study.
No `76010020` byte sequence was found using the earlier limited literal/word representations; the indexed/encrypted representation remains an open question.

## Next step

Extract two GGP reading libraries from the saved original ARM64 split using
`reverse/tools/extract_ggp_parser_libs.py`:

- `libSEARCHID.so` — seek exported `ggp_Open`, `IdSearch`, and GGP index/record decoding.
- `libx431file.so` — seek external file read / record support.

The extraction script verifies the known 17,201,289-byte original ARM64 split SHA-256 before writing a separate research copy, and verifies the split again afterward.
Proceed with read-only static analysis; do not patch GGP, modify ECU mileage, send write commands, alter license mechanisms, or reinstall the original app.
