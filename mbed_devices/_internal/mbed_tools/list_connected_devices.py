"""List all devices cli command."""
import click
import json
from operator import attrgetter
from typing import Iterable
from tabulate import tabulate

from mbed_devices import get_connected_devices, Device
from mbed_targets import MbedTarget


@click.command()
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", show_default=True, help="Set output format."
)
def list_connected_devices(format: str) -> None:
    """Prints connected devices."""
    devices = _sort_devices_by_name(get_connected_devices())
    output_builders = {
        "table": _build_tabular_output,
        "json": _build_json_output,
    }
    if devices:
        output = output_builders[format](devices)
        click.echo(output)
    else:
        click.echo("No connected Mbed devices found.")


def _sort_devices_by_name(devices: Iterable[Device]) -> Iterable[Device]:
    return sorted(devices, key=attrgetter("mbed_target.board_name"))


def _build_tabular_output(devices: Iterable[Device]) -> str:
    headers = ["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"]
    devices_data = []
    for device in devices:
        devices_data.append(
            [
                device.mbed_target.board_name,
                device.serial_number,
                device.serial_port or "UNKNOWN",
                "\n".join(str(mount_point) for mount_point in device.mount_points),
                "\n".join(_get_build_targets(device.mbed_target)),
            ]
        )
    return tabulate(devices_data, headers=headers)


def _build_json_output(devices: Iterable[Device]) -> str:
    devices_data = []
    for device in devices:
        mbed_target = device.mbed_target
        devices_data.append(
            {
                "serial_number": device.serial_number,
                "serial_port": device.serial_port,
                "mount_points": [str(m) for m in device.mount_points],
                "mbed_target": {
                    "product_code": mbed_target.product_code,
                    "board_type": mbed_target.board_type,
                    "board_name": mbed_target.board_name,
                    "mbed_os_support": mbed_target.mbed_os_support,
                    "mbed_enabled": mbed_target.mbed_enabled,
                    "build_targets": _get_build_targets(mbed_target),
                },
            }
        )
    return json.dumps(devices_data, indent=4)


def _get_build_targets(mbed_target: MbedTarget) -> Iterable[str]:
    return [f"{mbed_target.board_type}_{variant}" for variant in mbed_target.build_variant] + [mbed_target.board_type]
