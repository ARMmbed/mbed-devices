from unittest import TestCase

from mbed_devices.mbed_tools import cli
from mbed_devices._internal.mbed_tools.list_connected_devices import list_connected_devices


class TestCli(TestCase):
    def test_aliases_list_connected_devices(self):
        self.assertEqual(cli, list_connected_devices)
