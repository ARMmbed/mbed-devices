"""Facilitates parsing MBED.HTM files found on the Mbed devices.

For legacy reasons, we support many flavours of MBED.HTM files. The list of examples below is not exhaustive,
as at the time of writing it's not feasible to gather all examples in one place.
Its main goal is to provide a taste of different flavours of HTM files we need to support.

    <!-- mbed Microcontroller Website and Authentication Shortcut -->
    <!-- Version: 0200 Build: Feb  3 2014 14:03:10 -->
    <html>
    <head>
    <meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code=0710020092566DA9AD33FB84"/>
    <title>mbed Website Shortcut</title>
    </head>
    <body></body>
    </html>

---

    <!doctype html>
    <!-- mbed Platform Website and Authentication Shortcut -->
    <html>
    <head>
    <meta charset="utf-8">
    <title>mbed Website Shortcut</title>
    </head>
    <body>
    <script>
    window.location.replace("https://mbed.org/device/?code=460000000988254a00000000000000000000000097969902?version=0253?target_id=00000000000000000000000000000000");
    </script>
    </body>
    </html>

---

    <!-- mbed Microcontroller Website and Authentication Shortcut -->
    <html>
    <head>
    <meta http-equiv="refresh" content="0; url=http://mbed.org/start?auth=101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9&loader=11972&firmware=16457&configuration=4" />  # noqa
    <title>mbed Website Shortcut</title>
    </head>
    <body></body>
    </html>
"""
import pathlib
import re
from typing import Type, TypeVar, Optional


T = TypeVar("T", bound="HTMFileContentsParser")


class HTMFileContentsParser:
    """Extracts information from MBED.HTM file contents."""

    def __init__(self, file_contents: str) -> None:
        """Initialises HTMFileContentsParser with file contents."""
        self._file_contents = file_contents

    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        """Initialises HTMFileContentsParser with file contents read from given path."""
        return cls(file_contents=pathlib.Path(file_path).read_text())

    @property
    def code(self) -> Optional[str]:
        """Returns code parsed from the file contents, None if not found."""
        regex = r"""
            (?:code|auth)=          # attribute name
            (?P<code>[a-fA-F0-9]+)  # code identifier
        """
        match = re.search(regex, self._file_contents, re.VERBOSE)
        if match:
            return match["code"]
        return None
