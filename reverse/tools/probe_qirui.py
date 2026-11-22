#!/usr/bin/env python3
"""Read-only binary inventory and literal search of a locally backed-up QIRUI diagnostic pack.

No ECU communication, APK modifications, decompression, code execution or native library loading.
The byte patterns are candidate references only; the GGP container format is not decoded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

PATTERNS = {
    "ODO_ID_ASCII": b"76010020",
    "ODO_ID_UTF16LE": "76010020".encode("utf-16le"),
    "ODO_ID_UTF16BE": "76010020".encode("utf-16be"),
    "ODO_ID_RAW_HEX": bytes.fromhex("76 01 00 20"),
    "ODO_ID_RAW_LE": bytes.fromhex("20 00 01 76"),
    "MILE_METER_ASCII": b"Mile meter",
    "MILE_METER_UTF16LE": "Mile meter".encode("utf-16le"),
    "CHERY_OLD_ASCII": b"CHERY_OLD",
    "DELPHI_ASCII": b"Delphi",
}
CHUNK_SIZE = 1024 * 1024
MAX_HITS_PER_PATTERN = 12
MAX_FILES = 40000


def scan_file(path: Path) -> dict:
    result = {"bytes": 0, "sha256": "", "hits": []}
    digest = hashlib.sha256()
    overlap = max(len(v) for v in PATTERNS.values()) - 1
    tail = b""
    offset = 0
    counts = {key: 0 for key in PATTERNS}
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            block = tail + chunk
            block_start = offset - len(tail)
            for name, pattern in PATTERNS.items():
                start = 0
                while True:
                    hit = block.find(pattern, start)
                    if hit < 0:
                        break
                    start = hit + 1
                    # Suppress a match fully contained in the prior overlap.
                    if hit + len(pattern) <= len(tail):
                        continue
                    counts[name] += 1
                    if counts[name] <= MAX_HITS_PER_PATTERN:
                        absolute = block_start + hit
                        result["hits"].append({
                            "pattern": name,
                            "offset": absolute,
                            "bytes_hex": pattern.hex(),
                        })
            offset += len(chunk)
            tail = block[-overlap:] if overlap else b""
    result["bytes"] = offset
    result["sha256"] = digest.hexdigest()
    result["match_counts"] = {k: v for k, v in counts.items() if v}
    result["hits"].sort(key=lambda item: (item["offset"], item["pattern"]))
    return result


def probe(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError("QIRUI package directory does not exist")
    root = root.resolve()
    entries = []
    skipped_symlinks = 0
    for path in root.rglob("*"):
        if path.is_symlink():
            skipped_symlinks += 1
            continue
        if path.is_file():
            entries.append(path)
            if len(entries) > MAX_FILES:
                raise ValueError("Too many files; narrow --root to QIRUI_TY/V10.22")
    entries.sort(key=lambda p: p.relative_to(root).as_posix())
    data = {
        "analysis_type": "read-only-literal-binary-probe",
        "source_root": str(root),
        "format_decoded": False,
        "caution": "Binary/ASCII matches are not proof of GGP parsing or runtime visibility",
        "file_count": len(entries),
        "skipped_symlinks": skipped_symlinks,
        "files": [],
        "files_with_hits": 0,
        "extensions": {},
    }
    for path in entries:
        rel = path.relative_to(root).as_posix()
        ext = path.suffix.lower() or "(none)"
        data["extensions"][ext] = data["extensions"].get(ext, 0) + 1
        item = {"relative_path": rel, **scan_file(path)}
        data["files"].append(item)
        if item["hits"]:
            data["files_with_hits"] += 1
    data["extensions"] = dict(sorted(data["extensions"].items()))
    return data


def to_markdown(data: dict) -> str:
    t = chr(96)
    lines = [
        "# QIRUI diagnostic package — read-only binary probe", "",
        "This report lists **literal byte matches**, not decoded GGP records or ECU values.",
        "An ID can be compressed/encoded and not appear verbatim.",
        "",
        "Files: {}; files with matches: {}; skipped symlinks: {}.".format(
            data["file_count"], data["files_with_hits"], data["skipped_symlinks"]),
        "",
        "## File extensions", "",
    ]
    for ext, num in data["extensions"].items():
        lines.append("- {}: {}".format(t + ext + t, num))
    lines.extend(["", "## Files", ""])
    for item in data["files"]:
        lines.append("- {} — {} bytes; SHA-256 {}".format(
            t + item["relative_path"] + t, item["bytes"], t + item["sha256"] + t))
        for hit in item["hits"]:
            lines.append("  - {} at offset {} (literal {})".format(
                hit["pattern"], hit["offset"], hit["bytes_hex"]))
    lines.extend([
        "",
        "Next: independently verify format layout and whether the literal ID",
        "is a selectable OEM data-stream item; never infer any write capability.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True, help="Local QIRUI_TY/V10.22 directory")
    ap.add_argument("--json", type=Path, required=True)
    ap.add_argument("--markdown", type=Path, required=True)
    args = ap.parse_args()
    result = probe(args.root)
    if not result["file_count"]:
        ap.error("No files found beneath --root")
    for path, data in (
        (args.json, json.dumps(result, indent=2, ensure_ascii=False)),
        (args.markdown, to_markdown(result)),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
    print("PASS: {} QIRUI files hashed; {} files contain candidate literals".format(
        result["file_count"], result["files_with_hits"]))
    print("Evidence: " + str(args.markdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
