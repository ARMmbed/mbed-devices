"""Exceptions internal to the package."""

from mbed_tools_lib.exceptions import ToolsError


class SystemException(ToolsError):
    """Exception with regards to the underlying operating system."""


class NoTargetForCandidate(ToolsError):
    """Raised when target cannot be determined for a candidate."""
