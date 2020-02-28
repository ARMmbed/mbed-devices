from tests.markers import windows_only
from unittest import TestCase
import random


@windows_only
class TestDataAggregrator(TestCase):
    def test_retrieve_port_name(self):
        from mbed_devices._internal.windows.serial_port import parse_caption
        from mbed_devices._internal.windows.component_descriptor import UNKNOWN_VALUE

        self.assertEqual(UNKNOWN_VALUE, parse_caption(UNKNOWN_VALUE))
        self.assertEqual("COM13", parse_caption("Serial Port for Barcode Scanner (COM13)"))
        port_name = f"COM{random.choice(range(0, 1000))}"
        self.assertEqual(port_name, parse_caption(f"mbed Serial Port ({port_name})"))