# DollarFix: search for saved Android diagnostic recording from 2026-11-21

## Context

The user reported a recording on the phone on 2026-11-21 and asked to inspect it directly. The ChatGPT container cannot access the user's physically attached USB Android phone. The check must be run on the user's Windows computer over authorized read-only ADB.

Known package: `com.dnd.dollarfix.df51`; known device serial from previous local commands: `ZY22LFT26X`; QIRUI package previously copied from `/sdcard/Android/data/com.dnd.dollarfix.df51/files/DollarFix/ThinkDiag/9TFD20111779/64/DIAGNOSTIC/VEHICLES/QIRUI_TY/V10.22`.

## Safe search

- Search app-owned external `/sdcard/Android/data/com.dnd.dollarfix.df51/files` and `/cache`, `/sdcard/Android/media/com.dnd.dollarfix.df51`, `/sdcard/DollarFix`, and named DollarFix/ThinkDiag directories under Download/Documents.
- Inventory file modification epoch, byte length and full path with `adb shell find` + `stat`; convert with the device-provided UTC offset (`adb shell date +%z`). The specific target date is `2026-11-21` on the device.
- Search candidates by diagnostic/recording filename, directory and file extension; do not classify `libCHERY_OLD.so` or `CHERY_OLD_RU.GGP` as a recorded session merely because they reside in the diagnostic package.
- Display all date-matching candidates and recent record-like files on adjacent dates to catch files edited shortly before/after a session.
- A separately supplied local Python script `Find-DollarFix-Recordings.py` can optionally `adb pull` up to 40 record-like files, max 100 MiB total, skipping libraries/APKs/images. It was syntax-checked and passed five synthetic unit tests; the real phone scan has NOT been run by ChatGPT.
- Store results beneath `C:\REA\Project\DollarFix\reverse\reports\Phone-recordings-20261121`, a local research path, not public GitHub.

## PowerShell invocation

```powershell
$root = 'C:\REA\Project\DollarFix'
$adb = "$root\tools\android\platform-tools\adb.exe"
$out = "$root\reverse\reports\Phone-recordings-20261121"
& 'C:\Python314\python.exe' "$root\Find-DollarFix-Recordings.py" --adb $adb --serial ZY22LFT26X --date 2026-11-21 --out $out --pull
```

The Python file is a conversation deliverable and should be downloaded into the project root before running these commands. No ADB shell write, ECU request, root, or application patch is used.

## Success/failure interpretation

- If record-like files are returned, inspect their types and contents offline and look for an already-captured Delphi session and a driver-expanded >=60 byte buffer. Never apply GGP [56–59] positions directly to a raw KWP frame without verifying the driver mapping.
- If no files appear, do not conclude the session was not recorded. It may be in an app-private `/data/user/0/...` directory, a shared SQLite DB with different mtime, or an alternative Android location. The next step would be targeted directory discovery without deleting the app, rooting the device, or sending any ECU commands.
- Logs can contain VIN, adapter IDs and timestamps; share only relevant copies privately in chat, never commit them to the repository.
