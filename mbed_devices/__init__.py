#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""mbed-devices provides an API to detect any Mbed OS devices connected to the host computer.

It is expected that this package will be used by developers of Mbed OS tooling rather than by users of Mbed OS.
This package uses the https://github.com/ARMmbed/mbed-targets interface to identify valid Mbed Enabled Devices.
Please see the documentation for mbed-targets for information on configuration options.

For the command line interface to the API see the package https://github.com/ARMmbed/mbed-tools
"""
from mbed_devices._version import __version__
from mbed_devices.mbed_devices import get_connected_devices
from mbed_devices.device import Device
from mbed_devices import exceptions
