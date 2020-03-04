"""Defines a USB hub."""

from typing import NamedTuple, Dict, List, cast, Optional, Set, Generator

from mbed_devices._internal.windows.component_descriptor import ComponentDescriptor, ComponentDescriptorWrapper
from mbed_devices._internal.windows.usb_device_identifier import parse_device_id, UsbIdentifier
from mbed_devices._internal.windows.usb_controller import UsbController
from mbed_devices._internal.windows.device_instance_id import get_children_instance_id


class UsbHubMsdnDefinition(NamedTuple):
    """Msdn definition of a Usb hub.

    See https://docs.microsoft.com/en-gb/previous-versions/windows/desktop/cimwin32a/win32-usbhub?redirectedfrom=MSDN
    See also https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/cim-usbdevice
    """

    Availability: int
    Caption: str
    ClassCode: int
    ConfigManagerUserConfig: bool
    CreationClassName: str
    CurrentAlternateSettings: list
    CurrentConfigValue: int
    Description: str
    ErrorCleared: bool
    ErrorDescription: str
    GangSwitched: bool
    InstallDate: int
    LastErrorCode: int
    NumberOfConfigs: int
    NumberOfPorts: int
    PNPDeviceID: str
    PowerManagementCapabilities: list
    PowerManagementSupported: bool
    ProtocolCode: int
    Status: str
    StatusInfo: int
    SubclassCode: int
    SystemCreationClassName: str
    SystemName: str
    USBVersion: int
    ConfigManagerErrorCode: int
    DeviceID: str
    Name: str


class UsbHub(ComponentDescriptor):
    """USB Hub as defined in Windows API.

    See https://docs.microsoft.com/en-gb/previous-versions/windows/desktop/cimwin32a/win32-usbhub?redirectedfrom=MSDN
    Seems similar to https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/cim-usbhub
    """

    def __init__(self) -> None:
        """Initialiser."""
        super().__init__(UsbHubMsdnDefinition, win32_class_name="Win32_USBHub")

    @property
    def component_id(self) -> str:
        """Returns the device id field."""
        return cast(str, self.get("DeviceID"))

    @property
    def pnp_id(self) -> str:
        """Returns the plug and play id field."""
        return cast(str, self.get("PNPDeviceID"))


class SystemUsbDeviceInformation:
    """Usb Hub cache for this system.

    On Windows, each interface e.g. Composite, Mass storage, Port is defined as
    a separate independent UsbHub although they are related to the same device.
    This cache tries to reduce the list of UsbHubs to only genuinely different devices.
    """

    def __init__(self) -> None:
        """Initialiser."""
        self.cache: Optional[Dict[UsbIdentifier, List[UsbHub]]] = None
        self.ids_cache: Optional[Set[UsbIdentifier]] = None

    def _list_usb_controller_ids(self) -> List[UsbIdentifier]:
        return cast(
            List[UsbIdentifier],
            [
                parse_device_id(cast(UsbController, usbc).component_id)
                for usbc in ComponentDescriptorWrapper(UsbController).element_generator()
            ],
        )

    def _iterate_over_hubs(self) -> Generator["ComponentDescriptor", None, None]:
        return ComponentDescriptorWrapper(UsbHub).element_generator()

    def _populate_id_cache_with_non_serialnumbers(self) -> None:
        if not self.cache or not self.ids_cache:
            return
        for usb_id in self.cache:
            if usb_id not in self.ids_cache:
                self.ids_cache.add(usb_id)

    def _determine_potential_serial_number(self, usb_device: UsbHub) -> Optional[str]:
        """Fetches the ParentIdPrefix of a USB hub."""
        return get_children_instance_id(usb_device.pnp_id)

    def _load(self) -> None:
        """Populates the cache."""
        self.cache = cast(Dict[UsbIdentifier, List[UsbHub]], dict())
        self.ids_cache = cast(Set[UsbIdentifier], set())
        controllers = self._list_usb_controller_ids()
        for usb_device in self._iterate_over_hubs():
            usb_id = parse_device_id(
                usb_device.component_id, serial_number=self._determine_potential_serial_number(cast(UsbHub, usb_device))
            )
            if usb_id in controllers:
                continue
            entry = self.cache.get(usb_id, list())
            entry.append(cast(UsbHub, usb_device))
            self.cache[usb_id] = entry

            if usb_id.contains_genuine_serial_number():
                self.ids_cache.add(usb_id)
        self._populate_id_cache_with_non_serialnumbers()

    @property
    def usb_devices(self) -> Dict[UsbIdentifier, List[UsbHub]]:
        """Usb devices present in the system."""
        if not self.cache:
            self._load()
        return cast(Dict[UsbIdentifier, List[UsbHub]], self.cache)

    def get_usb_devices(self, uid: UsbIdentifier) -> List[UsbHub]:
        """Gets all USB devices related to an identifier."""
        return self.usb_devices.get(uid, list())

    def usb_device_ids(self) -> List[UsbIdentifier]:
        """Gets system usb device IDs."""
        if not self.ids_cache:
            self._load()
        return cast(List[UsbIdentifier], self.ids_cache)
