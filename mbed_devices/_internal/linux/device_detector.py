"""Defines a device detector for Windows."""
from typing import List

from mbed_devices._internal.base_detector import DeviceDetector
from mbed_devices._internal.candidate import Candidate


class LinuxDeviceDetector(DeviceDetector):
    """Linux specific implementation of device detection."""

    def find_candidates(self) -> List[Candidate]:
        """Return a list of Candidates."""
        pass
