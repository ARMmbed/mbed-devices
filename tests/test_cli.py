import json
import pathlib
from click.testing import CliRunner
from mbed_targets import MbedTarget
from tabulate import tabulate
from unittest import TestCase, mock

from mbed_devices.mbed_tools.cli import (
    cli,
    list_connected_devices,
    _build_tabular_output,
    _build_json_output,
    _get_build_targets,
    _sort_devices_by_name,
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

    @mock.patch("mbed_devices.mbed_tools.cli._sort_devices_by_name")
    @mock.patch("mbed_devices.mbed_tools.cli._build_tabular_output")
    def test_by_default_lists_devices_using_tabular_output(
        self, _build_tabular_output, _sort_devices_by_name, get_connected_devices
    ):
        get_connected_devices.return_value = [mock.Mock(spec_set=Device)]
        _build_tabular_output.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices)

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_tabular_output.return_value, result.output)
        _build_tabular_output.assert_called_once_with(_sort_devices_by_name.return_value)
        _sort_devices_by_name.assert_called_once_with(get_connected_devices.return_value)

    @mock.patch("mbed_devices.mbed_tools.cli._sort_devices_by_name")
    @mock.patch("mbed_devices.mbed_tools.cli._build_json_output")
    def test_given_json_flag_lists_devices_using_json_output(
        self, _build_json_output, _sort_devices_by_name, get_connected_devices
    ):
        get_connected_devices.return_value = [mock.Mock(spec_set=Device)]
        _build_json_output.return_value = "some output"

        result = CliRunner().invoke(list_connected_devices, "--format=json")

        self.assertEqual(result.exit_code, 0)
        self.assertIn(_build_json_output.return_value, result.output)
        _build_json_output.assert_called_once_with(_sort_devices_by_name.return_value)
        _sort_devices_by_name.assert_called_once_with(get_connected_devices.return_value)


class TestSortDevicesByName(TestCase):
    def test_sorts_devices_by_mbed_target_board_name(self):
        device_1 = mock.create_autospec(Device, mbed_target=mock.create_autospec(MbedTarget, board_name="A"))
        device_2 = mock.create_autospec(Device, mbed_target=mock.create_autospec(MbedTarget, board_name="B"))
        device_3 = mock.create_autospec(Device, mbed_target=mock.create_autospec(MbedTarget, board_name="C"))

        result = _sort_devices_by_name([device_3, device_1, device_2])

        self.assertEqual(list(result), [device_1, device_2, device_3])


class TestBuildTableOutput(TestCase):
    def test_returns_tabularised_representation_of_devices(self):
        device = Device(
            mbed_target=mock.create_autospec(
                MbedTarget, board_name="board-name", build_variant=("S", "NS"), board_type="board-type",
            ),
            serial_number="serial-number",
            serial_port="serial-port",
            mount_points=[pathlib.Path("/Volumes/FOO"), pathlib.Path("/Volumes/BAR")],
        )

        output = _build_tabular_output([device])

        expected_output = tabulate(
            [
                [
                    device.mbed_target.board_name,
                    device.serial_number,
                    device.serial_port,
                    "\n".join(map(str, device.mount_points)),
                    "\n".join(_get_build_targets(device.mbed_target)),
                ]
            ],
            headers=["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"],
        )
        self.assertEqual(output, expected_output)

    def test_displays_unknown_serial_port_value(self):
        device = Device(
            mbed_target=MbedTarget.from_target_entry({}),
            serial_number="serial",
            serial_port=None,
            mount_points=[pathlib.Path("somepath")],
        )

        output = _build_tabular_output([device])

        expected_output = tabulate(
            [
                [
                    device.mbed_target.board_name,
                    device.serial_number,
                    "UNKNOWN",
                    "\n".join(map(str, device.mount_points)),
                    "\n".join(_get_build_targets(device.mbed_target)),
                ]
            ],
            headers=["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"],
        )
        self.assertEqual(output, expected_output)


class TestBuildJsonOutput(TestCase):
    def test_returns_json_representation_of_devices(self):
        mbed_target = mock.create_autospec(
            MbedTarget,
            product_code="0021",
            board_type="HAT-BOAT",
            board_name="HAT Boat",
            mbed_os_support=["0.2"],
            mbed_enabled=["potentially"],
            build_variant=("S", "NS"),
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
                        "board_name": mbed_target.board_name,
                        "mbed_os_support": mbed_target.mbed_os_support,
                        "mbed_enabled": mbed_target.mbed_enabled,
                        "build_targets": _get_build_targets(mbed_target),
                    },
                }
            ],
            indent=4,
        )

        self.assertEqual(output, expected_output)

    def test_empty_values_keys_are_always_present(self):
        """Asserts that keys are present even if value is None."""
        device = Device(
            mbed_target=MbedTarget.from_target_entry({}), serial_number="foo", serial_port=None, mount_points=[],
        )

        output = json.loads(_build_json_output([device]))

        self.assertIsNone(output[0]["serial_port"])


class TestGetBuildTargets(TestCase):
    def test_returns_base_target_and_all_variants(self):
        mbed_target = mock.create_autospec(MbedTarget, build_variant=("S", "NS"), board_type="FOO")

        self.assertEqual(_get_build_targets(mbed_target), ["FOO_S", "FOO_NS", "FOO"])
