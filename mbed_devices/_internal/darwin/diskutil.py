"""Interactions with `diskutil`."""
import plistlib
import subprocess
from typing import Dict, List, Optional, cast


def get_all_external_disks_data() -> List[Dict]:
    """Returns parsed output of `diskutil` call, fetching only information of interest."""
    output = subprocess.check_output(["diskutil", "list", "-plist", "external"], stderr=subprocess.DEVNULL)
    if output:
        data: Dict = plistlib.loads(output)
        return data.get("AllDisksAndPartitions", [])
    return []


def get_all_external_volumes_data() -> List[Dict]:
    """Returns all external volumes data.

    Reduces structure returned by `diskutil` call to one which will only contain data about Volumes.
    Useful for determining MountPoints and DeviceIdentifiers.
    """
    data = get_all_external_disks_data()
    return _filter_volumes(data)


def get_external_volume_data(device_identifier: str) -> Optional[Dict]:
    """Returns external volume data for a given identifier."""
    data = get_all_external_volumes_data()
    for device in data:
        if device.get("DeviceIdentifier") == device_identifier:
            return device
    return None


def get_mount_point(device_identifier: str) -> Optional[str]:
    """Returns mount point of a given device."""
    device_data = get_external_volume_data(device_identifier)
    if device_data and "MountPoint" in device_data:
        return cast(str, device_data["MountPoint"])
    return None


def _filter_volumes(data: List[Dict]) -> List[Dict]:
    """Flattens the structure returned by `diskutil` call.

    Expected input will contain both partitioned an unpartitioned devices.
    Partitioned devices list mounted partitions under an arbitrary key,
    flattening the data helps finding actual end devices later on.
    """
    devices = []
    for device in data:
        if "Partitions" in device:
            devices.extend(_filter_volumes(device["Partitions"]))
        else:
            devices.append(device)
    return devices
