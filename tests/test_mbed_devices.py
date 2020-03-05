from unittest import TestCase, mock
from mbed_targets import UnknownTarget

from tests.factories import CandidateDeviceFactory
from mbed_devices.device import Device
from mbed_devices.mbed_devices import (
    NoTargetForCandidate,
    _build_device,
    _get_mbed_target_for_candidate,
    get_connected_devices,
)
from mbed_devices._internal.product_code import MissingProductCode


class TestGetConnectedDevices(TestCase):
    @mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
    @mock.patch("mbed_devices.mbed_devices._build_device")
    def test_builds_devices_from_candidates(self, _build_device, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        detect_candidate_devices.return_value = [candidate]
        self.assertEqual(get_connected_devices(), [_build_device.return_value])
        _build_device.assert_called_once_with(candidate)

    @mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
    @mock.patch("mbed_devices.mbed_devices._build_device")
    def test_skips_candidates_without_a_target(self, _build_device, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        _build_device.side_effect = NoTargetForCandidate
        detect_candidate_devices.return_value = [candidate]
        self.assertEqual(get_connected_devices(), [])
        _build_device.assert_called_once_with(candidate)


class TestBuildDevice(TestCase):
    @mock.patch("mbed_devices.mbed_devices._get_mbed_target_for_candidate")
    def test_converts_candidate_to_device(self, _get_mbed_target_for_candidate):
        candidate = CandidateDeviceFactory()
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


class TestGetMbedTargetForCandidate(TestCase):
    @mock.patch("mbed_devices.mbed_devices.get_target_by_product_code")
    @mock.patch("mbed_devices.mbed_devices.extract_product_code")
    def test_uses_product_code_to_fetch_target(self, extract_product_code, get_target_by_product_code):
        candidate = CandidateDeviceFactory()
        self.assertEqual(_get_mbed_target_for_candidate(candidate), get_target_by_product_code.return_value)
        extract_product_code.assert_called_once_with(candidate)
        get_target_by_product_code.assert_called_once_with(extract_product_code.return_value)

    @mock.patch("mbed_devices.mbed_devices.get_target_by_product_code")
    @mock.patch("mbed_devices.mbed_devices.extract_product_code")
    def test_raises_when_product_code_cannot_be_extracted(self, extract_product_code, get_target_by_product_code):
        candidate = CandidateDeviceFactory()
        extract_product_code.side_effect = MissingProductCode
        with self.assertRaises(NoTargetForCandidate):
            _get_mbed_target_for_candidate(candidate)
        get_target_by_product_code.assert_not_called()

    @mock.patch("mbed_devices.mbed_devices.get_target_by_product_code")
    @mock.patch("mbed_devices.mbed_devices.extract_product_code")
    def test_raises_when_target_not_found(self, extract_product_code, get_target_by_product_code):
        candidate = CandidateDeviceFactory()
        get_target_by_product_code.side_effect = UnknownTarget
        with self.assertRaises(NoTargetForCandidate):
            _get_mbed_target_for_candidate(candidate)
