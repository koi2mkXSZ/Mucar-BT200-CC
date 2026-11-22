#!/usr/bin/env python3
"""Review original-vs-candidate APK ZIP contents, including code and signatures."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

def inventory(path):
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid ZIP member in " + str(path))
        return {
            info.filename: hashlib.sha256(archive.read(info)).hexdigest()
            for info in archive.infolist() if not info.is_dir()
        }

def compare(original, candidate):
    original, candidate = Path(original), Path(candidate)
    left, right = inventory(original), inventory(candidate)
    lkeys, rkeys = set(left), set(right)
    changed = sorted(k for k in lkeys & rkeys if left[k] != right[k])
    added = sorted(rkeys - lkeys)
    removed = sorted(lkeys - rkeys)
    touched = changed + added + removed
    code = sorted(k for k in touched if k.endswith(".dex") or k.endswith(".so"))
    signed = sorted(k for k in touched if k.upper().startswith("META-INF/") or k.endswith(".idsig"))
    return {
        "schema": "dollarfix.apk-diff.v1",
        "original": original.name,
        "candidate": candidate.name,
        "changed": changed, "added": added, "removed": removed,
        "code_related": code, "signature_related": signed,
        "note": "A rebuilt APK may change unrelated ZIP members. Review ALL entries; resigning changes signature identity.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("original")
    p.add_argument("candidate")
    p.add_argument("-o", "--output")
    args = p.parse_args()
    report = compare(args.original, args.candidate)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": len(report["changed"]), "added": len(report["added"]),
                      "removed": len(report["removed"]), "code_related": report["code_related"],
                      "signature_related": report["signature_related"]}))

if __name__ == "__main__":
    main()
