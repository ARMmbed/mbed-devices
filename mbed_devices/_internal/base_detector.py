"""Interface for device detectors."""
from abc import ABC, abstractmethod
from typing import Generator

from mbed_devices._internal.candidate import Candidate


class DeviceDetector(ABC):
    """Object in charge of finding USB devices."""

    @abstractmethod
    def find_candidates(self) -> Generator[Candidate, None, None]:
        """Returns a generator of Candidates."""
        pass
