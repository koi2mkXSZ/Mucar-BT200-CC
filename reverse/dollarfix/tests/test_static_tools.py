"""Offline synthetic tests. No proprietary APK or GGP needed in CI."""
import importlib.util
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ReverseToolsTests(unittest.TestCase):
    def test_apk_inventory_counts_dex_elf_and_hits(self):
        m = load("inventory_apk")
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "dummy.apk"
            with zipfile.ZipFile(file, "w") as z:
                z.writestr("classes.dex", b"dex\n035\x00some BluetoothGatt method")
                z.writestr("lib/arm64-v8a/libdemo.so", b"\x7fELFxxJNI_OnLoad")
                z.writestr("AndroidManifest.xml", b"abc")
            r = m.analyze(file)
            self.assertEqual(r["summary"]["dex_count"], 1)
            self.assertEqual(r["summary"]["native_so_count"], 1)
            self.assertEqual(len(r["selected_code_hits"]), 2)
            self.assertEqual(r["summary"]["abis"], ["arm64-v8a"])

    def test_ggp_table_is_bounded_and_has_lah(self):
        m = load("inspect_ggp")
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "dummy.GGP"
            raw = bytearray(100)
            raw[:4] = b"GGP\x00"
            raw[11] = 1
            struct.pack_into("<II", raw, 76, 84, 16)
            raw[84:88] = b"LAH\x00"
            file.write_bytes(raw)
            r = m.analyze(file)
            self.assertEqual(r["section_count"], 1)
            self.assertTrue(r["all_sections_lah"])

    def test_apk_diff_reports_single_changed_member(self):
        m = load("compare_apks")
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.apk", Path(d) / "b.apk"
            with zipfile.ZipFile(a, "w") as z:
                z.writestr("classes.dex", "v1")
                z.writestr("assets/a", "same")
            with zipfile.ZipFile(b, "w") as z:
                z.writestr("classes.dex", "v2")
                z.writestr("assets/a", "same")
            r = m.compare(a, b)
            self.assertEqual(r["changed"], ["classes.dex"])
            self.assertEqual(r["code_related"], ["classes.dex"])
            self.assertFalse(r["added"])
            self.assertFalse(r["removed"])

if __name__ == "__main__":
    unittest.main()
