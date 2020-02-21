"""Entry point for mbed-tools cli."""
import click
from typing import Iterable
from tabulate import tabulate

from mbed_devices import get_connected_devices, Device


def _build_output(devices: Iterable[Device]) -> str:
    headers = ["Platform name", "Serial number", "Serial port", "Mount point(s)"]
    devices_data = []
    for device in devices:
        mount_points = ", ".join(str(mount_point) for mount_point in device.mount_points)
        devices_data.append([device.mbed_target.platform_name, device.serial_number, device.serial_port, mount_points])
    return tabulate(devices_data, headers=headers)


@click.command()
def list_connected_devices():
    """Prints connected devices."""
    devices = get_connected_devices()
    if devices:
        output = _build_output(devices)
        click.echo(output)
    else:
        click.echo("No connected Mbed devices found.")


cli = list_connected_devices
