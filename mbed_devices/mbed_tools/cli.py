"""Entry point for mbed-tools cli."""
import click
import json
from typing import Iterable
from tabulate import tabulate

from mbed_devices import get_connected_devices, Device
from mbed_targets import MbedTarget


@click.command()
@click.option(
    "--format", type=click.Choice(["table", "json"]), default="table", show_default=True, help="Set output format."
)
def list_connected_devices(format):
    """Prints connected devices."""
    devices = get_connected_devices()
    output_builders = {
        "table": _build_tabular_output,
        "json": _build_json_output,
    }
    if devices:
        output = output_builders[format](devices)
        click.echo(output)
    else:
        click.echo("No connected Mbed devices found.")


cli = list_connected_devices


def _build_tabular_output(devices: Iterable[Device]) -> str:
    headers = ["Board name", "Serial number", "Serial port", "Mount point(s)", "Build target(s)"]
    devices_data = []
    for device in devices:
        mount_points = ", ".join(str(mount_point) for mount_point in device.mount_points)
        devices_data.append(
            [
                device.mbed_target.board_name if device.mbed_target else "UNKNOWN",
                device.serial_number,
                device.serial_port or "UNKNOWN",
                mount_points,
                "\n".join(_get_build_targets(device.mbed_target)) if device.mbed_target else "UNKNOWN",
            ]
        )
    return tabulate(devices_data, headers=headers)


def _build_json_output(devices: Iterable[Device]) -> str:
    devices_data = []
    for device in devices:
        mbed_target = device.mbed_target
        if mbed_target:
            mbed_target_data = {
                "product_code": mbed_target.product_code,
                "board_type": mbed_target.board_type,
                "board_name": mbed_target.board_name,
                "mbed_os_support": mbed_target.mbed_os_support,
                "mbed_enabled": mbed_target.mbed_enabled,
                "build_targets": _get_build_targets(mbed_target),
            }
        else:
            mbed_target_data = None
        devices_data.append(
            {
                "serial_number": device.serial_number,
                "serial_port": device.serial_port,
                "mount_points": [str(m) for m in device.mount_points],
                "mbed_target": mbed_target_data,
            }
        )
    return json.dumps(devices_data, indent=4)


def _get_build_targets(mbed_target: MbedTarget) -> Iterable[str]:
    return [f"{mbed_target.board_type}_{variant}" for variant in mbed_target.build_variant] + [mbed_target.board_type]
