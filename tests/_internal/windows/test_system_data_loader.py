#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from unittest.mock import patch

from tests.markers import windows_only


@windows_only
class TestSystemDataLoader(unittest.TestCase):
    @patch("mbed_devices._internal.windows.system_data_loader.load_all")
    def test_system_data_load(self, load_all):
        from mbed_devices._internal.windows.system_data_loader import SystemDataLoader, SYSTEM_DATA_TYPES

        def mock_system_element_fetcher(arg):
            return (arg, list())

        load_all.side_effect = mock_system_element_fetcher

        loader = SystemDataLoader()
        for type in SYSTEM_DATA_TYPES:
            self.assertIsNotNone(loader.get_system_data(type))
            self.assertTrue(isinstance(loader.get_system_data(type), list))
        load_all.assert_called()
