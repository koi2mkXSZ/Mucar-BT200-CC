"""Tests operate solely on synthetic split APKs."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

FILE = Path(__file__).resolve().parents[1] / "tools" / "extract_ggp_parser_libs.py"
SPEC = importlib.util.spec_from_file_location("extract_ggp_parser_libs", FILE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestParserExtraction(unittest.TestCase):
    def test_extract_only_expected_arch_and_preserve_apk(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            apk = root / "split_config.arm64_v8a.apk"
            with zipfile.ZipFile(apk, "w") as z:
                z.writestr("lib/arm64-v8a/libSEARCHID.so", b"\x7fELFsearch")
                z.writestr("lib/arm64-v8a/libx431file.so", b"\x7fELFx431")
                z.writestr("lib/armeabi-v7a/libSEARCHID.so", b"wrong-abi")
                z.writestr("lib/arm64-v8a/libLICENSE.so", b"not-required")
            actual = mod.digest(apk)
            old_expected = mod.EXPECTED_SPLIT_SHA256
            try:
                mod.EXPECTED_SPLIT_SHA256 = actual
                result = mod.export(apk, root / "out")
                self.assertEqual(mod.digest(apk), actual)
                self.assertEqual([x["name"] for x in result["libraries"]], list(mod.REQUIRED))
                self.assertEqual((root / "out" / "libSEARCHID.so").read_bytes(), b"\x7fELFsearch")
                self.assertFalse((root / "out" / "libLICENSE.so").exists())
                with self.assertRaises(FileExistsError):
                    mod.export(apk, root / "out")
            finally:
                mod.EXPECTED_SPLIT_SHA256 = old_expected

    def test_wrong_checksum_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            apk = root / "fake.apk"
            with zipfile.ZipFile(apk, "w") as z:
                z.writestr("lib/arm64-v8a/libSEARCHID.so", b"x")
                z.writestr("lib/arm64-v8a/libx431file.so", b"y")
            with self.assertRaisesRegex(ValueError, "Unexpected ARM64 APK SHA-256"):
                mod.export(apk, root / "not-created")
            self.assertFalse((root / "not-created").exists())


if __name__ == "__main__":
    unittest.main()
