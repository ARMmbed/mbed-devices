#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock

from mbed_targets import MbedTarget
from mbed_targets.exceptions import MbedTargetsError

from tests.factories import CandidateDeviceFactory
from mbed_devices.device import Device
from mbed_devices._internal.exceptions import NoTargetForCandidate

from mbed_devices.mbed_devices import get_connected_devices
from mbed_devices.exceptions import DeviceLookupFailed


@mock.patch("mbed_devices.mbed_devices.detect_candidate_devices")
@mock.patch("mbed_devices.mbed_devices.resolve_target")
class TestGetConnectedDevices(TestCase):
    def test_builds_devices_from_candidates(self, resolve_target, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        detect_candidate_devices.return_value = [candidate]

        identified_devices, unidentified_devices = get_connected_devices()
        self.assertEqual(
            identified_devices,
            [
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_target=resolve_target.return_value,
                )
            ],
        )
        self.assertEqual(unidentified_devices, [])
        resolve_target.assert_called_once_with(candidate)

    @mock.patch.object(MbedTarget, "from_offline_target_entry")
    def test_skips_candidates_without_a_target(self, mbed_target, resolve_target, detect_candidate_devices):
        candidate = CandidateDeviceFactory()
        resolve_target.side_effect = NoTargetForCandidate
        detect_candidate_devices.return_value = [candidate]
        mbed_target.return_value = None

        identified_devices, unidentified_devices = get_connected_devices()
        self.assertEqual(identified_devices, [])
        self.assertEqual(
            unidentified_devices,
            [
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_target=None,
                )
            ],
        )

    def test_raises_device_lookup_failed_on_internal_error(self, resolve_target, detect_candidate_devices):
        resolve_target.side_effect = MbedTargetsError
        detect_candidate_devices.return_value = [CandidateDeviceFactory()]

        with self.assertRaises(DeviceLookupFailed):
            get_connected_devices()
