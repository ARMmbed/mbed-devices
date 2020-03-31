#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""API for listing devices."""
from typing import Tuple, List

from mbed_targets.exceptions import MbedTargetsError

from mbed_devices._internal.detect_candidate_devices import CandidateDevice, detect_candidate_devices
from mbed_devices._internal.resolve_target import resolve_target
from mbed_devices._internal.exceptions import NoTargetForCandidate

from mbed_targets import MbedTarget
from mbed_devices.device import Device
from mbed_devices.exceptions import DeviceLookupFailed


def get_connected_devices() -> Tuple[List[Device], List[Device]]:
    """Returns Mbed Devices connected to host computer.

    Returns:
        A tuple containing two lists, the first containing devices identified as Mbed Targets the second those devices
        connected but not identified as Mbed Targets.

    Raises:
        DeviceLookupFailed: TODO: find out when.
    """
    identified_devices = []
    unidentified_devices = []
    for candidate_device in detect_candidate_devices():
        try:
            mbed_target = resolve_target(candidate_device)
        except MbedTargetsError as err:
            raise DeviceLookupFailed("A problem occurred when looking up Mbed Targets for connected devices.") from err
        except NoTargetForCandidate:
            # Empty Mbed Target to ensure rendering is simple
            mbed_target = MbedTarget.from_offline_target_entry({})
            # Keep a list of devices that could not be identified but are Mbed Targets
            unidentified_devices.append(_build_device(candidate_device, mbed_target))
        else:
            # Keep a list of devices that have been identified as Mbed Targets
            identified_devices.append(_build_device(candidate_device, mbed_target))

    return identified_devices, unidentified_devices


def _build_device(candidate_device: CandidateDevice, mbed_target: MbedTarget) -> Device:
    """Construct a device instance from a candidate device and Mbed Target."""
    return Device(
        serial_port=candidate_device.serial_port,
        serial_number=candidate_device.serial_number,
        mount_points=candidate_device.mount_points,
        mbed_target=mbed_target,
    )
