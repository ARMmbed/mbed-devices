"""Resolve targets for `CandidateDevice`.

Resolving a target involves looking up an `MbedTarget` from the `mbed-targets` API, using data found in the "htm file"
located on an "Mbed Enabled" device's USB MSD.

For more information on the mbed-targets package visit https://github.com/ARMmbed/mbed-targets
"""
import itertools
import pathlib

from typing import Iterable, List, Optional

from mbed_targets import MbedTarget, get_target_by_product_code, get_target_by_online_id
from mbed_targets.exceptions import UnknownTarget

from mbed_devices._internal.htm_file import OnlineId, read_online_id, read_product_code
from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_devices._internal.exceptions import NoTargetForCandidate


def resolve_target(candidate: CandidateDevice) -> MbedTarget:
    """Resolves target for a given CandidateDevice.

    This function interrogates CandidateDevice, attempting to establish the best method to resolve an MbedTarget,
    the rules are as follows:

    1. Use product code retrieved from one of HTM files in the mass storage if available.
    2. Use online id retrieved from one of the HTM files in the mass storage if available.
    3. Fallback to product code retrieved from serial number.

    The specification of HTM files is that they redirect to devices product page on os.mbed.com.
    Information about Mbed Enabled requirements: https://www.mbed.com/en/about-mbed/mbed-enabled/requirements/
    """
    all_files_contents = _get_all_htm_files_contents(candidate.mount_points)

    product_code = _extract_product_code(all_files_contents)
    if product_code:
        try:
            return get_target_by_product_code(product_code)
        except UnknownTarget:
            raise NoTargetForCandidate

    online_id = _extract_online_id(all_files_contents)
    if online_id:
        try:
            return get_target_by_online_id(slug=online_id.device_slug, target_type=online_id.device_type)
        except UnknownTarget:
            raise NoTargetForCandidate

    # Product code might be the first 4 characters of the serial number
    try:
        return get_target_by_product_code(candidate.serial_number[:4])
    except UnknownTarget:
        raise NoTargetForCandidate


def _extract_product_code(all_files_contents: Iterable[str]) -> Optional[str]:
    """Return first product code found in files contents, None if not found."""
    for contents in all_files_contents:
        product_code = read_product_code(contents)
        if product_code:
            return product_code
    return None


def _extract_online_id(all_files_contents: Iterable[str]) -> Optional[OnlineId]:
    """Return first online id found in files contents, None if not found."""
    for contents in all_files_contents:
        online_id = read_online_id(contents)
        if online_id:
            return online_id
    return None


def _get_all_htm_files_contents(directories: Iterable[pathlib.Path]) -> List[str]:
    """Yields all htm files contents found in the list of given directories."""
    files_in_each_directory = (directory.iterdir() for directory in directories)
    all_files = itertools.chain.from_iterable(files_in_each_directory)
    return [file.read_text() for file in all_files if _is_htm_file(file)]


def _is_htm_file(file: pathlib.Path) -> bool:
    extensions = [".htm", ".HTM"]
    return file.suffix in extensions and not file.name.startswith(".")
