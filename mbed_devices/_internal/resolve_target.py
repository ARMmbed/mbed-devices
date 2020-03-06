"""Resolve targets for CandidateDevice.

Filesystem access is slow - this module does its best to do it lazily.
"""
import functools
import itertools
import pathlib
from typing import Callable, Iterable, List
from mbed_targets import MbedTarget, UnknownTarget, get_target_by_product_code, get_target_by_online_id

from mbed_devices._internal.htm_file import HTMFileContentsParser, OnlineId
from mbed_devices._internal.candidate_device import CandidateDevice


class NoTargetForCandidate(Exception):
    """Raised when target cannot be determined for a candidate."""


def resolve_target(candidate: CandidateDevice) -> MbedTarget:
    """Resolves target for given CandidateDevice if possible.

    Currently, the mechanism for resolving targets relies on existence of HTM files in devices mass storage.
    The specification of those HTM files is that they redirect to devices product page on os.mbed.com.
    Information about Mbed Enabled requirements: https://www.mbed.com/en/about-mbed/mbed-enabled/requirements/
    """
    return _resolve_target_using_file_contents(_get_all_htm_files_contents(candidate.mount_points))


def _resolve_target_using_file_contents(all_files_contents: Iterable[str]) -> MbedTarget:
    try:
        target_resolver = _build_target_resolver(all_files_contents)
    except UnableToBuildResolver:
        raise NoTargetForCandidate

    try:
        return target_resolver()
    except UnknownTarget:
        raise NoTargetForCandidate


class UnableToBuildResolver(Exception):
    """Raised when theres not enough information on the candidate to build a target resolver."""


def _build_target_resolver(all_files_contents: Iterable[str]) -> Callable:
    try:
        product_code = _extract_product_code(all_files_contents)
        return functools.partial(get_target_by_product_code, product_code)
    except ProductCodeNotFound:
        pass

    try:
        online_id = _extract_online_id(all_files_contents)
        return functools.partial(get_target_by_online_id, slug=online_id.device_slug, target_type=online_id.device_type)
    except OnlineIdNotFound:
        raise UnableToBuildResolver


class ProductCodeNotFound(Exception):
    """Raised when product code is not found in htm files."""


def _extract_product_code(all_files_contents: Iterable[str]) -> str:
    for contents in all_files_contents:
        product_code = HTMFileContentsParser(contents).product_code
        if product_code:
            return product_code
    raise ProductCodeNotFound


class OnlineIdNotFound(Exception):
    """Raised when online id is not found in htm files."""


def _extract_online_id(all_files_contents: Iterable[str]) -> OnlineId:
    for contents in all_files_contents:
        online_id = HTMFileContentsParser(contents).online_id
        if online_id:
            return online_id
    raise OnlineIdNotFound


def _get_all_htm_files_contents(directories: Iterable[pathlib.Path]) -> List[str]:
    """Yields all htm files contents found in the list of given directories."""
    extensions = [".htm", ".HTM"]
    files_in_each_directory = (directory.iterdir() for directory in directories)
    all_files = itertools.chain.from_iterable(files_in_each_directory)
    return [file.read_text() for file in all_files if file.suffix in extensions]
