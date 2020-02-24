import pathlib
from unittest import TestCase, mock

from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_devices.device import Device
from mbed_devices.mbed_devices import (
    _build_device,
    get_connected_devices,
)


class TestGetConnectedDevices(TestCase):
    @mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
    @mock.patch("mbed_devices.mbed_devices._build_device")
    def test_builds_devices_from_candidates(self, _build_device, detect_candidate_devices):
        candidate = mock.Mock(spec_set=CandidateDevice)
        detect_candidate_devices.return_value = [candidate]
        self.assertEqual(get_connected_devices(), [_build_device.return_value])
        _build_device.assert_called_once_with(candidate)


class TestBuildDevice(TestCase):
    @mock.patch("mbed_devices.mbed_devices._get_mbed_target_for_candidate")
    def test_converts_candidate_to_device(self, _get_mbed_target_for_candidate):
        candidate = CandidateDevice(
            product_id="0x0000",
            vendor_id="0x1234",
            serial_port="some-serial",
            serial_number="some-number",
            mount_points=[pathlib.Path("/")],
        )
        self.assertEqual(
            _build_device(candidate),
            Device(
                serial_port=candidate.serial_port,
                serial_number=candidate.serial_number,
                mount_points=candidate.mount_points,
                mbed_target=_get_mbed_target_for_candidate.return_value,
            ),
        )
        _get_mbed_target_for_candidate.assert_called_once_with(candidate)
