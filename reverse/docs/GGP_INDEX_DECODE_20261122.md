# DollarFix T11: decoded GGP section directory and odometer index (2026-11-22)

Source: user's privately supplied original 3-file GGP/ELF bundle plus saved ARM64 parser library bundle, examined **offline**. No ECU connection, app install, patch, or license modification.

## Input integrity

| File | SHA-256 |
|---|---|
| `libSEARCHID.so` | `cfd6c96802f75055415f4917d27d8e909ed2af4046d587574eeb5500637264d3` |
| `libx431file.so` | `feb41d0b922abdc0fe12747fd6c5e2531fd8af125bc674935adad43bc4ed13e5` |
| Active `CHERY_OLD_RU.GGP` | `be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1` |
| `CHERY_OLD_RU.GGP.T11ODO.BAK` | `ac4d52ee5d7275066dd5df7f09f6f01532688c6d0d689914d46bbea36899890d` |

## Verified libSEARCHID.so parser behavior

- ELF64/AArch64. `IdSearch` RVA `0x38D0` uses binary search over fixed-width index entries, `EncryptNumber` RVA `0x5550` transforms search keys, `GagDecrypt` RVA `0x51D4` handles encoded values.
- `GetGAGOffsetFromGGP` RVA `0x43DC` and `GetGAGSizeFromGGP` RVA `0x4788` locate embedded GAG sections via the directory. `OpenFileIssueSearchID` RVA `0x4A80` initializes record/file-reader state.
- The GGP container begins with `GGP\0` and contains a 1093-byte header with 15 entries, each **72 bytes**. The section names are 32-byte encrypted strings (Rijndael 256-bit block / 256-bit key), followed by offset/size fields.
- Section-name decryption was independently reproduced and validated against all 15 human-readable GAG names. The decoder derives needed material from the verified **local** libSEARCHID.so; no key is committed to GitHub.

## Section bounds relevant to T11

| Section | Absolute offset | Byte size | Index count |
|---|---:|---:|---:|
| `DSTREAM_RU.GAG` | 981342 | 639500 | 15771 |
| `XDSDATA.GAG` | 3221425 | 11652 | 375 |

Both GAG indexes have four-byte transformed keys plus four-byte encoded **data pointers** (eight-byte records). The active-versus-backup difference lies in these pointer fields; the keys and actual payloads are unchanged.

## Decoded target IDs

| Section | ID | Current pointer, section-relative | Backup pointer |
|---|---|---:|---:|
| `DSTREAM_RU.GAG` | `76010019` | 133469 | 133324 |
| `DSTREAM_RU.GAG` | `76010020` | 133469 | 133469 |
| `XDSDATA.GAG` | `76010019` | 7082 | 6966 |
| `XDSDATA.GAG` | `76010020` | 7082 | 7082 |

- The index row for 76010019 is 51 in DSTREAM and 359 in XDSDATA. The original 76010020 has row 26 in DSTREAM and 374 in XDSDATA.
- Current 76010019 now aliases the existing 76010020 **in both** sections. It does not make 76010020 newly selectable in the OEM UI.
- Exactly three modified raw bytes implement those pointer redirects: GGP offsets 982385: `7A` to `7B`, 982386: `E7` to `76`, 3224885: `74` to `E8` when going from backup to current.

## Decoded payloads

`DSTREAM_RU.GAG`:

- 76010020 -> `Mile meter`, unit `Km` (in both active and backup).
- 76010019 -> active `Mile meter` / `Km`, backup `EGR position` / `%`.

`XDSDATA.GAG`:

- 76010020 -> `F1=[56]1677721.6*[57]6553.6*+[58]25.6*+[59]0.1*+` (in both active and backup).
- 76010019 -> active same odometer formula, backup `F2=[44]2.56/`.

The odometer equation is equivalent to `(A*2^24 + B*2^16 + C*2^8 + D)/10` for four **driver-positioned** bytes [56]..[59]; offline example `00 0F 42 40` -> 100000 km. This alone does **not** establish which KWP packets are sent, nor whether those positions contain the intended data during a live Delphi session.

## Implication for the original display-only goal

The earlier unsuccessful EGR substitution is fully explained at the GGP index level: it redirects 76010019 to a pre-existing 76010020 description and formula. If the vehicle-specific OEM menu excludes 76010019 or 76010020, changing index data pointers cannot cause a new UI list item to appear.

Next evidence: trace the **vehicle-specific OEM menu emission** in libCHERY_OLD.so / GGP menu records through the Android `DiagnoseUIDataBusiness.jsonUIDataStream` function. Distinguish `BasicDataStreamBean.id` string from numerical `Const_Text_Item` selection index. Verify actual response formatting via an existing *read-only* diagnostic trace or offline replay before proposing any modification. Do not change ECU mileage, ECU writes, app licensing, or original phone installation.
