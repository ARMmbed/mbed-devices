"""Defines CandidateDevice model used for device detection."""
import functools

from typing import Optional, List, Any, Sequence
from pathlib import Path


class CandidateDeviceError(ValueError):
    """Base exception raised by a CandidateDevice."""


class USBDescriptorError(CandidateDeviceError):
    """USB descriptor field was not found."""


class FilesystemMountpointError(CandidateDeviceError):
    """Filesystem mount point was not found."""


class DataField:
    """CandidateDevice data attribute descriptor."""

    def __set_name__(self, owner: object, name: str) -> None:
        """Sets the descriptor name, this is called by magic in the owners.__new__ method."""
        self.name = name

    def __get__(self, instance: object, owner: object = None) -> Any:
        """Get the attribute value from the instance."""
        return instance.__dict__.setdefault(self.name, None)


class USBDescriptorHex(DataField):
    """USB descriptor field which cannot be set to an empty value, or an invalid hex value."""

    def __set__(self, instance: object, value: Any) -> None:
        """Prevent setting the descriptor to an empty or invalid hex value."""
        try:
            instance.__dict__[self.name] = _format_hex(value)
        except ValueError:
            raise USBDescriptorError(f"{self.name} cannot be an empty and must be valid hex.")


class USBDescriptorString(DataField):
    """USB descriptor field which cannot be set to an empty value."""

    def __set__(self, instance: object, value: str) -> None:
        """Prevent setting the descriptor to a non-string or empty value."""
        if not value or not isinstance(value, str):
            raise USBDescriptorError(f"{self.name} cannot be an empty field and must be a string.")

        instance.__dict__[self.name] = value


class FilesystemMountpoints(DataField):
    """Data descriptor which must be set to a non-empty list or tuple."""

    def __set__(self, instance: object, value: Sequence) -> None:
        """Prevent setting the descriptor to a non-sequence or empty sequence value."""
        if not value or not isinstance(value, (list, tuple)):
            raise FilesystemMountpointError(f"{self.name} must be set to a non-empty list or tuple.")

        instance.__dict__[self.name] = value


@functools.total_ordering
class CandidateDevice:
    """Valid candidate device connected to the host computer.

    We know for a fact that a valid candidate contains certain non-empty fields.
    """

    product_id = USBDescriptorHex()
    vendor_id = USBDescriptorHex()
    serial_number = USBDescriptorString()
    mount_points = FilesystemMountpoints()

    def __init__(
        self,
        product_id: str,
        vendor_id: str,
        mount_points: List[Path],
        serial_number: str,
        serial_port: Optional[str] = None,
    ) -> None:
        """Validate given values and return a CandidateDevice."""
        self.product_id = product_id
        self.vendor_id = vendor_id
        self.serial_number = serial_number
        self.mount_points = mount_points
        self.serial_port = serial_port

    def __eq__(self, other: object) -> bool:
        """Compare two candidates based on the value of their required attributes."""
        if not isinstance(other, CandidateDevice):
            return NotImplemented

        return (self.serial_number, self.vendor_id, self.product_id) == (
            other.serial_number,
            other.vendor_id,
            other.product_id,
        )

    def __lt__(self, other: object) -> Any:
        """Define < so object is sortable by serial number."""
        if not isinstance(other, CandidateDevice):
            return NotImplemented

        return self.serial_number < other.serial_number

    def __hash__(self) -> int:
        """Create a hash consistent with the equality comparison operator."""
        return hash(self.serial_number) ^ hash(self.vendor_id) ^ hash(self.product_id)

    def __repr__(self) -> str:
        """Namedtuple-like representation of the instance."""
        values = [f"{k}={v!r}" for (k, v) in self.__dict__.items()]
        return f"CandidateDevice({', '.join(values)})"


def _format_hex(hex_value: str) -> str:
    """Return hex value with a prefix.

    Accepts hex_value in prefixed (0xff) and unprefixed (ff) formats.
    """
    return hex(int(hex_value, 16))
