"""Data aggregation about a disk on Windows.

On Windows, information about disk drive is scattered around Physical disks,
Partitions and Logical Drives.
This file tries to reconcile all these pieces of information so that it is presented
as a single object: AggregatedDiskData.
"""
from typing import List, Optional, Callable
from typing import NamedTuple, cast

from mbed_devices._internal.windows.component_descriptor import ComponentDescriptor, ComponentDescriptorWrapper
from mbed_devices._internal.windows.component_descriptor_utils import retain_value_or_default
from mbed_devices._internal.windows.disk_drive import DiskDrive
from mbed_devices._internal.windows.disk_partition import DiskPartition
from mbed_devices._internal.windows.disk_partition_logical_disk_relationships import (
    DiskPartitionLogicalDiskRelationship,
)
from mbed_devices._internal.windows.logical_disk import LogicalDisk
from mbed_devices._internal.windows.volume_set import VolumeInformation, get_volume_information


class AggregatedDiskDataDefinition(NamedTuple):
    """Data aggregation with regards to a disk."""

    label: str  # e.g. C:
    description: str  # e.g. Removal Disk
    free_space: int
    size: int
    partition_name: str  # e.g. Disk #0, Partition #2
    partition_type: str  # 16-bit FAT
    volume_information: VolumeInformation
    caption: str  # e.g. SAMSUNG MZNLN512HMJP-000L7
    physical_disk_name: str
    model: str
    interface_type: str  # e.g. IDE
    media_type: str  # e.g. Fixed hard disk media
    manufacturer: str
    serial_number: str
    status: str
    pnp_device_id: str


class AggregatedDiskData(ComponentDescriptor):
    """Disk information based on lots of different sources."""

    def __init__(self) -> None:
        """Initialiser."""
        super().__init__(AggregatedDiskDataDefinition, win32_class_name="DiskDataAggregation")

    @property
    def component_id(self) -> str:
        """Returns the ID field."""
        return cast(str, self.get("label"))


class DiskDataAggregator:
    """Aggregator for any scattered data related to disks."""

    def __init__(
        self,
        physical_disks: dict,
        partition_disks: dict,
        logical_partition_relationships: dict,
        lookup_volume_information: Callable[[LogicalDisk], VolumeInformation],
    ) -> None:
        """Initialiser."""
        self._physical_disks = physical_disks
        self._partition_disks = partition_disks
        self._logical_partition_relationships = logical_partition_relationships
        self._lookup_volume_information = lookup_volume_information

    def _get_corresponding_partition(self, logical_disk: LogicalDisk) -> DiskPartition:
        """Determines the partition corresponding to a logical disk."""
        # Determines the partition ID
        partition_id = self.logical_disk_partition_relationships.get(logical_disk.component_id)
        return self._partition_disks.get(partition_id, DiskPartition()) if partition_id else DiskPartition()

    @property
    def physical_disks(self) -> dict:
        """Gets local cache of physical disks data."""
        return self._physical_disks

    @property
    def partition_disks(self) -> dict:
        """Gets local cache of disk partition data."""
        return self._partition_disks

    @property
    def logical_disk_partition_relationships(self) -> dict:
        """Gets local cache of relationships between logical disk and disk partitions."""
        return self._logical_partition_relationships

    def aggregate(self, logical_disk: LogicalDisk) -> AggregatedDiskData:
        """Aggregates data about a disk from different sources."""
        corresponding_partition = self._get_corresponding_partition(logical_disk)
        corresponding_volume_information = self._lookup_volume_information(logical_disk)
        # Determines which physical disk the partition is on
        # See https://superuser.com/questions/1147218/on-which-physical-drive-is-this-logical-drive
        corresponding_physical = self._physical_disks.get(corresponding_partition.get("DiskIndex"), DiskDrive())
        aggregatedData = AggregatedDiskData()
        aggregatedData.set_data_values(
            dict(
                label=logical_disk.component_id,
                description=logical_disk.get("Description"),
                free_space=logical_disk.get("FreeSpace"),
                size=logical_disk.get("Size"),
                partition_name=corresponding_partition.component_id,
                partition_type=corresponding_partition.get("Type"),
                volume_information=corresponding_volume_information,
                caption=corresponding_physical.get("Caption"),
                physical_disk_name=corresponding_physical.get("DeviceID"),
                model=corresponding_physical.get("Model"),
                interface_type=corresponding_physical.get("InterfaceType"),
                media_type=corresponding_physical.get("MediaType"),
                manufacturer=corresponding_physical.get("Manufacturer"),
                serial_number=retain_value_or_default(corresponding_physical.get("SerialNumber")),
                status=corresponding_physical.get("Status"),
                pnp_device_id=corresponding_physical.get("PNPDeviceID"),
            )
        )
        return aggregatedData


class WindowsDataAggregator(DiskDataAggregator):
    """Disk Data aggregator for Windows."""

    def __init__(self) -> None:
        """Initialiser."""
        super().__init__(
            physical_disks={
                d.Index: d  # type: ignore
                for d in ComponentDescriptorWrapper(DiskDrive).element_generator()
            },
            partition_disks={p.component_id: p for p in ComponentDescriptorWrapper(DiskPartition).element_generator()},
            logical_partition_relationships={
                r.logical_disk_id: r.disk_partition_id  # type: ignore
                for r in ComponentDescriptorWrapper(DiskPartitionLogicalDiskRelationship).element_generator()
            },
            lookup_volume_information=lambda logical_disk: get_volume_information(logical_disk.component_id),
        )


class SystemDiskInformation:
    """All information about disks on the current system."""

    def __init__(self) -> None:
        """Initialiser."""
        self._disk_data_by_serial_number: Optional[dict] = None
        self._disk_data_by_label: Optional[dict] = None

    def _load_data(self) -> None:
        aggregator = WindowsDataAggregator()
        disk_data_by_serialnumber: dict = dict()
        disk_data_by_label = dict()
        for l in ComponentDescriptorWrapper(LogicalDisk).element_generator():
            aggregation = aggregator.aggregate(cast(LogicalDisk, l))
            key = aggregation.get("serial_number").lower()
            disk_data_list = disk_data_by_serialnumber.get(key, list())
            disk_data_list.append(aggregation)
            disk_data_by_serialnumber[key] = disk_data_list
            disk_data_by_label[aggregation.get("label")] = aggregation
        self._disk_data_by_serial_number = disk_data_by_serialnumber
        self._disk_data_by_label = disk_data_by_label

    @property
    def disk_data_by_serialnumber(self) -> dict:
        """Gets system's disk data by serial number."""
        if not self._disk_data_by_serial_number:
            self._load_data()
        return self._disk_data_by_serial_number if self._disk_data_by_serial_number else dict()

    @property
    def disk_data_by_label(self) -> dict:
        """Gets system's disk data by label."""
        if not self._disk_data_by_label:
            self._load_data()
        return self._disk_data_by_label if self._disk_data_by_label else dict()

    def get_disk_information(self, serial_number: str) -> List[AggregatedDiskData]:
        """Gets all disk information for a given serial number."""
        return self.disk_data_by_serialnumber.get(serial_number.lower(), list())

    def get_disk_information_by_label(self, label: str) -> AggregatedDiskData:
        """Gets all disk information for a given label."""
        return self.disk_data_by_label.get(
            label.upper(), self.disk_data_by_label.get(label.lower(), AggregatedDiskData())
        )
