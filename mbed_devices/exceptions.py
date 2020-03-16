"""Public exceptions raised by the package."""
from mbed_tools_lib.exceptions import ToolsError


class MbedDevicesError(ToolsError):
    """Base public exception for the mbed-devices package."""


class DeviceLookupFailed(MbedDevicesError):
    """Failed to look up data associated with the device."""
