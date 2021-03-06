#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Shared pytest functionality."""
import platform
import unittest


windows_only = unittest.skipIf(platform.system() != "Windows", reason="Windows required")
darwin_only = unittest.skipIf(platform.system() != "Darwin", reason="Darwin required")
linux_only = unittest.skipIf(platform.system() != "Linux", reason="Linux required")
