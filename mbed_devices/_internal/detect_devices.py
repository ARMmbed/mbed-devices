"""Detect Mbed devices connected to host computer."""
import platform
from typing import List

from mbed_devices._internal.candidate import Candidate
from mbed_devices._internal.base_detector import DeviceDetector


def get_detector_for_current_os() -> DeviceDetector:
    """Returns DeviceDetector for current operating system."""
    if platform.system() == "Windows":
        from mbed_devices._internal.windows.device_detector import WindowsDeviceDetector

        return WindowsDeviceDetector()
    if platform.system() == "Linux":
        from mbed_devices._internal.linux.device_detector import LinuxDeviceDetector

        return LinuxDeviceDetector()
    else:
        from mbed_devices._internal.darwin.device_detector import DarwinDeviceDetector

        return DarwinDeviceDetector()


def detect_devices() -> List[Candidate]:
    """Returns Devices connected to host computer."""
    # TODO:
    # - map Candidates to Devices
    detector = get_detector_for_current_os()
    candidates = detector.find_candidates()
    return candidates
