#!/usr/bin/env python3
"""Copy ONLY the two needed AArch64 parser libraries out of a saved split APK.

This script never modifies the APK, the phone, or native libraries.
No application installation and no library code execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

EXPECTED_SPLIT_SHA256 = "703bf7b3222b3a43958aef2b5e963a2494408b7d201cf423293d810c17a663e9"
REQUIRED = ("libSEARCHID.so", "libx431file.so")


def digest(file: Path) -> str:
    h = hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def export(apk: Path, output: Path) -> dict:
    if not apk.is_file():
        raise FileNotFoundError(str(apk))
    original_sha = digest(apk)
    if original_sha != EXPECTED_SPLIT_SHA256:
        raise ValueError("Unexpected ARM64 APK SHA-256: " + original_sha)
    found = {}
    with zipfile.ZipFile(apk, "r") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if name.startswith("lib/arm64-v8a/") and name.rsplit("/", 1)[-1] in REQUIRED:
                base = name.rsplit("/", 1)[-1]
                if base in found:
                    raise ValueError("Ambiguous duplicate library: " + base)
                found[base] = info
        missing = set(REQUIRED).difference(found)
        if missing:
            available = sorted(
                item.filename for item in z.infolist()
                if item.filename.endswith(".so")
            )[:50]
            raise ValueError("Missing required libraries {}. First available: {}".format(
                sorted(missing), available))
        output.mkdir(parents=True, exist_ok=True)
        extracted = []
        for name in REQUIRED:
            info = found[name]
            dest = output / name
            if dest.exists():
                raise FileExistsError(
                    "Output already exists; preserve prior evidence, use a new output directory: " +
                    str(dest))
            content = z.read(info)
            dest.write_bytes(content)
            extracted.append({
                "name": name,
                "zip_member": info.filename,
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            })
    result = {
        "analysis_type": "static-extraction-from-original-split",
        "source_apk": str(apk.resolve()),
        "source_apk_sha256": original_sha,
        "libraries": extracted,
    }
    (output / "parser-extract-manifest.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    if digest(apk) != original_sha:
        raise RuntimeError("Source split APK changed during extraction!")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apk", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    data = export(args.apk, args.out)
    print("PASS: ARM64 original split unchanged")
    for lib in data["libraries"]:
        print("{}: {} bytes SHA256={}".format(
            lib["name"], lib["size_bytes"], lib["sha256"]))
    print("Manifest: " + str(args.out / "parser-extract-manifest.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
