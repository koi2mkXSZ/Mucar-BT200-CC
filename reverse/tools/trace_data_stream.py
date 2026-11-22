#!/usr/bin/env python3
"""Collect reference locations from local JADX/Apktool sources, without copying source code.

This is lexical evidence only. An identifier occurrence does not establish
runtime reachability, a Delphi ECU path, or availability of the GGP item.
The resulting reports contain filenames, line numbers and names only.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
from pathlib import Path
import sys

MARKERS = (
    "76010020", "PIDV", "toBasicDataStreamBean", "BasicDataStreamBean",
    "ELMDataViewUtil", "DataStreamScene", "JniX431File", "lsx_rec_readds",
    "SearchIdOpenFile", "GetGAGOffsetFromGGP", "GetGAGSizeFromGGP",
    "GeneralStreamCalc", "GeneralMain", "libCHERY_OLD", "CHERY_OLD",
    "QIRUI_TY", "DataStream", "dataStream", "DataStreamBean",
    "DiagnosisService", "DiagnoseService", "BluetoothManager", "SocketCall",
    "IdSearch", "SearchId", "XDSDATA", "GGP"
)
TEXT_EXTENSIONS = {".java", ".kt", ".smali", ".xml"}
MAX_FILE_BYTES = 4 * 1024 * 1024


def package_hint(filename: str) -> str:
    """These are filename-only hints, not verified subsystem classifications."""
    name = filename.replace("\\", "/").lower()
    if "/elm/" in name or "/elmdata" in name or "/elm_" in name:
        return "ELM_NAMING_HINT"
    if any(k in name for k in ("/chery/", "/qirui", "/cnlaunch/", "/x431/")):
        return "OEM_OR_X431_NAMING_HINT"
    if any(k in name for k in ("/thinkcar/", "/thinkdiag/", "/launch/")):
        return "VENDOR_SDK_NAMING_HINT"
    return "UNCLASSIFIED"


def trace(roots: list[Path], max_per_marker: int = 120) -> dict:
    counts = collections.Counter()
    occurrences = []
    by_file = collections.defaultdict(set)
    skipped = 0
    inspected = 0
    dedup = set()
    for root in roots:
        if not root.is_dir():
            continue
        for directory, subdirs, filenames in os.walk(root, followlinks=False):
            subdirs[:] = [name for name in subdirs if not name.startswith(".")]
            for name in filenames:
                path = Path(directory, name)
                if path.suffix.lower() not in TEXT_EXTENSIONS or path.is_symlink():
                    continue
                filename = str(path.resolve())
                if filename in dedup:
                    continue
                dedup.add(filename)
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        skipped += 1
                        continue
                    content = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    skipped += 1
                    continue
                inspected += 1
                method = ""
                smali = path.suffix.lower() == ".smali"
                for number, line in enumerate(content.splitlines(), 1):
                    trimmed = line.strip()
                    if smali and trimmed.startswith(".method "):
                        method = trimmed[len(".method "):]
                    elif smali and trimmed.startswith(".end method"):
                        method = ""
                    for marker in MARKERS:
                        if marker not in line:
                            continue
                        counts[marker] += 1
                        by_file[filename].add(marker)
                        if counts[marker] <= max_per_marker:
                            occurrences.append({
                                "marker": marker,
                                "filename": filename,
                                "line": number,
                                "method_anchor": method if smali else None,
                                "path_hint": package_hint(filename),
                            })
    related = [
        {
            "filename": filename,
            "markers": sorted(markers),
            "path_hint": package_hint(filename),
        }
        for filename, markers in by_file.items()
        if len(markers) >= 2
    ]
    related.sort(key=lambda item: (-len(item["markers"]), item["filename"]))
    occurrences.sort(key=lambda item: (item["marker"], item["filename"], item["line"]))
    return {
        "analysis_type": "lexical-references-only",
        "not_a_call_graph": True,
        "files_inspected": inspected,
        "files_skipped": skipped,
        "marker_counts": dict(sorted(counts.items())),
        "occurrences": occurrences,
        "cooccurrence_files": related[:200],
        "cooccurrence_total": len(related),
        "occurrences_per_marker_limit": max_per_marker,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# DollarFix reference locator", "",
        "**Caution:** lexical matches and filename-based hints are NOT evidence",
        "that ELM code is used for the proprietary Chery Delphi diagnostic path.", "",
        f"Scanned files: {report['files_inspected']}; skipped: {report['files_skipped']}.",
        "", "| Marker | Count |", "|---|---:|",
    ]
    for key, value in report["marker_counts"].items():
        lines.append(f"| \`{key}\` | {value} |")
    lines += ["", "## Files containing two or more markers", ""]
    for record in report["cooccurrence_files"][:100]:
        lines.append("- \`{}\` — {} ({})".format(
            record["filename"], ", ".join(record["markers"]), record["path_hint"]
        ))
    lines += ["", "Next: verify the real caller chain and item type in REA/Smali before patching.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dirs", nargs="+", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    if not any(root.is_dir() for root in args.source_dirs):
        parser.error("No source directories found")
    report = trace(args.source_dirs)
    for target, payload in (
        (args.json, json.dumps(report, indent=2, ensure_ascii=False)),
        (args.markdown, to_markdown(report)),
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
    print(f"OK: {report['files_inspected']} files inspected")
    print(f"Source-reference report: {args.markdown}")
    print(f"Structured reference map: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
