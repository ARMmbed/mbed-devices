"""Defines a device detector for Windows."""
from typing import List

from mbed_devices._internal.base_detector import DeviceDetector
from mbed_devices._internal.candidate_device import CandidateDevice


class WindowsDeviceDetector(DeviceDetector):
    """Windows specific implementation of device detection."""

    def find_candidates(self) -> List[CandidateDevice]:
        """Return a generator of CandidateDevices."""
        pass
