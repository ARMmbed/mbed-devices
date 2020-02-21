"""Device model definition."""
import pathlib
from typing import NamedTuple, List
from mbed_targets import MbedTarget


class Device(NamedTuple):
    """Definition of an Mbed Device."""

    mbed_target: MbedTarget
    serial_number: str
    serial_port: str
    mount_points: List[pathlib.Path]
