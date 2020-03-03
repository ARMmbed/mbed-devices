import uuid
from unittest import TestCase
from mbed_devices._internal.windows.component_descriptor_utils import data_object_to_dict

from tests.markers import windows_only


@windows_only
class TestDeviceIdParsing(TestCase):
    """Tests based on https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers."""

    def test_single_interface_usb_device(self):
        from mbed_devices._internal.windows.usb_device_identifier import parse_device_id

        self.assertTrue(parse_device_id("").is_undefined)
        self.assertTrue(parse_device_id(None).is_undefined)
        self.assertTrue(parse_device_id("4&38EF038C&0&0").is_undefined)
        self.assertFalse(parse_device_id("USB\\4&38EF038C&0&0").is_undefined)
        self.assertEqual(parse_device_id("USB\\4&38EF038C&0&0").RAW_UID, "4&38EF038C&0&0")
        self.assertEqual(parse_device_id("USB\\4&38EF038C&0&0").UID, "38EF038C")
        self.assertEqual(parse_device_id("USB\\ROOT_HUB30\\4&38EF038C&0&0").RAW_UID, "4&38EF038C&0&0")
        self.assertEqual(parse_device_id("USB\\VID_2109&PID_2812\\6&38E4CCB6&0&4").RAW_UID, "6&38E4CCB6&0&4")
        self.assertEqual(parse_device_id("USB\\VID_2109&PID_2812\\6&38E4CCB6&0&4").UID, "38E4CCB6")
        self.assertEqual(parse_device_id("USB\\VID_2109&PID_2812\\6&38E4CCB6&0&4").PID, "2812")
        self.assertEqual(parse_device_id("USB\\VID_2109&PID_2812\\6&38E4CCB6&0&4").VID, "2109")
        self.assertEqual(parse_device_id("USB\\VID_2109&PID_2812&REV_1100\\6&38E4CCB6&0&4").REV, "1100")

        self.assertGreaterEqual(
            data_object_to_dict(parse_device_id("USB\\VID_2109&PID_2812&REV_1100\\6&38E4CCB6&0&4")).items(),
            {"VID": "2109", "PID": "2812", "REV": "1100", "UID": "38E4CCB6", "RAW_UID": "6&38E4CCB6&0&4"}.items(),
        )

    def test_multiple_interface_usb_device(self):
        from mbed_devices._internal.windows.usb_device_identifier import parse_device_id

        self.assertEqual(
            parse_device_id("USB\\VID_0D28&PID_0204&MI_00\\0240000034544E45001A00018AA900292011000097969900").UID,
            "0240000034544E45001A00018AA900292011000097969900",
        )
        self.assertEqual(
            parse_device_id("USB\\VID_0D28&PID_0204&MI_00\\0240000034544E45001A00018AA900292011000097969900").RAW_UID,
            "0240000034544E45001A00018AA900292011000097969900",
        )
        self.assertEqual(
            parse_device_id("USB\\VID_0D28&PID_0204&MI_00\\0240000034544E45001A00018AA900292011000097969900").PID,
            "0204",
        )
        self.assertEqual(
            parse_device_id("USB\\VID_0D28&PID_0204&MI_02\\0240000034544E45001A00018AA900292011000097969900").VID,
            "0D28",
        )
        self.assertEqual(
            parse_device_id("USB\\VID_0D28&PID_0204&MI_02\\0240000034544E45001A00018AA900292011000097969900").MI, "02"
        )

    def test_equals(self):
        from mbed_devices._internal.windows.usb_device_identifier import UsbIdentifier, KEY_UID

        a = UsbIdentifier()
        b = UsbIdentifier()
        self.assertEqual(a, a)
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        a_dict = data_object_to_dict(a)
        a_dict[KEY_UID] = uuid.uuid4()
        b_dict = data_object_to_dict(a)
        b_dict[KEY_UID] = uuid.uuid4()
        a = UsbIdentifier(**a_dict)
        b = UsbIdentifier(**b_dict)
        self.assertEqual(a, a)
        self.assertNotEqual(a.uid, b.uid)
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        b = UsbIdentifier(**a_dict)
        self.assertEqual(a.uid, b.uid)
        self.assertEqual(a, a)
        self.assertEqual(a, b)
        self.assertEqual(b, a)

    def test_hashing(self):
        from mbed_devices._internal.windows.usb_device_identifier import UsbIdentifier, KEY_UID

        a = UsbIdentifier()
        b = UsbIdentifier()
        a_dict = data_object_to_dict(a)
        a_dict[KEY_UID] = uuid.uuid4()
        b_dict = data_object_to_dict(a)
        b_dict[KEY_UID] = uuid.uuid4()
        a = UsbIdentifier(**a_dict)
        b = UsbIdentifier(**b_dict)
        self.assertNotIn(a, dict())
        self.assertNotIn(a, {b: ""})
        self.assertIn(b, {b: ""})
        b = UsbIdentifier(**a_dict)
        self.assertIn(b, {b: ""})
        self.assertIn(a, {b: ""})
        self.assertIn(a, {b: ""})
