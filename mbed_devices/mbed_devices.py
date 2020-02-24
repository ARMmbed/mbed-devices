"""API for listing devices."""
from typing import Iterable
from mbed_targets import MbedTarget

from mbed_devices.device import Device
from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.candidate_device import CandidateDevice


def get_connected_devices() -> Iterable[Device]:
    """Returns Mbed Devices connected to host computer."""
    return [_build_device(candidate) for candidate in detect_candidate_devices()]


def _build_device(candidate: CandidateDevice) -> Device:
    return Device(
        serial_port=candidate.serial_port,
        serial_number=candidate.serial_number,
        mount_points=candidate.mount_points,
        mbed_target=_get_mbed_target_for_candidate(candidate),
    )


def _get_mbed_target_for_candidate(candidate: CandidateDevice) -> MbedTarget:
    return MbedTarget({})
