# T11 Mile meter: detached phone test — separate Stage and Restore

## Why

User cannot leave phone connected to a PC or keep PowerShell running while testing on the car. Existing `Test-T11-MileMeter-Phone-PS51-FIX.ps1 -Mode Test` waits for Enter during the entire test, making it unsuitable for this use case.

## Tested private tools (no real phone execution)

Prepared a **separate** `Test-T11-MileMeter-Detached-PS51.ps1`, provided to user as chat artifact `T11_MileMeter_Detached_Phone_Test_20261122.zip`. The original script and proprietary ELF are not changed/committed in GitHub. A 12-condition static source safety inspection and ZIP integrity check passed. **PowerShell 5.1 execution on Windows and testing on Android HAVE NOT been performed by ChatGPT.**

The script reuses previous fixed ADB error handling, SHA-pinned source/patch hashes and two accepted GGP hashes; modes are:

- `Inspect`: read-only ADB verification of exact original external SO and GGP. Must output **PREFLIGHT PASS**.
- `Stage -ConfirmStage`: create local persistent original backup under `reverse/local-private/T11-milemeter-phone/<serial>/<adapter>/original-libCHERY_OLD.so`, check SHA256, force-stop app, push patch only to `.../QIRUI_TY/V10.22/libCHERY_OLD.so`, pull back and check patched SHA256, persist `STAGE_STATUS.json`. **Return immediately, no Read-Host; user may close PC and disconnect USB.**
- `Restore`: independent later call on same Windows PC after returning home; validates original SHA, copies recent QIRUI logs if readable, stops app, pushes saved original to the same external target, pulls back and verifies source SHA, persists restore status.

Stage attempts immediate rollback in the event of **staging failure**, but after successful Stage there is **no automatic timer / on-phone rollback while disconnected**. Failed or interrupted Restore requires the user to reconnect and retry; the backup on PC must not be deleted. Users must not use other diagnostic functions while modified file remains staged. The external file may not be the actual library used by the app, and restoring it may not erase a separately cached private copy.

The script does not alter installed APK, license, ECU firmware, EEPROM, stored mileage, or diagnostic memory; do not perform Clear Codes/Coding/Programming/Adaptation or write actions during car test.

## User Windows commands

Place `Test-T11-MileMeter-Detached-PS51.ps1` in existing `C:\REA\Project\DollarFix\t11\phone-ecu-tools` and use:

```powershell
$root = 'C:\REA\Project\DollarFix'
$test = "$root\t11\phone-ecu-tools\Test-T11-MileMeter-Detached-PS51.ps1"
& $test -Mode Inspect -Serial 'ZY22LFT26X' -AdapterId '9TFD20111779' -ProjectRoot $root
# Only after PREFLIGHT PASS:
& $test -Mode Stage -ConfirmStage -Serial 'ZY22LFT26X' -AdapterId '9TFD20111779' -ProjectRoot $root
```

Close PowerShell; disconnect USB; at a parked car use DollarFix Data Stream only and capture Mile meter row/value/screenshot. Then return home, reconnect USB and run in a **new** shell:

```powershell
$root = 'C:\REA\Project\DollarFix'
$test = "$root\t11\phone-ecu-tools\Test-T11-MileMeter-Detached-PS51.ps1"
& $test -Mode Restore -Serial 'ZY22LFT26X' -AdapterId '9TFD20111779' -ProjectRoot $root
```

Never claim the temporary patch has been validated on an Android runtime until user supplies Inspect/Stage/Restore output and a screenshot or new decoded LAUNCH log.

## Other work

Separate user's original 128 KiB ECU BIN was only scanned **on the user's Windows** (SHA256 25496241a2e17c8495124748c008bb3e65a798754972e7853dd8e0cf8bf92758). Firmware contents not available to ChatGPT; this detached test does not touch firmware.
