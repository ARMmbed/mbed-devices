"""Defines a USB Device ID descriptor."""

import re
from enum import Enum
from typing import Optional, Pattern, Any, List

from mbed_devices._internal.utils.python_helpers import named_tuple_with_defaults
from mbed_devices._internal.windows.component_descriptor_utils import is_undefined_data_object

KEY_UID = "UID"
KEY_RAW_UID = "RAW_UID"


class USBIdentifierToken(Enum):
    """Tokens used in the device Id field.

    See https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
    """

    VID = 1
    PID = 2
    REV = 3
    MI = 4

    @property
    def pattern(self) -> Pattern:
        """Gets the regex pattern for the corresponding part."""
        return re.compile(f"^{self.name}_(.*)$")

    @staticmethod
    def get_patterns_dict() -> dict:
        """Returns a dictionary of all the regexes."""
        return {p: p.pattern for p in USBIdentifierToken}


class UsbIdentifier(
    named_tuple_with_defaults(  # type:ignore
        typename="UsbIdentifier",
        field_names=[KEY_UID, KEY_RAW_UID] + [part.name for part in USBIdentifierToken],
        defaults=[None] * (len(USBIdentifierToken) + 2),
    )
):
    """Object describing the different elements present in a the device Id."""

    def get(self, key: USBIdentifierToken) -> str:
        """Returns the value corresponding to a specific token."""
        return str(self.__getattribute__(key.name))

    @property
    def uid(self) -> str:
        """Gets the USB ID."""
        return str(self.__getattribute__(KEY_UID))

    @property
    def raw_uid(self) -> str:
        """Gets the USB id (raw form as it can be a combination of other elements e.g. 8&3432E179&0&000)."""
        return str(self.__getattribute__(KEY_RAW_UID))

    @property
    def product_id(self) -> str:
        """Returns the product id field."""
        return self.get(USBIdentifierToken.PID)

    @property
    def vendor_id(self) -> str:
        """Returns the product id field."""
        return self.get(USBIdentifierToken.VID)

    def __eq__(self, other: Any) -> bool:
        """States whether the other id equals to self."""
        if not other or not isinstance(other, UsbIdentifier):
            return False
        if self.is_undefined:
            return other.is_undefined
        return all(
            [
                self.raw_uid == other.raw_uid or self.uid == other.uid,
                self.product_id == other.product_id,
                self.vendor_id == other.vendor_id,
            ]
        )

    def __hash__(self) -> int:
        """Generates a hash."""
        return hash(self.uid) + hash(self.get(USBIdentifierToken.PID)) + hash(self.get(USBIdentifierToken.VID))

    @property
    def is_undefined(self) -> bool:
        """States whether none of the elements present in DeviceId were defined."""
        return is_undefined_data_object(self)


class Win32DeviceIdParser:
    """Parser of a standard Win32 device ID.

    See https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
    """

    def parse_uid(self, raw_id: str) -> str:
        """Parses the UID value.

        For some boards (e.g. ST boards), the ID may contain other information that we are not interested in.
        This method try to retrieve the actual ID.
        """
        id_elements = raw_id.split("&")
        return id_elements[1 if len(id_elements) > 1 else 0]

    def record_id_element(self, element: str, valuable_information: dict, patterns_dict: dict) -> None:
        """Stores recognised parts of the device ID based on patterns defined."""
        for k, p in patterns_dict.items():
            match = p.fullmatch(element)
            if match:
                valuable_information[k.name] = match.group(1)

    def split_id_elements(self, parts: List[str]) -> dict:
        """Splits the different elements of an Device ID."""
        information = dict()
        information[KEY_RAW_UID] = parts[-1]
        information[KEY_UID] = self.parse_uid(information[KEY_RAW_UID])
        other_elements = parts[-2].split("&")
        patterns_dict = USBIdentifierToken.get_patterns_dict()
        for element in other_elements:
            self.record_id_element(element, information, patterns_dict)
        return information

    def parse(self, id_string: Optional[str]) -> "UsbIdentifier":
        r"""Parses the device id string and retrieves the different elements of interest.

        See https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
         Format: <device-ID>\<instance-specific-ID>
         Ex. `USB\VID_2109&PID_8110\5&376ABA2D&0&21`
          - `<device-ID>`: `USB\VID_2109&PID_8110`
          - `<instance-specific-ID>`: `5&376ABA2D&0&21`
        [Device instance IDs](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/device-instance-ids)
        -> [Device IDs](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/device-ids)
        -> [Hardware IDs](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/hardware-ids)
        -> [Device identifier formats](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/device-identifier-formats)  # noqa: E501
        -> [Identifiers for USB](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/identifiers-for-usb-devices)
         - [Standard USB Identifiers](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers)
         - [Special USB Identifiers](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/special-usb-identifiers)
          - [Instance specific ID](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/instance-ids)

        Returns:
            corresponding DeviceIdInformation.
        """
        if not id_string or len(id_string.strip()) == 0:
            return UsbIdentifier()
        parts = id_string.split("\\")
        if len(parts) < 2:
            return UsbIdentifier()
        return UsbIdentifier(**self.split_id_elements(parts))


def parse_device_id(id_string: Optional[str]) -> UsbIdentifier:
    """Parses the device id string and retrieves the different elements of interest.

    See https://docs.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
    """
    return Win32DeviceIdParser().parse(id_string)