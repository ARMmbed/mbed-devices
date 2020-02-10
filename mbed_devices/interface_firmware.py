"""Defines interface firmware model."""

from typing import NamedTuple


class InterfaceFirmware(NamedTuple):
    """Definition of an interface firmware."""

    name: str
    vendor_id: str
