"""API for listing devices."""
import logging
from typing import Iterable
from mbed_targets import MbedTarget, get_target_by_product_code, UnknownTarget

from mbed_devices.device import Device
from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.product_code import extract_product_code, MissingProductCode


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
    return Device(
        serial_port=candidate.serial_port,
        serial_number=candidate.serial_number,
        mount_points=candidate.mount_points,
        mbed_target=_get_mbed_target_for_candidate(candidate),
    )


class NoTargetForCandidate(Exception):
    """Raised when target cannot be determined for a candidate."""


def _get_mbed_target_for_candidate(candidate: CandidateDevice) -> MbedTarget:
    try:
        product_code = extract_product_code(candidate)
    except MissingProductCode:
        logging.debug(f"Cannot determine product code for {candidate}.")
        raise NoTargetForCandidate

    try:
        return get_target_by_product_code(product_code)
    except UnknownTarget:
        logging.debug(f"Cannot determine target for product code {product_code}.")
        raise NoTargetForCandidate
