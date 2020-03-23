#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase
from mbed_targets.mbed_tools import config_variables as mbed_targets_config_variables

from mbed_devices.mbed_tools import cli, config_variables
from mbed_devices._internal.mbed_tools.list_connected_devices import list_connected_devices


class TestCli(TestCase):
    def test_aliases_list_connected_devices(self):
        self.assertEqual(cli, list_connected_devices)


class TestConfigVariables(TestCase):
    def test_aliases_list_of_config_variables_from_mbed_targets(self):
        self.assertEqual(config_variables, mbed_targets_config_variables)
