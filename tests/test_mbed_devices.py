from unittest import TestCase, mock

from tests.factories import CandidateDeviceFactory
from mbed_devices.device import Device
from mbed_devices._internal.resolve_target import NoTargetForCandidate
from mbed_devices.mbed_devices import get_connected_devices
from mbed_targets import DatabaseMode


class TestGetConnectedDevices(TestCase):
    @mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
    @mock.patch("mbed_devices.mbed_devices.resolve_target")
    def test_builds_devices_from_candidates(self, resolve_target, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        mode = DatabaseMode.ONLINE
        detect_candidate_devices.return_value = [candidate]
        self.assertEqual(
            get_connected_devices(mode),
            [
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_target=resolve_target.return_value,
                )
            ],
        )
        resolve_target.assert_called_once_with(candidate=candidate, mode=mode)

    @mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
    @mock.patch("mbed_devices.mbed_devices.resolve_target")
    def test_skips_candidates_without_a_target(self, resolve_target, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        resolve_target.side_effect = NoTargetForCandidate
        detect_candidate_devices.return_value = [candidate]
        self.assertEqual(get_connected_devices(), [])
