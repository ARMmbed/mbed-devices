"""Defines a Disk drive."""

from typing import NamedTuple, cast

from mbed_devices._internal.windows.component_descriptor import ComponentDescriptor


class DiskDriveMsdnDefinition(NamedTuple):
    """Msdn definition of a disk drive.

    See https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-diskdrive
    """

    Availability: int
    BytesPerSector: int
    Capabilities: list
    CapabilityDescriptions: list
    Caption: str
    CompressionMethod: str
    ConfigManagerErrorCode: int
    ConfigManagerUserConfig: bool
    CreationClassName: str
    DefaultBlockSize: int
    Description: str
    DeviceID: str
    ErrorCleared: bool
    ErrorDescription: str
    ErrorMethodology: str
    FirmwareRevision: str
    Index: int
    InstallDate: int
    InterfaceType: str
    LastErrorCode: int
    Manufacturer: str
    MaxBlockSize: int
    MaxMediaSize: int
    MediaLoaded: bool
    MediaType: str
    MinBlockSize: int
    Model: str
    Name: str
    NeedsCleaning: bool
    NumberOfMediaSupported: int
    Partitions: int
    PNPDeviceID: str
    PowerManagementCapabilities: list
    PowerManagementSupported: bool
    SCSIBus: int
    SCSILogicalUnit: int
    SCSIPort: int
    SCSITargetId: int
    SectorsPerTrack: int
    SerialNumber: str
    Signature: int
    Size: int
    Status: str
    StatusInfo: int
    SystemCreationClassName: str
    SystemName: str
    TotalCylinders: int
    TotalHeads: int
    TotalSectors: int
    TotalTracks: int
    TracksPerCylinder: int


class DiskDrive(ComponentDescriptor):
    """Disk Drive as defined in Windows API.

    See https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-diskdrive
    """

    def __init__(self) -> None:
        """Initialiser."""
        super().__init__(DiskDriveMsdnDefinition, win32_class_name="Win32_DiskDrive")

    @property
    def component_id(self) -> str:
        """Returns the device id field."""
        return cast(str, self.get("DeviceID"))
