"""Device detector for Darwin."""
import logging
import pathlib
import re
from typing import List, Optional
from typing_extensions import TypedDict
from mbed_devices._internal.base_detector import DeviceDetector
from mbed_devices._internal.candidate import Candidate
from mbed_devices._internal.darwin import system_profiler, ioreg, diskutil
from mbed_tools_lib.logging import log_exception


logger = logging.getLogger(__name__)


class CandidateData(TypedDict):
    """CandidateData calculated from USBDevice."""

    vendor_id: str
    product_id: str
    serial_number: str
    mount_points: List[pathlib.Path]
    serial_port: Optional[str]


class InvalidCandidateDataError(ValueError):
    """Raised when Candidate was given invalid data and it cannot be built."""

    pass


class DarwinDeviceDetector(DeviceDetector):
    """Darwin specific implementation of device detection."""

    def find_candidates(self) -> List[Candidate]:
        """Return a list of Candidates."""
        usb_devices_data = system_profiler.get_end_usb_devices_data()
        candidates = []
        for device_data in usb_devices_data:
            logging.debug(f"Building from: {device_data}.")
            try:
                candidate = _build_candidate(device_data)
            except InvalidCandidateDataError:
                pass
            else:
                logging.debug(f"Built candidate: {candidate}.")
                candidates.append(candidate)
        return candidates


def _build_candidate(device_data: system_profiler.USBDevice) -> Candidate:
    assembled_data = _assemble_candidate_data(device_data)
    try:
        return Candidate(**assembled_data)
    except ValueError as e:
        log_exception(logger, e)
        raise InvalidCandidateDataError


def _assemble_candidate_data(device_data: system_profiler.USBDevice) -> CandidateData:
    return {
        "vendor_id": _format_vendor_id(device_data.get("vendor_id", "")),
        "product_id": device_data.get("product_id", ""),
        "serial_number": device_data.get("serial_num", ""),
        "mount_points": _get_mount_points(device_data),
        "serial_port": _get_serial_port(device_data),
    }


def _format_vendor_id(vendor_id: str) -> str:
    """Strips vendor name from vendor_id field.

    Example:
        >>> _format_vendor_id("0x1234 (Nice Vendor Inc.)")  # "0x1234"
    """
    return vendor_id.split(maxsplit=1)[0]


def _get_mount_points(device_data: system_profiler.USBDevice) -> List[pathlib.Path]:
    """Returns mount points for a given device, empty list if device has no mount points."""
    storage_identifiers = [media["bsd_name"] for media in device_data.get("Media", []) if "bsd_name" in media]
    mount_points = []
    for storage_identifier in storage_identifiers:
        mount_point = diskutil.get_mount_point(storage_identifier)
        if mount_point:
            mount_points.append(pathlib.Path(mount_point))
        else:
            logging.debug(f"Couldn't determine mount point for device id: {storage_identifier}.")
    return mount_points


def _get_serial_port(device_data: system_profiler.USBDevice) -> Optional[str]:
    """Returns serial port for a given device, None if serial port cannot be determined."""
    device_name = device_data.get("_name")
    if not device_name:
        logging.debug('Missing "_name" in "{device_data}", which is required for ioreg name.')
        return None

    location_id = device_data.get("location_id")
    if not location_id:
        logging.debug('Missing "location_id" in "{device_data}", which is required for ioreg name.')
        return None

    ioreg_name = _build_ioreg_device_name(device_name=device_name, location_id=location_id)
    serial_port = ioreg.get_io_dialin_device(ioreg_name)
    return serial_port


def _build_ioreg_device_name(device_name: str, location_id: str) -> str:
    """Converts extracted `_name` and `location_id` attributes from `system_profiler` to a valid ioreg device name.

    `system_profiler` utility returns location ids in the form of `0xNNNNNNN`, with an optional suffix of ` / N`.

    Example:
        >>> _build_ioreg_device_name("STM32 Foo", "0x123456 / 2")
        "STM32 Foo@123456"
    """
    pattern = r"""
    0x                # hexadecimal prefix
    (?P<location>\d+) # location (i.e.: "123456" in "0x123456 / 2")
    (\s\/\s\d+)?      # suffix of location (" / 14")
    """
    match = re.match(pattern, location_id, re.VERBOSE)
    if match:
        return f"{device_name}@{match['location']}"
    else:
        return device_name
