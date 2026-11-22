#!/usr/bin/env python3
"""Extract bounded method-level Smali evidence for the OEM DollarFix data-stream path.

Reads local, user-obtained Apktool output. Does not modify APKs, phone, or ECU.
The excerpt is saved ONLY in local output and must not be committed as source.
No control flow or call edges are inferred from lexical co-occurrence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

TARGETS = {
    "smali_classes3/com/cnlaunch/diagnosemodule/DiagnoseLogicBusiness.smali": (
        "dealDataStream", "getDataStreamCount", "dealUIData", "pageStreamFeedbackMask",
    ),
    "smali_classes3/com/cnlaunch/diagnosemodule/DiagnoseUIDataBusiness.smali": (
        "jsonUIDataStream", "getDefDataStreamDatraFromJson",
        "jsonUIDiagnoseSpecialDatastream", "getDiagInfoFromJson",
    ),
    "smali_classes3/com/cnlaunch/diagnosemodule/bean/BasicDataStreamBean.smali": (
        "id", "choice", "select", "value", "dataStream",
        "name", "isShow", "isVisible", "<init>",
    ),
    "smali_classes7/com/thinkcar/diagnosebase/ui/datastream/UiDataStreamManager.smali": (
        "dealWithDataStreamForUi", "dataStream", "choice", "select",
    ),
    "smali_classes7/com/thinkcar/diagnosebase/ui/datastream/logic/DataStreamManager.smali": (
        "dataStream", "select", "choice", "id",
    ),
    "smali_classes7/com/thinkcar/diagnosebase/ui/popup/SelectDataStreamDrawerPopup.smali": (
        "dataStream", "select", "choice", "id",
    ),
    "smali_classes3/com/cnlaunch/diagnosemodule/adapter/BaseDatastreamListAdapter.smali": (
        "dataStream", "select", "choice", "id", "convert", "bind",
    ),
}
HIGHLIGHTS = re.compile(
    r"(?i)(?:\b(?:invoke-\w+|new-instance|iput(?:-\w+)?|iget(?:-\w+)?|"
    r"sget(?:-\w+)?|sput(?:-\w+)?|const-string(?:/jumbo)?|"
    r"if-[a-z]+|packed-switch|sparse-switch)\b|"
    r"\b(?:dataStream|datastream|selected|visible|hidden|choice|"
    r"JSONObject|JSONArray|BasicDataStreamBean|76010020|GGP|"
    r"getId|setId)\b)"
)
MAX_EXCERPT_LINES = 250
MAX_METHODS_PER_FILE = 50


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def select_method(signature: str, needles: tuple[str, ...]) -> bool:
    return any(name.lower() in signature.lower() for name in needles)


def extract_smali(path: Path, needles: tuple[str, ...]) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    methods = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith(".method "):
            index += 1
            continue
        begin = index
        signature = lines[begin].strip().removeprefix(".method ")
        end = begin + 1
        while end < len(lines) and not lines[end].lstrip().startswith(".end method"):
            end += 1
        if end >= len(lines):
            raise ValueError(f"Unterminated Smali method at {path}:{begin + 1}")
        index = end + 1
        if not select_method(signature, needles):
            continue
        if len(methods) >= MAX_METHODS_PER_FILE:
            break
        selected = set()
        for i in range(begin, end + 1):
            if HIGHLIGHTS.search(lines[i]):
                for j in range(max(begin, i - 2), min(end + 1, i + 3)):
                    selected.add(j)
        selected.add(begin)
        ordered = sorted(selected)
        excerpts = [
            {"line": i + 1, "text": lines[i][:400]}
            for i in ordered[:MAX_EXCERPT_LINES]
        ]
        methods.append({
            "signature": signature,
            "line_start": begin + 1,
            "line_end": end + 1,
            "source_line_count": end - begin + 1,
            "selected_excerpt_lines": len(excerpts),
            "excerpt_truncated": len(ordered) > MAX_EXCERPT_LINES,
            "excerpt": excerpts,
        })
    return methods


def collect(apktool_dir: Path) -> dict:
    if not apktool_dir.is_dir():
        raise FileNotFoundError(str(apktool_dir))
    output = {
        "analysis_type": "bounded-smali-excerpts",
        "source_apk": "locally extracted base.apk; verify separately against manifest",
        "not_a_call_graph": True,
        "warning": "Do not infer runtime behavior or Delphi visibility from lexical references",
        "files": [],
        "missing_targets": [],
        "total_methods": 0,
    }
    for relative_name, needles in TARGETS.items():
        path = apktool_dir.joinpath(*relative_name.split("/"))
        if not path.is_file():
            output["missing_targets"].append(relative_name)
            continue
        methods = extract_smali(path, needles)
        output["files"].append({
            "relative_path": relative_name,
            "sha256": file_hash(path),
            "matched_methods": methods,
        })
        output["total_methods"] += len(methods)
    return output


def markdown(data: dict) -> str:
    tick = chr(96)
    fence = tick * 3
    result = [
        "# DollarFix OEM Data Stream — Smali evidence excerpts",
        "",
        "**Important:** This is bounded source evidence, not a verified call graph.",
        "Inspect all excerpts before selecting an actual UI patch location.",
        "",
        f"Matched methods: {data['total_methods']}; "
        f"files found: {len(data['files'])}; "
        f"files missing: {len(data['missing_targets'])}.",
        "",
    ]
    if data["missing_targets"]:
        result += ["## Missing files", ""]
        result += [f"- {tick}{name}{tick}" for name in data["missing_targets"]]
        result.append("")
    for file in data["files"]:
        result += [f"## {tick}{file['relative_path']}{tick}", "",
                   f"SHA-256 (decompiled Smali): {tick}{file['sha256']}{tick}", ""]
        for method in file["matched_methods"]:
            result += [
                f"### {tick}{method['signature']}{tick}",
                "",
                f"Lines {method['line_start']}–{method['line_end']}; "
                f"excerpt {method['selected_excerpt_lines']} / "
                f"{method['source_line_count']} total lines.",
                "",
                fence + "smali",
            ]
            last = None
            for line in method["excerpt"]:
                if last is not None and line["line"] > last + 1:
                    result.append("    ...")
                result.append(f"{line['line']:>6}: {line['text']}")
                last = line["line"]
            result += [fence, ""]
            if method["excerpt_truncated"]:
                result += ["*Excerpt limited; inspect local Smali for full method.*", ""]
    return "\n".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apktool", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    if not args.apktool.is_dir():
        parser.error(f"Directory not found: {args.apktool}")
    result = collect(args.apktool)
    if not result["files"]:
        parser.error("No target Smali files found; verify path to apktool-base")
    for path, content in (
        (args.output_json, json.dumps(result, ensure_ascii=False, indent=2)),
        (args.output_md, markdown(result)),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"PASS: {len(result['files'])} target files inspected; "
          f"{result['total_methods']} target methods located")
    print(f"OEM Smali report: {args.output_md}")
    if result["missing_targets"]:
        print(f"Note: {len(result['missing_targets'])} optional target files missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
