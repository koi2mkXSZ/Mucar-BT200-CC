"""Verify bounded, method-anchored OEM Smali evidence extraction."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "extract_oem_trace.py"
SPEC = importlib.util.spec_from_file_location("extract_oem_trace", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestSmaliEvidence(unittest.TestCase):
    def test_method_matching_uses_name_not_parameter_type(self):
        self.assertTrue(MODULE.select_method(
            "public jsonUIDataStream(Ljava/lang/String;Lorg/json/JSONObject;)V",
            ("jsonUIDataStream",)))
        self.assertFalse(MODULE.select_method(
            "public randomCall(Landroid/content/Context;)V", ("id",)))
        self.assertTrue(MODULE.select_method(
            "public getDataStreamID()Ljava/lang/String;", ("id",)))

    def test_exact_lines_and_bounded_snippets(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "UiBusiness.smali"
            path.write_text(
                ".class Lcom/cnlaunch/diagnosemodule/UiBusiness;\n"
                ".field private mDataStreamID:Ljava/lang/String;\n"
                ".method private unrelated()V\n"
                "  return-void\n"
                ".end method\n"
                ".method private jsonUIDataStream(Ljava/lang/String;Lorg/json/JSONObject;)V\n"
                '  const-string v0, "key"\n'
                "  invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;\n"
                "  return-void\n"
                ".end method\n", encoding="utf-8"
            )
            matches = MODULE.extract_smali(path, ("jsonUIDataStream",))
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["line_start"], 6)
            self.assertEqual(matches[0]["line_end"], 10)
            self.assertTrue(any("optString" in line["text"] for line in matches[0]["excerpt"]))
            self.assertNotIn("unrelated", MODULE.markdown({"total_methods":1, "files":[{
                "relative_path":"UiBusiness.smali", "sha256":"dummy", "fields":[],
                "matched_methods":matches
            }], "missing_targets":[]}).lower())

    def test_missing_optional_files_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            part = root / "smali_classes3" / "com" / "cnlaunch" / "diagnosemodule"
            part.mkdir(parents=True)
            path = part / "DiagnoseLogicBusiness.smali"
            path.write_text(".method public dealDataStream()V\n return-void\n.end method\n")
            data = MODULE.collect(root)
            self.assertEqual(len(data["files"]), 1)
            self.assertEqual(data["total_methods"], 1)
            self.assertEqual(len(data["missing_targets"]), len(MODULE.TARGETS) - 1)
            self.assertTrue(data["not_a_call_graph"])


if __name__ == "__main__":
    unittest.main()
