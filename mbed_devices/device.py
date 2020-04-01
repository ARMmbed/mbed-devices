#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Data model definition for Device and ConnectedDevices."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, Optional, List
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


@dataclass(order=True)
class ConnectedDevices:
    """Definition of connected devices which may be Mbed Targets.

    If a connected device is identified as an Mbed Target by using the HTM file on the USB mass storage device (or
    sometimes by using the serial number), it will be included in the `identified_devices` list.

    However, if the device appears as if it could be an Mbed Target but it has not been possible to find a matching
    entry in the database then it will be included in the `unidentified_devices` list.

    Attributes:
        identified_devices: A list of devices that have been identified as MbedTargets.
        unidentified_devices: A list of devices that could potentially be MbedTargets.
    """

    identified_devices: List[Device] = field(default_factory=list)
    unidentified_devices: List[Device] = field(default_factory=list)
