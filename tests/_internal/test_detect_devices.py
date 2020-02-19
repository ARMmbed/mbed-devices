from unittest import TestCase
from mbed_devices._internal.detect_devices import get_detector_for_current_os
from tests.markers import windows_only, darwin_only, linux_only


class TestGetDetectorForCurrentOS(TestCase):
    @windows_only
    def test_windows_uses_correct_module(self):
        from mbed_devices._internal.windows.device_detector import WindowsDeviceDetector

        self.assertIsInstance(get_detector_for_current_os(), WindowsDeviceDetector)

    @darwin_only
    def test_darwin_uses_correct_module(self):
        from mbed_devices._internal.darwin.device_detector import DarwinDeviceDetector

        self.assertIsInstance(get_detector_for_current_os(), DarwinDeviceDetector)

    @linux_only
    def test_linux_uses_correct_module(self):
        from mbed_devices._internal.linux.device_detector import LinuxDeviceDetector

        self.assertIsInstance(get_detector_for_current_os(), LinuxDeviceDetector)
