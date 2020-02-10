"""Defines Candidate model used for device detection."""
from typing import Optional, NamedTuple
from pathlib import Path


class Candidate(NamedTuple):
    """Device connected to the host computer."""

    is_mounted: bool
    product_id: str
    vendor_id: str
    mount_point: Optional[Path]
    serial_port: str
