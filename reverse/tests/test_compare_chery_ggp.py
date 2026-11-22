"""Self-contained tests for read-only GGP difference detection."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "compare_chery_ggp.py"
SPEC = importlib.util.spec_from_file_location("compare_chery_ggp", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestCompareGgp(unittest.TestCase):
    def test_identical_inputs_have_no_byte_ranges(self):
        result = mod.compare(b"ABCDEFG", b"ABCDEFG")
        self.assertTrue(result["bytewise_equal"])
        self.assertEqual(result["total_merged_ranges"], 0)
        self.assertEqual(result["equal_prefix_bytes"], 7)
        self.assertEqual(result["differing_bytes_in_common_span"], 0)

    def test_sparse_and_grouped_changes(self):
        a = bytearray(b"x" * 200)
        b = bytearray(a)
        b[21] = ord("1")
        b[28] = ord("2")
        b[101] = ord("3")
        result = mod.compare(bytes(a), bytes(b), merge_gap=10)
        self.assertFalse(result["bytewise_equal"])
        self.assertEqual(result["differing_bytes_in_common_span"], 3)
        self.assertEqual(result["total_merged_ranges"], 2)
        self.assertEqual([v["offset_start"] for v in result["first_merged_ranges"]], [21, 101])
        self.assertEqual(result["first_merged_ranges"][0]["differing_bytes"], 2)

    def test_different_length_and_decimal_id(self):
        id_value = (76010020).to_bytes(4, "little")
        original = b"AB" + id_value
        backup = original + b"EXTRA"
        result = mod.compare(original, backup)
        self.assertFalse(result["same_size"])
        self.assertEqual(result["trailing_bytes_after_common_span"], 5)
        self.assertEqual(result["pattern_hits"]["ID_DECIMAL_WORD_LITTLE_ENDIAN"]["current_first_positions"], [2])

    def test_hashes_do_not_modify_readonly_files(self):
        with tempfile.TemporaryDirectory() as root:
            a = Path(root) / "CHERY_OLD_RU.GGP"
            b = Path(root) / "CHERY_OLD_RU.GGP.T11ODO.BAK"
            a.write_bytes(b"HELLO")
            b.write_bytes(b"HElLO")
            before_a, before_b = a.read_bytes(), b.read_bytes()
            diff = mod.compare(before_a, before_b)
            self.assertEqual(a.read_bytes(), before_a)
            self.assertEqual(b.read_bytes(), before_b)
            self.assertEqual(diff["current"]["sha256"], hashlib.sha256(before_a).hexdigest())


if __name__ == "__main__":
    unittest.main()
