"""API for listing devices."""
from mbed_devices.device import Device

from typing import List


def list_devices() -> List[Device]:
    """Lists devices connected to the host machine."""
    return list()
