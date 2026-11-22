#!/usr/bin/env python3
"""Read-only compare of two CHERY_OLD_RU.GGP variants.

Collects checksums, byte-level changed ranges, and bounded hex previews.
No binary patching, vehicle communication, GGP decoding, or uploads.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import sys

MAX_INPUT_BYTES = 64 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    total = len(data)
    counts = collections.Counter(data)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def _excerpt(data: bytes, offset: int, context: int = 24) -> dict:
    start = max(0, offset - context)
    end = min(len(data), offset + context)
    block = data[start:end]
    return {
        "offset_start": start,
        "offset_end_exclusive": end,
        "hex": block.hex(" "),
        "ascii": "".join(chr(ch) if 32 <= ch <= 126 else "." for ch in block),
    }


def compare(current: bytes, backup: bytes, merge_gap: int = 16) -> dict:
    if merge_gap < 0 or merge_gap > 1024:
        raise ValueError("merge_gap outside 0..1024")

    equal_prefix = 0
    for a, b in zip(current, backup):
        if a != b:
            break
        equal_prefix += 1

    common_length = min(len(current), len(backup))
    differing_count = 0
    range_count = 0
    first_ranges: list[dict] = []
    biggest_ranges: list[dict] = []
    active_start = None
    active_end = None
    active_differences = 0

    def push_range() -> None:
        nonlocal range_count
        if active_start is None:
            return
        range_count += 1
        region = {
            "offset_start": active_start,
            "offset_end_exclusive": active_end + 1,
            "window_bytes": active_end - active_start + 1,
            "differing_bytes": active_differences,
        }
        if len(first_ranges) < 24:
            first_ranges.append(region)
        biggest_ranges.append(region)
        biggest_ranges.sort(key=lambda r: (-r["differing_bytes"], r["offset_start"]))
        if len(biggest_ranges) > 16:
            biggest_ranges.pop()

    for index in range(common_length):
        if current[index] == backup[index]:
            continue
        differing_count += 1
        if active_start is None:
            active_start = index
            active_end = index
            active_differences = 1
        elif index - active_end - 1 <= merge_gap:
            active_end = index
            active_differences += 1
        else:
            push_range()
            active_start = index
            active_end = index
            active_differences = 1
    push_range()

    candidates = sorted({
        region["offset_start"] for region in first_ranges + biggest_ranges
    })
    previews = [
        {
            "difference_offset": start,
            "current": _excerpt(current, start),
            "backup": _excerpt(backup, start),
        }
        for start in candidates[:32]
    ]

    # Two possible interpretations of the identifier, for reconnaissance only:
    # literal ASCII digits; hex bytes; decimal integer represented as a word.
    numeric_id = 76010020
    patterns = {
        "ID_ASCII": b"76010020",
        "ID_UTF16LE": "76010020".encode("utf-16le"),
        "ID_HEX_BIG_ENDIAN": bytes.fromhex("76010020"),
        "ID_HEX_LITTLE_ENDIAN": bytes.fromhex("20000176"),
        "ID_DECIMAL_WORD_BIG_ENDIAN": numeric_id.to_bytes(4, "big"),
        "ID_DECIMAL_WORD_LITTLE_ENDIAN": numeric_id.to_bytes(4, "little"),
        "MILE_METER_ASCII": b"Mile meter",
    }
    pattern_hits = {}
    for name, pattern in patterns.items():
        original_positions = []
        backup_positions = []
        for blob, positions in ((current, original_positions), (backup, backup_positions)):
            index = blob.find(pattern)
            while index >= 0 and len(positions) < 12:
                positions.append(index)
                index = blob.find(pattern, index + 1)
        pattern_hits[name] = {
            "pattern_hex": pattern.hex(),
            "current_first_positions": original_positions,
            "backup_first_positions": backup_positions,
        }

    return {
        "analysis_type": "bytewise-comparison-only",
        "decoded_ggp": False,
        "current": {
            "bytes": len(current),
            "sha256": sha256(current),
            "entropy_bits_per_byte": round(entropy(current), 4),
        },
        "backup": {
            "bytes": len(backup),
            "sha256": sha256(backup),
            "entropy_bits_per_byte": round(entropy(backup), 4),
        },
        "same_size": len(current) == len(backup),
        "bytewise_equal": current == backup,
        "equal_prefix_bytes": equal_prefix,
        "bytes_in_common_span": common_length,
        "differing_bytes_in_common_span": differing_count,
        "trailing_bytes_after_common_span": abs(len(current) - len(backup)),
        "total_merged_ranges": range_count,
        "merge_gap_bytes": merge_gap,
        "first_merged_ranges": first_ranges,
        "largest_merged_ranges": biggest_ranges,
        "bounded_hex_previews": previews,
        "pattern_hits": pattern_hits,
        "conclusion_limit": "Different bytes do not identify which variant is original or prove an odometer filter.",
    }


def render_markdown(result: dict) -> str:
    t = chr(96)
    lines = [
        "# QIRUI CHERY_OLD_RU.GGP — read-only byte comparison",
        "",
        "This comparison does NOT determine which version is factory original.",
        "No GGP records were decoded and no files were modified.",
        "",
        "## File integrity", "",
        "| Version | Bytes | SHA-256 | Entropy (bits/byte) |",
        "|---|---:|---|---:|",
    ]
    for name in ("current", "backup"):
        item = result[name]
        lines.append("| {} | {} | {} | {} |".format(
            name, item["bytes"], t + item["sha256"] + t, item["entropy_bits_per_byte"]))
    lines += [
        "",
        "Equal files: **{}**; byte differences in common span: **{}**; merged regions: **{}**.".format(
            result["bytewise_equal"],
            result["differing_bytes_in_common_span"],
            result["total_merged_ranges"]
        ),
        "",
        "Equal prefix: {} bytes; trailing unmatched bytes: {}.".format(
            result["equal_prefix_bytes"], result["trailing_bytes_after_common_span"]
        ),
        "",
        "## First changed regions", "",
        "| First offset | End offset (exclusive) | Bytes actually changed |",
        "|---:|---:|---:|",
    ]
    for item in result["first_merged_ranges"]:
        lines.append("| {} | {} | {} |".format(
            item["offset_start"], item["offset_end_exclusive"], item["differing_bytes"]
        ))
    lines += ["", "## Largest changed regions", "",
              "| First offset | End offset (exclusive) | Bytes actually changed |",
              "|---:|---:|---:|"]
    for item in result["largest_merged_ranges"]:
        lines.append("| {} | {} | {} |".format(
            item["offset_start"], item["offset_end_exclusive"], item["differing_bytes"]
        ))
    lines += ["", "## Candidate encoded identifiers (first 12 matches only)", "",
              "| Representation | Current offsets | Backup offsets |",
              "|---|---|---|"]
    for key, item in result["pattern_hits"].items():
        lines.append("| {} | {} | {} |".format(
            key, ", ".join(map(str, item["current_first_positions"])) or "none",
            ", ".join(map(str, item["backup_first_positions"])) or "none"
        ))
    lines += ["", "## Bounded hex context", ""]
    for item in result["bounded_hex_previews"]:
        lines += [
            "### Offset {}".format(item["difference_offset"]),
            "",
            "Current [{}:{}]".format(
                item["current"]["offset_start"], item["current"]["offset_end_exclusive"]),
            "",
            t + item["current"]["hex"] + t,
            "",
            "Backup [{}:{}]".format(
                item["backup"]["offset_start"], item["backup"]["offset_end_exclusive"]),
            "",
            t + item["backup"]["hex"] + t,
            "",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--merge-gap", type=int, default=16)
    args = parser.parse_args()

    a = args.current.resolve()
    b = args.backup.resolve()
    if a == b:
        parser.error("Specify two different filenames")
    for path in (a, b):
        if not path.is_file():
            parser.error("Missing file: {}".format(path))
        if path.stat().st_size > MAX_INPUT_BYTES:
            parser.error("File too large for static comparison: {}".format(path))
    if any(path.resolve() in (a, b) for path in (args.json, args.markdown)):
        parser.error("Output paths cannot be either input file")

    result = compare(a.read_bytes(), b.read_bytes(), args.merge_gap)
    result["source_paths"] = {"current": str(a), "backup": str(b)}
    for path, value in (
        (args.json, json.dumps(result, indent=2, ensure_ascii=False)),
        (args.markdown, render_markdown(result)),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    print("PASS: neither binary was modified")
    print("Equal sizes: {} | diff bytes: {} | merged regions: {}".format(
        result["same_size"], result["differing_bytes_in_common_span"],
        result["total_merged_ranges"]
    ))
    print("Report: {}".format(args.markdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
