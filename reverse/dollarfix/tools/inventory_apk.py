#!/usr/bin/env python3
"""Static, read-only APK inventory for private REA/Codex analysis."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile, BadZipFile

SCAN_LIMIT = 64 * 1024 * 1024
TOKENS = [
    b"BluetoothGatt", b"BluetoothSocket", b"BluetoothAdapter",
    b"BluetoothDevice", b"BluetoothLeScanner", b"BluetoothGattCharacteristic",
    b"createRfcommSocket", b"connectGatt", b"java/util/UUID", b"android/bluetooth",
    b"com.cnlaunch", b"ThinkDiag", b"Launch", b"DiagnoseLogUtil",
    b"JNI_OnLoad", b"RegisterNatives", b"SearchIdOpenFile", b"DPU",
    b"QIRUI_TY", b"CHERY_OLD_RU.GGP", b"XDSDATA.GAG",
]
CLASSES_RE = re.compile(r"^classes(?:[0-9]+)?\\.dex$")
SO_RE = re.compile(r"^lib/[^/]+/[^/]+\\.so$")

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def analyze(path):
    path = Path(path)
    report = {
        "schema": "dollarfix.apk-inventory.v1",
        "filename": path.name,
        "file_bytes": path.stat().st_size,
        "sha256": file_hash(path),
        "entries": [],
        "selected_code_hits": [],
        "summary": {},
    }
    counts = {"dex": 0, "native_so": 0, "other": 0}
    with ZipFile(path) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError("Corrupt member: " + corrupt)
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename
            is_dex = bool(CLASSES_RE.fullmatch(name))
            is_so = bool(SO_RE.fullmatch(name))
            kind = "dex" if is_dex else ("native_so" if is_so else "other")
            counts[kind] += 1
            record = {
                "path": name, "kind": kind,
                "size": info.file_size, "compressed_size": info.compress_size,
                "crc32": "%08x" % info.CRC,
            }
            report["entries"].append(record)
            if (is_dex or is_so) and info.file_size <= SCAN_LIMIT:
                data = archive.read(info)
                record["sha256"] = hashlib.sha256(data).hexdigest()
                hits = []
                low = data.lower()
                for token in TOKENS:
                    pos = low.find(token.lower())
                    if pos >= 0:
                        hits.append({"symbol": token.decode("ascii"), "offset": pos})
                if hits:
                    report["selected_code_hits"].append({"member": name, "hits": hits})
    report["summary"] = {
        "entry_count": len(report["entries"]),
        "dex_count": counts["dex"], "native_so_count": counts["native_so"],
        "other_count": counts["other"],
        "abis": sorted({e["path"].split("/")[1] for e in report["entries"] if e["kind"] == "native_so"}),
    }
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("apk", help="Existing APK path")
    p.add_argument("-o", "--output", help="Local JSON report path")
    args = p.parse_args()
    result = analyze(args.apk)
    data = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data + "\n", encoding="utf-8")
    print(json.dumps({"sha256": result["sha256"], "summary": result["summary"],
                      "code_hit_files": len(result["selected_code_hits"])}, ensure_ascii=False))

if __name__ == "__main__":
    main()
