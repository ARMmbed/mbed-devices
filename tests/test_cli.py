import pathlib
from unittest import TestCase, mock
from click.testing import CliRunner
from mbed_targets import MbedTarget

from mbed_devices.mbed_tools.cli import cli, list_connected_devices
from mbed_devices import Device


class TestCli(TestCase):
    def test_aliases_list_connected_devices(self):
        self.assertEqual(cli, list_connected_devices)


@mock.patch("mbed_devices.mbed_tools.cli.get_connected_devices")
class TestListConnectedDevices(TestCase):
    def test_informs_when_no_devices_are_connected(self, get_connected_devices):
        get_connected_devices.return_value = []

        result = CliRunner().invoke(list_connected_devices)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No connected Mbed devices found.", result.output)

    def test_lists_devices_which_are_connected(self, get_connected_devices):
        device = Device(
            mbed_target=mock.Mock(spec_set=MbedTarget, platform_name="Foo"),
            serial_number="nice serial",
            serial_port="I'm a serial port",
            mount_points=[pathlib.Path("/Volumes/FOO")],
        )
        get_connected_devices.return_value = [device]

        result = CliRunner().invoke(list_connected_devices)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(device.mbed_target.platform_name, result.output)
        self.assertIn(device.serial_number, result.output)
        self.assertIn(device.serial_port, result.output)
        self.assertIn(", ".join(str(m) for m in device.mount_points), result.output)
