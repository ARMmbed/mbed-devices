#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Integration with https://github.com/ARMmbed/mbed-tools."""
from mbed_devices._internal.mbed_tools.list_connected_devices import list_connected_devices
from mbed_targets.mbed_tools import env_variables as mbed_targets_env_variables

cli = list_connected_devices
env_variables = mbed_targets_env_variables
