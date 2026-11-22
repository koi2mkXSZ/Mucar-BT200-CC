#!/usr/bin/env python3
"""Validate structural LAH/GAG sections in a GGP file or a QIRUI ZIP."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from zipfile import ZipFile

def read_ggp(path, member=None):
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as f:
            candidates = [n for n in f.namelist() if n.upper().endswith("/CHERY_OLD_RU.GGP") or n.upper() == "CHERY_OLD_RU.GGP"]
            if member:
                if member not in f.namelist():
                    raise ValueError("GGP member not found: " + member)
                name = member
            elif len(candidates) == 1:
                name = candidates[0]
            else:
                raise ValueError("Expected one CHERY_OLD_RU.GGP member; found: " + repr(candidates))
            return f.read(name), name
    return path.read_bytes(), path.name

def analyze(path, member=None):
    data, source = read_ggp(path, member)
    if len(data) < 12 or data[:4] != b"GGP\x00":
        raise ValueError("Not a known GGP container")
    count = data[11]
    if not 1 <= count <= 128:
        raise ValueError("Unexpected section count: " + str(count))
    table_end = 12 + count * 72
    if len(data) < table_end:
        raise ValueError("Truncated section table")
    sections = []
    for i in range(count):
        rec = 12 + i * 72
        offset, size = struct.unpack_from("<II", data, rec + 64)
        if offset < table_end or size == 0 or offset + size > len(data):
            raise ValueError("Invalid section %d offset=%d size=%d" % (i, offset, size))
        magic = data[offset:offset + 4]
        sections.append({
            "section": i, "offset": offset, "size": size,
            "magic_hex": magic.hex(), "is_lah": magic[:3] == b"LAH",
            "sha256": hashlib.sha256(data[offset:offset+size]).hexdigest(),
        })
    ranges = sorted((s["offset"], s["offset"]+s["size"], s["section"]) for s in sections)
    for (_, finish, i), (start2, _, j) in zip(ranges, ranges[1:]):
        if finish > start2:
            raise ValueError("Sections overlap: %d and %d" % (i, j))
    return {
        "schema": "dollarfix.ggp-structure.v1", "source": source,
        "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "section_count": count, "sections": sections,
        "all_sections_lah": all(s["is_lah"] for s in sections),
        "note": "Only header/table structure, NOT encrypted descriptor content or Data Stream membership.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="CHERY_OLD_RU.GGP or QIRUI_FULL.zip")
    p.add_argument("--member", help="Explicit GGP path inside ZIP")
    p.add_argument("-o", "--output")
    args = p.parse_args()
    r = analyze(args.input, args.member)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:r[k] for k in ("source", "size", "sha256", "section_count", "all_sections_lah")}))

if __name__ == "__main__":
    main()
