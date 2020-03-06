import pathlib
from unittest import TestCase
from mbed_devices._internal.candidate_device import CandidateDevice


def build_candidate_data(**overrides):
    defaults = {
        "product_id": "0x1234",
        "vendor_id": "0x5678",
        "mount_points": [pathlib.Path("./foo")],
        "serial_number": "qwer",
        "serial_port": "COM1",
    }
    return {**defaults, **overrides}


class TestCandidateDevice(TestCase):
    def test_produces_a_valid_candidate(self):
        candidate_data = build_candidate_data()
        candidate = CandidateDevice(**candidate_data)

        self.assertEqual(candidate.product_id, candidate_data["product_id"])
        self.assertEqual(candidate.vendor_id, candidate_data["vendor_id"])
        self.assertEqual(candidate.mount_points, candidate_data["mount_points"])
        self.assertEqual(candidate.serial_number, candidate_data["serial_number"])
        self.assertEqual(candidate.serial_port, candidate_data["serial_port"])

    def test_candidates_with_same_properties_are_equal(self):
        candidate_data = build_candidate_data()
        self.assertEqual(
            CandidateDevice(**candidate_data), CandidateDevice(**candidate_data),
        )

    def test_compares_false_with_non_candidate_type(self):
        candidate_data = build_candidate_data()
        self.assertEqual(CandidateDevice(**candidate_data) != candidate_data, True)

    def test_candidate_compares_lt_candidate_with_greater_serial_number(self):
        candidate_data_a = build_candidate_data(serial_number="1")
        candidate_data_b = build_candidate_data(serial_number="0")
        self.assertLess(CandidateDevice(**candidate_data_b), CandidateDevice(**candidate_data_a))

    def test_candidate_lt_op_raises_type_error_for_non_candidate(self):
        candidate_data_a = build_candidate_data(serial_number="1")
        candidate_data_b = build_candidate_data(serial_number="0")
        with self.assertRaises(TypeError):
            CandidateDevice(**candidate_data_b) < candidate_data_a

    def test_hash_is_hash_of_required_fields(self):
        cand_data = build_candidate_data()
        expect = hash(cand_data["serial_number"]) ^ hash(cand_data["vendor_id"]) ^ hash(cand_data["product_id"])
        self.assertEqual(hash(CandidateDevice(**cand_data)), expect)

    def test_raises_when_product_id_is_empty(self):
        candidate_data = build_candidate_data(product_id="")
        with self.assertRaisesRegex(ValueError, "product_id"):
            CandidateDevice(**candidate_data)

    def test_raises_when_product_id_is_not_hex(self):
        candidate_data = build_candidate_data(product_id="TEST")
        with self.assertRaisesRegex(ValueError, "product_id"):
            CandidateDevice(**candidate_data)

    def test_prefixes_product_id_hex_value(self):
        candidate_data = build_candidate_data(product_id="ff01")
        candidate = CandidateDevice(**candidate_data)
        self.assertEqual(candidate.product_id, "0xff01")

    def test_raises_when_vendor_id_is_empty(self):
        candidate_data = build_candidate_data(vendor_id="")
        with self.assertRaisesRegex(ValueError, "vendor_id"):
            CandidateDevice(**candidate_data)

    def test_raises_when_vendor_id_is_not_hex(self):
        candidate_data = build_candidate_data(vendor_id="TEST")
        with self.assertRaisesRegex(ValueError, "vendor_id"):
            CandidateDevice(**candidate_data)

    def test_prefixes_vendor_id_hex_value(self):
        candidate_data = build_candidate_data(vendor_id="cbad")
        candidate = CandidateDevice(**candidate_data)
        self.assertEqual(candidate.vendor_id, "0xcbad")

    def test_raises_when_mount_points_are_empty(self):
        with self.assertRaisesRegex(ValueError, "mount_points"):
            CandidateDevice(product_id="1234", vendor_id="1234", mount_points=[], serial_number="1234")

    def test_raises_when_serial_number_is_empty(self):
        candidate_data = build_candidate_data(serial_number="")
        with self.assertRaisesRegex(ValueError, "serial_number"):
            CandidateDevice(**candidate_data)
