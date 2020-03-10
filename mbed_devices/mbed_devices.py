"""API for listing devices."""
from typing import Iterable

from mbed_devices.device import Device
from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.resolve_target import resolve_target, NoTargetForCandidate
from mbed_targets import DatabaseMode


def get_connected_devices(mode: DatabaseMode = DatabaseMode.AUTO) -> Iterable[Device]:
    """Returns Mbed Devices connected to host computer."""
    devices = []
    for candidate in detect_candidate_devices():
        try:
            target = resolve_target(candidate=candidate, mode=mode)
            devices.append(
                Device(
                    serial_port=candidate.serial_port,
                    serial_number=candidate.serial_number,
                    mount_points=candidate.mount_points,
                    mbed_target=target,
                )
            )
        except NoTargetForCandidate:
            pass
    return devices
