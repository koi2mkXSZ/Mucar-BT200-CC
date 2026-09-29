# Mucar-BT200-CC

Open-source Android diagnostic client research project for the MUCAR BT200.

## Stage 1
- Android/Kotlin application skeleton
- GitHub Actions debug APK build
- BT200 transport abstraction
- KWP2000 frame helpers
- Chery Tiggo T11 / Delphi 2.0L/2.4L ECU profile
- Read-only PID decoding, including odometer research

> Status: transport framing is under reverse engineering. No ECU write/coding/EEPROM operations are implemented.

## Confirmed research baseline
For the tested Chery Tiggo T11 2.4 (Delphi 4G63/4G64), the captured diagnostic session uses ECU address `0x11`, tester address `0xF1`, KWP service `21 01`, and a positive response beginning with `61 01`.

The odometer value is represented by four bytes and decoded as an unsigned big-endian value multiplied by 0.1 km.

## Build
GitHub Actions builds `app-debug.apk` on every push to `main` and on pull requests.

Local build:
```bash
gradle :app:assembleDebug
```

## Safety
The current project is intentionally read-only. Clear-DTC, actuator tests, coding, EEPROM access and odometer writing are outside Stage 1.
