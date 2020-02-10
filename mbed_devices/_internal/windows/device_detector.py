"""Defines a device detector for Windows."""
from typing import Generator

from mbed_devices._internal.base_detector import DeviceDetector
from mbed_devices._internal.candidate import Candidate


class WindowsDeviceDetector(DeviceDetector):
    """Windows specific implementation of device detection."""

    def find_candidates(self) -> Generator[Candidate, None, None]:
        """Return a generator of Candidates."""
        pass
