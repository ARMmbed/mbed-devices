"""Device model definition."""
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional
from mbed_targets import MbedTarget


@dataclass(frozen=True, order=True)
class Device:
    """Definition of an Mbed Enabled Device.

    An Mbed Device is always a USB mass storage device, which sometimes also presents a USB serial port.
    A valid Mbed Device must have an MbedTarget associated with it.

    Attributes:
        mbed_target: The MbedTarget associated with this device.
        serial_number: The serial number presented by the device to the USB subsystem.
        serial_port: The serial port presented by this device, could be None.
        mount_points: The filesystem mount points associated with this device.
    """

    mbed_target: MbedTarget
    serial_number: str
    serial_port: Optional[str]
    mount_points: Tuple[Path, ...]
