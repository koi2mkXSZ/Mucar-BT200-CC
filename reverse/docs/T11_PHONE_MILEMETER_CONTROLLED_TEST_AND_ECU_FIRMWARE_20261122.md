# T11 Delphi II: controlled phone test of `76010020` and ECU BIN research gate — 2026-11-22

## Scope and status

**User requested direct Android test** of the already SHA-pinned local 19-item patch, and stated that an original ECU image was placed at `C:\REA\Project\DollarFix\EC0116U9 4G64_MAFN_EURO-3-Full Tiggo 2.4.bin` on the user's Windows PC.

ChatGPT does **not** have USB/ADB access to this physical phone or the Windows `C:` drive. It has **not** performed an actual Android test and **has not inspected the ROM bytes**. Do not claim Android load/UI success, transport invariance, ECU firmware architecture/offsets, or verified dash odometer.

## Verified inputs and candidate

- Original vendor `libCHERY_OLD.so` 3,296,304 bytes SHA256 `74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79`.
- Reversible offline **19-stream-ID** test library 3,296,304 bytes SHA256 `b63f69be799fda8e2bce301d877772c871442474b6172056b37a6cff4858d295`, appending `76010020` while preserving original 18. All other code bytes unchanged. Previous static 9/9 tests passed.
- Both accepted GGP snapshots include `76010020 — Mile meter — Km` with `(big-endian uint32 at KWP bytes 56..59)/10`: SHA256 `be351e06a59a715f9bac51a72c44b4e9db212fb8925e179dfd11d304c2ff77a1` or `ac4d52ee5d7275066dd5df7f09f6f01532688c6d0d689914d46bbea36899890d`.
- Real 21-Nov 2026 KWP `21 01` frames have `00 0F 42 40` at positions 56..59, corresponding to an **ECM diagnostic field 100000.0 km**. The round value could be a constant/placeholder and is **not** an independently verified odometer reading.

## Test apparatus, privately supplied

A ZIP named `T11_T11_MileMeter_Phone_ECU_Test_20261122.zip` contains the pinned patched `.so`, `Test-T11-MileMeter-Phone.ps1`, `Inspect-T11-ECU-Firmware.py`, a README, and previous patcher/tests. Source tools are present in the **chat attachment only**, not in this public repo; proprietary `.so` is not committed.

### Test runner `Test-T11-MileMeter-Phone.ps1`

Modes: `Inspect` (nonmutating ADB verification), `Test` (explicit temporary external .so replacement with backed-up file and automated finally rollback), `Restore` (independent emergency recovery from pinned backup). It targets only:

`/sdcard/Android/data/com.dnd.dollarfix.df51/files/DollarFix/ThinkDiag/<adapter>/64/DIAGNOSTIC/VEHICLES/QIRUI_TY/V10.22/libCHERY_OLD.so`.

Preflight fails closed unless the phone's library and GGP match pinned SHA256 hashes, the intended package is installed, ADB is authorized, and the patched `.so` itself matches the pinned hash. Backups are saved exclusively to `reverse/local-private/T11-milemeter-phone/` on Windows. Test forces the app to stop and then `adb push` to **one exact external app-owned file**, checks readback hash, instructs user to inspect **Data Stream only**, then in a `finally` block stops the app and restores the original, checking the full restored SHA256. It also attempts to copy the latest QIRUI logs for later trace comparison. No root, APK re-signing, app uninstall, ECU flash or write command.

**Unproven assumption:** Android DollarFix may actually load native libraries from a different private cache (or may overwrite the externally stored `.so` at launch). A successful ADB push *alone* does not prove the patch was loaded. If permission is denied, loader doesn't use file, or app performs an integrity check, abort and restore; no permission bypass or root procedure is authorized.

### PowerShell invocation

Download ZIP and extract to `C:\REA\Project\DollarFix\reverse\work\T11-MileMeter-19`. With explicit serial and adapter-folder IDs from user's own prior ADB run:

```powershell
$root='C:\REA\Project\DollarFix'
$test="$root\reverse\work\T11-MileMeter-19\Test-T11-MileMeter-Phone.ps1"
& $test -Mode Inspect -Serial '<device-serial>' -AdapterId '<adapter-folder>' -ProjectRoot $root
# Proceed only if PREFLIGHT PASS and ready to operate safely while vehicle parked
& $test -Mode Test -Serial '<device-serial>' -AdapterId '<adapter-folder>' -ProjectRoot $root
# If interrupted without successful rollback:
& $test -Mode Restore -Serial '<device-serial>' -AdapterId '<adapter-folder>' -ProjectRoot $root
```

### Test acceptance

1. The 19th row **Mile meter** actually appears in the live Delphi II ECM Data Stream list and uses OEM Km unit; previous 18 rows unchanged.
2. Selecting Mile meter yields a UI value; compare historical ECM 100000.0 km and actual instrument-panel mileage **without assuming equivalence**.
3. Collect and decode new 55AA/KWP log; compare service IDs and packet request rates with 21-Nov 2026 original baseline. No new write/clear/adaptation/programming operations. Any unexpected traffic invalidates a 'UI-only' claim.
4. Complete `Restore` and verify original exact SHA256 before further use.

## ECU firmware investigation (read-only)

Given Windows file (actual bytes NOT provided yet): `EC0116U9 4G64_MAFN_EURO-3-Full Tiggo 2.4.bin`. The private `Inspect-T11-ECU-Firmware.py` creates a new JSON with size, SHA256, whole-image and 4KiB entropy, file header/footer fingerprints, ASCII-string *offsets only*, and byte-pattern counts for ECU model labels, the KWP services `21 01`/`61 01`, and `00 0F 42 40` in both byte orders. Pattern hits may be data, compression artifacts or false positives and **must not be reported as a confirmed KWP service handler**.

Five firmware-scanner synthetic tests passed and previous nine patch tests passed (**14 total Python unit tests**). Phone PS1 was structurally checked but **could not be syntax-validated with PowerShell or executed with Android/ADB in this container**.

To advance beyond the manifest, user must privately upload the **actual BIN**. Only after reading and fingerprinting its contents can we infer architecture, memory map, KWP handler, constant/default mileage field, other supported safe read-only diagnostics, and calibration/protocol compatibility. No automatic firmware update, checksum patch, ECU security access or odometer changes are in scope.

## Rollback scope clarification

The PowerShell runner verifies and restores the exact **external** `.../V10.22/libCHERY_OLD.so` file by SHA256. It cannot prove that a possibly separate Android app-private executable/library cache has been refreshed; a cached patched library could persist after external restoration. Thus a byte-identical external restore is **not a guarantee of full application cache rollback**. If the app still displays a 19th entry after restoring the external library and reopening, stop and inspect loader/cache behavior; do not root or uninstall the app to force it.

User-side run is still pending. The latest private ZIP explicitly documents this caveat.
