"""Synthetic, privacy-safe tests for the QIRUI literal inventory."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "probe_qirui.py"
SPEC = importlib.util.spec_from_file_location("probe_qirui", SCRIPT)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class TestQiruiProbe(unittest.TestCase):
    def test_find_ascii_utf16_and_raw_at_chunk_boundaries(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "CHERY_OLD_RU.GGP"
            payload = (
                b"abc" + b"76010020" + b"z" +
                "76010020".encode("utf-16le") + b"\x00" +
                bytes.fromhex("76 01 00 20") + b"\xff" + b"Mile meter"
            )
            path.write_bytes(payload)
            before = path.read_bytes()
            old_chunk = probe.CHUNK_SIZE
            probe.CHUNK_SIZE = 7
            try:
                report = probe.probe(root)
            finally:
                probe.CHUNK_SIZE = old_chunk
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(report["file_count"], 1)
            self.assertEqual(report["files_with_hits"], 1)
            result = report["files"][0]
            self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
            offsets = {(x["pattern"], x["offset"]) for x in result["hits"]}
            self.assertIn(("ODO_ID_ASCII", 3), offsets)
            self.assertIn(("ODO_ID_UTF16LE", 12), offsets)
            self.assertIn(("ODO_ID_RAW_HEX", 29), offsets)
            self.assertIn(("MILE_METER_ASCII", 34), offsets)

    def test_no_hit_does_not_claim_format_decoded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "libCHERY_OLD.so").write_bytes(bytes(range(100)))
            report = probe.probe(root)
            self.assertFalse(report["format_decoded"])
            self.assertEqual(report["extensions"], {".so": 1})
            self.assertEqual(report["files_with_hits"], 0)


if __name__ == "__main__":
    unittest.main()
