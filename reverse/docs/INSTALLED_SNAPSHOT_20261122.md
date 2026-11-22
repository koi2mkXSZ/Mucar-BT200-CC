# Installed DollarFix APK snapshot — 2026-11-22

Source of these facts: successful local ADB backup output supplied by the user. SHA-256 values are taken from that output and have **not been independently recalculated by ChatGPT** (phone filesystem is not connected to this session).

- Original package: `com.dnd.dollarfix.df51`
- Collection time (local): `2026-11-22 11:27:39`
- Relative storage: `reverse/input/DollarFix-installed-20261122_112739/`
- APK count: **4** (base + arm64-v8a + Russian resource + xxhdpi resource)
- Total bytes: **193,198,473** (sum of four reported sizes)

| APK | Size (bytes) | SHA-256 |
|---|---:|---|
| `base.apk` | 174,392,566 | `139ba36fb5a0d12f53494bfefdf1a7224ebb864d07d97b91a1d2aee8f6cccb23` |
| `split_config.arm64_v8a.apk` | 17,201,289 | `703bf7b3222b3a43958aef2b5e963a2494408b7d201cf423293d810c17a663e9` |
| `split_config.ru.apk` | 950,681 | `ba17c25d4dde2866fa619dd52634cc84209dd30f136d9ffd0db96ea97aed66bf` |
| `split_config.xxhdpi.apk` | 653,937 | `9cce89b27cd96b24034ec875e4a618ff967c66b53a809cae0e0e11d16da95aca` |

Full bundle ZIP SHA-256 (reported): `51eafa7a2606ee83072163e94c4b19f12f2e16ec7bc79e75ec251b87eb7d574b`.

## Important implications

- Earlier research used a different, much smaller APK (~77 MB). Do not assume patch offsets, classes, resources, signatures or protocol implementations match this current 174 MB base APK.
- A full reverse engineering investigation must inventory the ARM64 split as well as the base. APK resource splits can carry strings, density assets and layouts that affect UI reconstruction.
- Do not treat `split_config.arm64_v8a.apk` as a whole standalone app; it is part of one installed split APK set.
- Verify all four SHA-256 values against the local saved files before starting JADX/REA, and verify they are unchanged afterward.
- Preserve all four unmodified APKs, the manifest, and user data. Modified APK installation/signing must be planned separately; avoid reinstalling until compatibility is established.

## Next run

Use the script `scripts/Analyze-DollarFix-Snapshot.ps1` from the repository checkout, pointing `-ProjectRoot` to the parent project folder. It verifies the backup manifest and generates separate reports for each APK before invoking installed JADX, Apktool, REA and Codex.
