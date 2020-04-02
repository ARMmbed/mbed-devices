#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""API for listing devices."""

from mbed_targets.exceptions import MbedTargetsError

from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.resolve_target import resolve_target
from mbed_devices._internal.exceptions import NoTargetForCandidate

from mbed_devices.device import ConnectedDevices
from mbed_devices.exceptions import DeviceLookupFailed


def get_connected_devices() -> ConnectedDevices:
    """Returns Mbed Devices connected to host computer.

    Connected devices which have been identified as Mbed Targets and also connected devices which are potentially
    Mbed Targets (but not could not be identified in the database) are returned.

    Raises:
        DeviceLookupFailed: If there is a problem with the process of identifying Mbed Targets from connected devices.
    """
    connected_devices = ConnectedDevices()

    for candidate_device in detect_candidate_devices():
        try:
            mbed_target = resolve_target(candidate_device)
        except NoTargetForCandidate:
            mbed_target = None
        except MbedTargetsError as err:
            raise DeviceLookupFailed("A problem occurred when looking up Mbed Targets for connected devices.") from err

        connected_devices.add_device(candidate_device, mbed_target)

    return connected_devices
