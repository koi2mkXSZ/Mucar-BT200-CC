"""Tests use tiny synthetic code, never proprietary DollarFix source."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools" / "trace_data_stream.py"
SPEC = importlib.util.spec_from_file_location("trace_data_stream", PATH)
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)


class TestSourceTrace(unittest.TestCase):
    def test_smali_method_anchor_and_separate_vendor_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            smali = root / "smali" / "com" / "elm" / "PIDV.smali"
            smali.parent.mkdir(parents=True)
            smali.write_text(
                ".method public toBasicDataStreamBean()Ljava/lang/Object;\n"
                '    const-string v0, "76010020"\n'
                ".end method\n", encoding="utf-8"
            )
            java = root / "src" / "com" / "cnlaunch" / "Reader.java"
            java.parent.mkdir(parents=True)
            java.write_text("class Reader { JniX431File reader; }\n", encoding="utf-8")
            data = scanner.trace([root])
            self.assertTrue(data["not_a_call_graph"])
            self.assertEqual(data["files_inspected"], 2)
            self.assertEqual(data["marker_counts"]["76010020"], 1)
            self.assertEqual(data["marker_counts"]["JniX431File"], 1)
            odometer = next(x for x in data["occurrences"] if x["marker"] == "76010020")
            self.assertEqual(odometer["line"], 2)
            self.assertTrue(odometer["path_hint"].startswith("ELM"))
            self.assertIn("toBasicDataStreamBean", odometer["method_anchor"])

    def test_no_match_does_not_claim_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "NoMatchingCode.java"
            src.write_text("class Example {}", encoding="utf-8")
            data = scanner.trace([Path(tmp)])
            self.assertEqual(data["marker_counts"], {})
            self.assertEqual(data["files_inspected"], 1)


if __name__ == "__main__":
    unittest.main()
