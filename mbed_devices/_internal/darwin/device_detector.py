"""Device detector for Darwin."""
from typing import Generator
from mbed_devices._internal.base_detector import DeviceDetector
from mbed_devices._internal.candidate import Candidate


class DarwinDeviceDetector(DeviceDetector):
    """Darwin specific implementation of device detection."""

    def find_candidates(self) -> Generator[Candidate, None, None]:
        """Return a generator of Candidates."""
        pass
