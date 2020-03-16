"""API for listing devices."""
from typing import Iterable

from mbed_targets.exceptions import MbedTargetsError

from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.resolve_target import resolve_target
from mbed_devices._internal.exceptions import NoTargetForCandidate

from mbed_devices.device import Device
from mbed_devices.exceptions import DeviceLookupFailed


def get_connected_devices() -> Iterable[Device]:
    """Returns Mbed Devices connected to host computer."""
    devices = []
    for candidate_device in detect_candidate_devices():
        try:
            devices.append(_build_device(candidate_device))
        except NoTargetForCandidate:
            pass
    return devices


def _build_device(candidate: CandidateDevice) -> Device:
    try:
        return Device(
            serial_port=candidate.serial_port,
            serial_number=candidate.serial_number,
            mount_points=candidate.mount_points,
            mbed_target=resolve_target(candidate),
        )
    except MbedTargetsError as err:
        raise DeviceLookupFailed("Failed to find a connected device.") from err
