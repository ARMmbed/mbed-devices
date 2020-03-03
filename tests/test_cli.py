import json
import pathlib
from unittest import TestCase, mock
from click.testing import CliRunner
from mbed_targets import MbedTarget

from mbed_devices.mbed_tools.cli import (
    cli,
    list_connected_devices,
    _build_tabular_output,
    _build_json_output,
)
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

    @mock.patch("mbed_devices.mbed_tools.cli._build_tabular_output")
    def test_by_default_lists_devices_using_tabular_output(self, _build_tabular_output, get_connected_devices):
        get_connected_devices.return_value = [mock.Mock(spec_set=Device)]
        _build_tabular_output.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_tabular_output.return_value, result.output)

    @mock.patch("mbed_devices.mbed_tools.cli._build_json_output")
    def test_given_json_flag_lists_devices_using_json_output(self, _build_json_output, get_connected_devices):
        get_connected_devices.return_value = [mock.Mock(spec_set=Device)]
        _build_json_output.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices, "--format=json")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_json_output.return_value, result.output)


class TestBuildTableOutput(TestCase):
    def test_returns_tabularised_representation_of_devices(self):
        device = Device(
            mbed_target=mock.Mock(spec_set=MbedTarget, platform_name="Foo"),
            serial_number="nice serial",
            serial_port="I'm a serial port",
            mount_points=[pathlib.Path("/Volumes/FOO"), pathlib.Path("/Volumes/BAR")],
        )

        output = _build_tabular_output([device])

        self.assertIn(device.mbed_target.platform_name, output)
        self.assertIn(device.serial_number, output)
        self.assertIn(device.serial_port, output)
        self.assertIn(", ".join(str(m) for m in device.mount_points), output)

    def test_handles_unknown_mbed_target(self):
        device = Device(
            mbed_target=None, serial_number="serial", serial_port="COM1", mount_points=[pathlib.Path("somepath")],
        )

        output = _build_tabular_output([device])

        self.assertIn("UNKNOWN", output)

    def test_handles_unknown_serial_port(self):
        device = Device(
            mbed_target=mock.Mock(spec_set=MbedTarget, platform_name="Bar"),
            serial_number="serial",
            serial_port=None,
            mount_points=[pathlib.Path("somepath")],
        )

        output = _build_tabular_output([device])

        self.assertIn("UNKNOWN", output)


class TestBuildJsonOutput(TestCase):
    def test_returns_json_representation_of_devices(self):
        mbed_target = mock.Mock(
            spec_set=MbedTarget,
            product_code="0021",
            board_type="HAT-BOAT",
            platform_name="HAT Boat",
            mbed_os_support=["0.2"],
            mbed_enabled=["potentially"],
        )
        device = Device(
            mbed_target=mbed_target,
            serial_number="09887654",
            serial_port="COM1",
            mount_points=[pathlib.Path("somepath")],
        )

        output = _build_json_output([device])
        expected_output = json.dumps(
            [
                {
                    "serial_number": device.serial_number,
                    "serial_port": device.serial_port,
                    "mount_points": [str(m) for m in device.mount_points],
                    "mbed_target": {
                        "product_code": mbed_target.product_code,
                        "board_type": mbed_target.board_type,
                        "platform_name": mbed_target.platform_name,
                        "mbed_os_support": mbed_target.mbed_os_support,
                        "mbed_enabled": mbed_target.mbed_enabled,
                    },
                }
            ],
            indent=4,
        )

        self.assertEqual(output, expected_output)

    def test_empty_values_keys_are_always_present(self):
        """Asserts that keys are present even if value is None."""
        device = Device(mbed_target=None, serial_number="foo", serial_port=None, mount_points=[],)

        output = _build_json_output([device])
        expected_output = json.dumps(
            [{"serial_number": "foo", "serial_port": None, "mount_points": [], "mbed_target": None}], indent=4
        )

        self.assertEqual(output, expected_output)
