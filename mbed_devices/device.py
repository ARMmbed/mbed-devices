"""Device model definition."""
from typing import NamedTuple

from mbed_targets import MbedTarget
from mbed_devices.interface_firmware import InterfaceFirmware


class Device(NamedTuple):
    """Definition of an Mbed Device."""

    mount_point: str
    identifier: str
    interface_firmware: InterfaceFirmware
    interface_firmware_version: str
    mbed_target: MbedTarget
    serial_port: str
