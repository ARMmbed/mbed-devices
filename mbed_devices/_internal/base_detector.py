"""Interface for device detectors."""
from abc import ABC, abstractmethod
from typing import List

from mbed_devices._internal.candidate import Candidate


class DeviceDetector(ABC):
    """Object in charge of finding USB devices."""

    @abstractmethod
    def find_candidates(self) -> List[Candidate]:
        """Returns Candidates."""
        pass
