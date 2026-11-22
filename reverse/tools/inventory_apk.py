#!/usr/bin/env python3
"""Static, read-only inventory of an APK (or QIRUI ZIP), using Python stdlib.

The script never runs the app, decompiles code or publishes extracted binaries.
Any native-library extraction requires an explicit local output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import sys
import zipfile

TAG_BYTES = {
    "bluetooth_socket": b"BluetoothSocket",
    "bluetooth_gatt": b"BluetoothGatt",
    "bluetooth_le_scanner": b"BluetoothLeScanner",
    "bluetooth_adapter": b"BluetoothAdapter",
    "bluetooth_device": b"BluetoothDevice",
    "rfcomm": b"createRfcommSocket",
    "service_uuid": b"UUID",
    "dpu": b"DPU",
    "diagnose_log": b"DiagnoseLogUtil",
    "launch": b"com.cnlaunch",
    "thinkdiag": b"ThinkDiag",
    "searchid": b"SearchIdOpenFile",
    "data_stream": b"DataStream",
    "delphi": b"Delphi",
    "safe_matrix": b"SafeMatrix",
    "ggp": b"GGP",
    "native_load": b"loadLibrary",
}

ELF_ARCH = {3: "x86", 40: "ARM", 62: "x86_64", 183: "AArch64"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            buf = stream.read(1024 * 1024)
            if not buf:
                return digest.hexdigest()
            digest.update(buf)


def elf_metadata(data: bytes) -> dict | None:
    if len(data) < 20 or data[:4] != b"\x7fELF":
        return None
    endian = "<" if data[5] == 1 else ">" if data[5] == 2 else None
    if endian is None:
        return {"valid_elf_header": False}
    machine = struct.unpack_from(endian + "H", data, 18)[0]
    return {
        "valid_elf_header": True,
        "class": {1: "ELF32", 2: "ELF64"}.get(data[4], "unknown"),
        "machine": machine,
        "architecture": ELF_ARCH.get(machine, "other"),
    }


def is_native(name: str) -> bool:
    return name.lower().endswith(".so")


def scan_bytes(data: bytes, filename: str, max_hits: int = 12) -> list[dict]:
    """Record exact token + offset only, never contextual raw strings/secrets."""
    lowered = data.lower()
    matches = []
    for label, raw_token in TAG_BYTES.items():
        start = 0
        for _ in range(max_hits):
            pos = lowered.find(raw_token.lower(), start)
            if pos < 0:
                break
            matches.append({"tag": label, "entry": filename, "offset": pos})
            start = pos + len(raw_token)
    return matches


def inspect(archive: Path, extract_native: Path | None = None) -> dict:
    max_entry_bytes = 128 * 1024 * 1024
    sha256 = sha256_file(archive)
    result = {
        "source_filename": archive.name,
        "size_bytes": archive.stat().st_size,
        "sha256": sha256,
        "method": "stdlib zipfile inventory (no execution or decompilation)",
        "dex": [],
        "native": [],
        "entries": [],
        "tags": [],
        "warnings": [],
        "has_android_manifest": False,
        "certificate_entries": [],
    }

    with zipfile.ZipFile(archive) as zf:
        for item in sorted(zf.infolist(), key=lambda x: x.filename):
            name = item.filename
            if item.is_dir():
                continue
            entry = {
                "name": name,
                "size_bytes": item.file_size,
                "compressed_bytes": item.compress_size,
                "crc32": f"{item.CRC:08x}",
            }
            result["entries"].append(entry)
            if name == "AndroidManifest.xml":
                result["has_android_manifest"] = True
            if name.upper().startswith("META-INF/") and name.upper().endswith(
                (".RSA", ".DSA", ".EC", ".SF", ".MF")
            ):
                result["certificate_entries"].append(name)
            if item.file_size > max_entry_bytes:
                result["warnings"].append(
                    f"Skipped content inspection of oversized archive member: {name}"
                )
                continue

            if name.lower().endswith(".dex") or is_native(name):
                with zf.open(item) as handle:
                    data = handle.read()
                digest = hashlib.sha256(data).hexdigest()
                entry["sha256"] = digest
                result["tags"].extend(scan_bytes(data, name))

                if name.lower().endswith(".dex"):
                    result["dex"].append({"path": name, "size_bytes": len(data), "sha256": digest})

                if is_native(name):
                    record = {"path": name, "size_bytes": len(data), "sha256": digest}
                    record.update(elf_metadata(data) or {"valid_elf_header": False})
                    result["native"].append(record)
                    if extract_native is not None:
                        original = PurePosixPath(name)
                        if original.is_absolute() or ".." in original.parts:
                            raise ValueError(f"Unsafe archive path: {name}")
                        target = extract_native.joinpath(*original.parts)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)

    result["entry_count"] = len(result["entries"])
    result["dex_count"] = len(result["dex"])
    result["native_count"] = len(result["native"])
    result["tags"].sort(key=lambda x: (x["entry"], x["offset"], x["tag"]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path, help="Original APK or QIRUI ZIP file")
    parser.add_argument("--output", type=Path, required=True, help="Local JSON report")
    parser.add_argument("--extract-native", type=Path, help="Local extraction of .so files")
    args = parser.parse_args()
    if not args.apk.is_file():
        parser.error(f"No input file: {args.apk}")
    if not zipfile.is_zipfile(args.apk):
        parser.error(f"Not a valid ZIP-based APK/archive: {args.apk}")

    evidence = inspect(args.apk, args.extract_native)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "original_sha256": evidence["sha256"],
        "entries": evidence["entry_count"],
        "dex": evidence["dex_count"],
        "native": evidence["native_count"],
        "tag_hits": len(evidence["tags"]),
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
