# QIRUI CHERY_OLD_RU.GGP byte comparison — 2026-11-22

Source: user-uploaded `ggp-diff.json` and `ggp-diff.md` generated locally from
`QIRUI-installed-20261122_123943/V10.22`. The exact binary files were
not included in the upload and are not present in this repository.

## Exact findings

- Current and backup are each 3,420,296 bytes.
- Current SHA-256: `be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1`.
- `.T11ODO.BAK` SHA-256: `ac4d52ee5d7275066dd5df7f09f6f01532688c6d0d689914d46bbea36899890d`.
- Exactly **three bytes differ**, in **two ranges**; 3,420,293 bytes match.

| Absolute offset (decimal) | Hex offset | Current | .T11ODO.BAK |
|---:|---|---|---|
| 982385 | `0x0EFD71` | `7B` | `7A` |
| 982386 | `0x0EFD72` | `76` | `E7` |
| 3224885 | `0x313535` | `E8` | `74` |

Local 8-byte contexts containing the modified bytes:

- Current: `7B 76 04 2A E8 B9 CE 9F`; backup: `7A E7 04 2A E8 B9 CE 9F`.
- Current: `E8 D0 43 64 92 B7 1E BD`; backup: `74 D0 43 64 92 B7 1E BD`.

Adjacent entries in both contexts also have apparent eight-byte stride,
but the **record format is unknown**. Do not infer whether the changed bytes
represent values, offsets, flags, table indexes, encryption or checksums.

## Identifier search

The comparison report found no literal occurrence of `76010020` in
ASCII, UTF-16LE, either suggested hex-byte ordering, 32-bit decimal-word
big-/little-endian, or `Mile meter` ASCII in either binary.
Absence of those literals does not prove the record or parameter is absent.

## Next work

Obtain privately (not via public GitHub) the exact three files:

- `V10.22/CHERY_OLD_RU.GGP`
- `V10.22/CHERY_OLD_RU.GGP.T11ODO.BAK`
- `V10.22/libCHERY_OLD.so`

Reconfirm those hashes, inspect GGP header/section layout and ELF exports
and internal GGP reader behavior. Seek a verified mapping of the hidden
parameter to the OEM JSON menu and only then propose an isolated, read-only
UI change. Preserve unmodified app installation, never modify ECU mileage
or licensing mechanisms.
