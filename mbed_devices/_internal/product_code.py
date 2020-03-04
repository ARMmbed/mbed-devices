"""Product code retrieval from CandidateDevice."""
import itertools
import pathlib
from typing import Iterable, List, Optional

from mbed_devices._internal.htm_file import HTMFileContentsParser
from mbed_devices._internal.candidate_device import CandidateDevice
from mbed_tools_lib.exceptions import ToolsError


class MissingProductCode(ToolsError):
    """Raised when product code cannot be established."""

    pass


def extract_product_code(candidate: CandidateDevice) -> str:
    """Orchestrates extracting product code from *.htm files on device."""
    htm_files = _get_all_htm_files(candidate.mount_points)
    product_codes = (_extract_product_code_from_htm_file(htm_file) for htm_file in htm_files)
    try:
        return next(product_code for product_code in product_codes if product_code)
    except StopIteration:
        raise MissingProductCode(f"Cannot extract product code from {candidate}.")


def _get_all_htm_files(directories: List[pathlib.Path]) -> Iterable[pathlib.Path]:
    """Yields all htm files found in the list of given directories."""
    extensions = [".htm", ".HTM"]
    files_in_each_directory = (directory.iterdir() for directory in directories)
    all_files = itertools.chain.from_iterable(files_in_each_directory)
    return (file for file in all_files if file.suffix in extensions)


def _extract_product_code_from_htm_file(file: pathlib.Path) -> Optional[str]:
    return HTMFileContentsParser.from_file(str(file)).product_code
