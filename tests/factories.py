#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import factory
import pathlib

from mbed_devices._internal.candidate_device import CandidateDevice


class CandidateDeviceFactory(factory.Factory):
    class Meta:
        model = CandidateDevice

    product_id = factory.Faker("hexify")
    vendor_id = factory.Faker("hexify")
    mount_points = [pathlib.Path(".")]
    serial_number = factory.Faker("hexify", text=("^" * 20))  # 20 characters serial number
    serial_port = None
