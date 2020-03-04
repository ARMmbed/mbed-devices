import unittest
from mbed_devices._internal.windows.windows_identifier import WindowsUID, is_device_instance_id
import random
import uuid
from tests.markers import windows_only


def generateUID() -> WindowsUID:
    return WindowsUID(uid=str(uuid.uuid4()), raw_uid=f"/{uuid.uuid4()}&001", serial_number=str(random.randint(1, 100)))


@windows_only
class TestWindowsUID(unittest.TestCase):
    def test_is_instance_id(self):
        # Testing that the values are likely to be instance IDs generated by the OS
        self.assertTrue(is_device_instance_id(None))
        self.assertTrue(is_device_instance_id("8&2F125EC6&0&0003"))
        self.assertTrue(is_device_instance_id("8&2f125ec6&0"))
        self.assertTrue(is_device_instance_id("8&2F125EC6&0&0002"))
        self.assertFalse(is_device_instance_id(""))
        self.assertFalse(is_device_instance_id("000440112138"))

    def test_uid_equality(self):
        uid1 = WindowsUID(uid="uid1", raw_uid="/uid1&001", serial_number=str(random.randint(1, 100)))
        # Equal testing with self and other types.
        self.assertNotEqual(uid1, None)
        self.assertIsNotNone(uid1)
        self.assertNotEqual(uid1, "")
        self.assertFalse(uid1 == "")
        self.assertFalse(uid1 == dict())
        self.assertEqual(uid1, uid1)
        self.assertTrue(uid1 == uid1)

        # Does not equal to completely different objects
        uid2 = WindowsUID(uid="uid2", raw_uid="/uid1&002", serial_number=None)
        self.assertNotEqual(uid1, uid2)

        # Equals other objects with same uid
        uid3 = WindowsUID(uid="uid1", raw_uid="/uid1&003", serial_number=str(random.randint(1, 100)))
        self.assertEqual(uid1, uid3)
        self.assertTrue(uid1 == uid3)

        # Equals other objects with similar uid (subset)
        uid5 = WindowsUID(uid="uid1&0114", raw_uid="/uid1&0114", serial_number=None)
        self.assertEqual(uid3, uid5)
        self.assertEqual(uid1, uid5)

        # Equals other objects with same serial number
        uid4 = WindowsUID(uid="uid4", raw_uid="/uid4&004", serial_number=uid1.serial_number)
        self.assertEqual(uid1, uid4)

        # Equals other objects with serial number same to uid
        uid6 = WindowsUID(uid="uid6454", raw_uid="/uid6454&006", serial_number="uid1")
        self.assertEqual(uid1, uid6)

    def test_serial_number(self):
        # Tests trying to determine the most plausible serial number from a set of values.
        uid1 = generateUID()
        self.assertEqual(uid1.presumed_serial_number, uid1.uid)
        self.assertNotEqual(uid1.presumed_serial_number, uid1.serial_number)
        uid2 = WindowsUID(uid="uid12&223", raw_uid="djfds;fj", serial_number=None)
        self.assertEqual(uid2.presumed_serial_number, uid2.uid)
        self.assertNotEqual(uid2.presumed_serial_number, uid2.serial_number)
        self.assertFalse(uid2.contains_genuine_serial_number())
        uid3 = WindowsUID(uid="uid12&223", raw_uid="djfds;fj", serial_number="12345679")
        self.assertNotEqual(uid3.presumed_serial_number, uid3.uid)
        self.assertEqual(uid3.presumed_serial_number, uid3.serial_number)
        self.assertTrue(uid3.contains_genuine_serial_number())

    def test_instanceid(self):
        # Tests trying to determine the most plausible instance IDs from a set of values.
        uid1 = generateUID()
        self.assertEqual(uid1.instance_id, uid1.serial_number)
        uid2 = WindowsUID(uid="uid12&223", raw_uid="djfds;fj", serial_number=None)
        self.assertEqual(uid2.instance_id, uid2.uid)
        uid3 = WindowsUID(uid="uid12&223", raw_uid="djfds;fj", serial_number="12345679")
        self.assertEqual(uid3.instance_id, uid3.uid)
        uid4 = WindowsUID(uid="12345687", raw_uid="djfds;fj", serial_number="12&3456&79")
        self.assertEqual(uid4.instance_id, uid4.serial_number)

    def test_uid_hashing(self):
        uid1 = generateUID()
        uid2 = generateUID()
        # Usual checks for different UIDs
        # Checks that if hashes are different then elements are not equal
        self.assertNotEqual(hash(uid1), hash(uid2))
        self.assertNotEqual(uid1, uid2)

        # Checks lookup in set
        self.assertIn(uid1, (uid1, uid2))
        self.assertIn(uid2, {uid1, uid2})
        # Checks lookup in dictionary
        self.assertIn(uid1, {uid1: "1", uid2: "2"})
        self.assertNotIn(uid1, dict())
        self.assertNotIn(uid1, {uid2: "1"})
        self.assertEqual({uid1: "1", uid2: "2"}.get(uid1), "1")
        self.assertIsNone({uid2: "2"}.get(uid1))

        # Checks the situation where two UIDs are equal/corresponding to the same device but their fields are different.
        uid3 = WindowsUID(uid="uid12&223", raw_uid="djfds;fj", serial_number=None)
        uid4 = WindowsUID(uid="123412", raw_uid="djfds;fjfsf&0&0000", serial_number="uid12&223")
        # UIDs being equal => hashes are equal.
        self.assertEqual(uid3, uid4)
        self.assertEqual(uid4, uid3)
        self.assertEqual(hash(uid3), hash(uid4))
        self.assertEqual(hash(uid4), hash(uid3))
        # Checks lookup in set
        self.assertIn(uid3, (uid1, uid4))
        self.assertIn(uid4, (uid1, uid3))

    def test_ordering(self):
        uid1 = WindowsUID(uid="123456789", raw_uid="/uid1&002", serial_number=None)
        uid2 = WindowsUID(uid="0&64FAFGG", raw_uid="/0&64FAFGG&002", serial_number="345240562")
        self.assertGreater(uid2, uid1)
        self.assertLess(uid1, uid2)
        self.assertListEqual(sorted([uid2, uid1]), [uid1, uid2])
