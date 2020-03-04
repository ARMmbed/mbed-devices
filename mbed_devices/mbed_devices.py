"""API for listing devices."""
from typing import Iterable, Optional
from concurrent.futures import ThreadPoolExecutor
from mbed_targets import MbedTarget, get_target_by_product_code
from mbed_tools_lib.exceptions import ToolsError

from mbed_devices.device import Device
from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_devices._internal.detect_candidate_devices import detect_candidate_devices
from mbed_devices._internal.product_code import extract_product_code, MissingProductCode


def get_connected_devices() -> Iterable[Device]:
    """Returns Mbed Devices connected to host computer."""
    with ThreadPoolExecutor() as executor:
        return [device for device in executor.map(_build_device, detect_candidate_devices())]


def _build_device(candidate: CandidateDevice) -> Device:
    return Device(
        serial_port=candidate.serial_port,
        serial_number=candidate.serial_number,
        mount_points=candidate.mount_points,
        mbed_target=_get_mbed_target_for_candidate(candidate),
    )


def _get_mbed_target_for_candidate(candidate: CandidateDevice) -> Optional[MbedTarget]:
    try:
        product_code = extract_product_code(candidate)
    except MissingProductCode:
        return None

    try:
        return get_target_by_product_code(product_code)
    except ToolsError:
        return None
