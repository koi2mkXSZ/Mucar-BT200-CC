"""Unit tests using synthetic archives, never proprietary DollarFix data."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

MODULE = Path(__file__).resolve().parents[1] / "tools" / "inventory_apk.py"
spec = importlib.util.spec_from_file_location("inventory_apk", MODULE)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class TestApkInventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.apk = self.root / "sample.apk"
        elf = bytearray(32)
        elf[0:4] = b"\x7fELF"
        elf[4] = 2
        elf[5] = 1
        elf[18:20] = (183).to_bytes(2, "little")
        with ZipFile(self.apk, "w") as zf:
            zf.writestr("AndroidManifest.xml", b"binary manifest placeholder")
            zf.writestr("classes.dex", b"dex\nBluetoothSocket;com.cnlaunch;")
            zf.writestr("lib/arm64-v8a/libsample.so", bytes(elf))
            zf.writestr("META-INF/CERT.RSA", b"fake test certificate")

    def tearDown(self):
        self.tmp.cleanup()

    def test_inventory_discovers_dex_native_and_signing_entries(self):
        report = inventory.inspect(self.apk)
        self.assertEqual(report["entry_count"], 4)
        self.assertEqual(report["dex_count"], 1)
        self.assertEqual(report["native_count"], 1)
        self.assertTrue(report["has_android_manifest"])
        self.assertEqual(report["native"][0]["architecture"], "AArch64")
        self.assertIn("META-INF/CERT.RSA", report["certificate_entries"])
        self.assertEqual(report["sha256"], hashlib.sha256(self.apk.read_bytes()).hexdigest())

    def test_keyword_offsets_are_exact_and_no_context_is_leaked(self):
        report = inventory.inspect(self.apk)
        hits = [x for x in report["tags"] if x["tag"] == "bluetooth_socket"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["entry"], "classes.dex")
        self.assertEqual(hits[0]["offset"], 4)
        self.assertNotIn("context", hits[0])

    def test_extracted_native_is_exact(self):
        root = self.root / "native"
        inventory.inspect(self.apk, root)
        expected = root / "lib" / "arm64-v8a" / "libsample.so"
        self.assertTrue(expected.is_file())
        with ZipFile(self.apk) as zf:
            self.assertEqual(expected.read_bytes(), zf.read("lib/arm64-v8a/libsample.so"))

    def test_path_traversal_is_rejected(self):
        bad_archive = self.root / "unsafe.apk"
        with ZipFile(bad_archive, "w") as zf:
            zf.writestr("../escape.so", b"not an ELF")
        with self.assertRaises(ValueError):
            inventory.inspect(bad_archive, self.root / "native")
        self.assertFalse((self.root.parent / "escape.so").exists())


if __name__ == "__main__":
    unittest.main()
