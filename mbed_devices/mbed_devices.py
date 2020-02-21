"""API for listing devices."""
from typing import Iterable

from mbed_devices.device import Device


def get_connected_devices() -> Iterable[Device]:
    """Lists devices connected to the host machine."""
    return []
