#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Integration with https://github.com/ARMmbed/mbed-tools."""
from mbed_devices._internal.mbed_tools.list_connected_devices import list_connected_devices
from mbed_targets.mbed_tools import config_variables as mbed_targets_config_variables

cli = list_connected_devices
config_variables = mbed_targets_config_variables
