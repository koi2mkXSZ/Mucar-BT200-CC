# Chery Tiggo T11 Delphi II: reversible offline-only 19th Data Stream selector (2026-11-22)

## Scope and evidence

The original, user-supplied **QIRUI V10.22** `libCHERY_OLD.so` (ARM64 ELF; SHA-256 `74e49060a363b47c5e6dde21b9c881ca2ddcdf8e251e70ffe399b6061e075b79`) was modified **only in a local duplicate**, not the device.

Independent evidence already confirms the live vehicle's selected `F11A` route to `CheryDelphiII`, the original 18-element `DataStreamId` list, and `76010020`'s existing GGP name `Mile meter` / `Km` plus its original [56..59] formula. From the previously archived session, three distinct `KWP 21 01` ECU responses contain `00 0F 42 40`, yielding 100000.0 km for that **ECM field**. It is NOT yet established that this is true instrument-panel mileage; the exact round number may be a firmware placeholder.

## Exact in-place AArch64 patch

ELF `.text` address equals file offset in this *pinned build*. The `DataStreamId` BSS symbol at `0x36DE1C` exports **800 bytes**, capacity 200 32-bit entries; there is room for one extra 19th entry. The adjacent `iDataStreamItem` is a separate four-byte BSS symbol at `0x36DE18`.

| ELF offset | Original instruction | Patched instruction | Before bytes -> After bytes (LE) |
|---|---|---|---|
| `0x13F898` | `b.ne 0x13F9B0` | `b.ne 0x13F9B4` | `c1080054` → `e1080054` |
| `0x13F92C` | `mov w11, #18` | `mov w11, #19` | `4b028052` → `6b028052` |
| `0x13F9AC` | `b 0x13F9B4` | `add w8, w13, #31` | `02000014` → `a87d0011` |
| `0x13F9B0` | `orr w19, wzr, #1` | `str w8, [x12,#72]` | `f3030032` → `884900b9` |

Reason this does not lose a failure branch: `w19=1` has **already been set** at `0x13F778` before the conditional at `0x13F898`; redirecting it directly to the unmodified epilogue at `0x13F9B4` preserves the failure code. The success path clears `w19` at `0x13F9A0`, completes the original nine `stp` writes at `0x13F9A8`, then computes `76010001 + 0x1F = 76010020` and writes `DataStreamId[18]`.

## Offline validation

- Patched SHA-256: `b63f69be799fda8e2bce301d877772c871442474b6172056b37a6cff4858d295`.
- Original and patched byte length: **3,296,304**, ELF program/section layout and Build ID bytes unchanged.
- **Four changed instructions / eight actual differing bytes**; all other bytes, including `QR_CommDelphi2`, `GeneralMain`, `GeneralStreamCalc`, `GetStreamCmdFromLib`, unchanged.
- Bounded ARM64 initializer reconstruction: all 18 old IDs in original order plus only `76010020` at index 18.
- Branch predecessor checks, 19 vs 200 capacity check and restoring the original file **byte-for-byte**, reproducing its original full SHA.
- Local Python unittest **9/9 PASS**; tests repeated from an extracted deliverable ZIP *without requiring the original vendor library*, since SHA-pinned reversal is independently verified.
- LLVM objdump confirmed instruction mnemonics and branch destinations at all changed sites.
- One separately created privacy-safe CSV reuses three **already recorded** 21-Nov KWP responses. It is an offline display preview, not new vehicle traffic.

## Artifacts

A private conversation download named `T11_DelphiII_MileMeter_19_OFFLINE_PATCH_20261122.zip` contains a checksum-pinned `patch_chery_delphi2_mile_meter.py` (CLI `apply / verify / restore`), nine offline tests, JSON manifest, Markdown report, offline historical CSV, and the **modified local copy** `libCHERY_OLD.T11_MILE_METER_OFFLINE_TEST.so`. **No original or modified proprietary ELF is committed to this GitHub repository.**

## Critical limits / next gate

**THIS IS NOT YET AN ANDROID-VERIFIED OR VEHICLE-VERIFIED PATCH.** No APK rebuild/re-signing, Android installation, active trace comparison or ECU operation was performed. Static preservation of native transport code does not prove unchanged runtime request count, response timing, behavior upon selecting the additional ID, Android signatures, or library loader acceptance. Those require a separate controlled test with a restorable app snapshot and explicit user approval. Do not attempt odometer writes, firmware modifications, license bypass, or changes to the currently installed original.
