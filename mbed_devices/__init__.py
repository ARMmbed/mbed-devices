"""Exposes the primary interfaces for the library."""

from mbed_devices._version import __version__
from mbed_devices.mbed_devices import get_connected_devices
from mbed_devices.device import Device
from mbed_devices import exceptions
