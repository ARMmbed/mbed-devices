"""Defines CandidateDevice model used for device detection."""
from typing import Optional, List
from pathlib import Path


class CandidateDevice:
    """Valid candidate device connected to the host computer.

    We know for a fact that a valid candidate contains certain non-empty fields.
    """

    def __init__(
        self,
        product_id: str,
        vendor_id: str,
        mount_points: List[Path],
        serial_number: str,
        serial_port: Optional[str] = None,
    ) -> None:
        """Validate given values and return a CandidateDevice."""
        try:
            self.product_id = _format_hex(product_id)
        except ValueError:
            raise ValueError('Given "product_id" must be a non-empty hex value.')

        try:
            self.vendor_id = _format_hex(vendor_id)
        except ValueError:
            raise ValueError('Given "vendor_id" must be a non-empty hex value.')

        if not mount_points:
            raise ValueError('Given "mount_points" must be non-empty.')
        self.mount_points = mount_points

        if not serial_number:
            raise ValueError('Given "serial_number" must be non-empty.')
        self.serial_number = serial_number

        self.serial_port = serial_port

    def __eq__(self, other: object) -> bool:
        """Allows comparing two candidates by the value of their attributes."""
        if not isinstance(other, CandidateDevice):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __repr__(self) -> str:
        """Namedtuple-like representation of the instance."""
        values = [f"{k}={v!r}" for (k, v) in self.__dict__.items()]
        return f"CandidateDevice({', '.join(values)})"


def _format_hex(hex_value: str) -> str:
    """Return hex value with a prefix.

    Accepts hex_value in prefixed (0xff) and unprefixed (ff) formats.
    """
    return hex(int(hex_value, 16))
