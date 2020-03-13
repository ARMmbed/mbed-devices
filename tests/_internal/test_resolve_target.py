import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase, mock
from mbed_targets import UnknownTarget

from tests.factories import CandidateDeviceFactory
from mbed_devices._internal.htm_file import OnlineId
from mbed_devices._internal.resolve_target import (
    NoTargetForCandidate,
    _get_all_htm_files_contents,
    resolve_target,
)


@mock.patch(
    "mbed_devices._internal.resolve_target._get_all_htm_files_contents",
    autospec=True,
    return_value=["some file contents"],
)
@mock.patch("mbed_devices._internal.resolve_target.read_product_code", autospec=True)
@mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code", autospec=True)
class TestResolveTargetUsingProductCodeFromHTM(TestCase):
    def test_returns_resolved_target(self, get_target_by_product_code, read_product_code, _get_all_htm_files_contents):
        read_product_code.return_value = "0123"
        candidate = CandidateDeviceFactory()

        subject = resolve_target(candidate)

        self.assertEqual(subject, get_target_by_product_code.return_value)
        get_target_by_product_code.assert_called_once_with(read_product_code.return_value)
        read_product_code.assert_called_once_with(_get_all_htm_files_contents.return_value[0])
        _get_all_htm_files_contents.assert_called_once_with(candidate.mount_points)

    def test_raises_when_target_not_found(
        self, get_target_by_product_code, read_product_code, _get_all_htm_files_contents
    ):
        read_product_code.return_value = "1234"
        get_target_by_product_code.side_effect = UnknownTarget
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoTargetForCandidate):
            resolve_target(candidate)


@mock.patch(
    "mbed_devices._internal.resolve_target._get_all_htm_files_contents",
    autospec=True,
    return_value=["other file contents"],
)
@mock.patch("mbed_devices._internal.resolve_target.read_product_code", autospec=True, return_value=None)
@mock.patch("mbed_devices._internal.resolve_target.read_online_id", autospec=True)
@mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id", autospec=True)
class TestResolveTargetUsingOnlineIdFromHTM(TestCase):
    def test_returns_resolved_target(
        self, get_target_by_online_id, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        online_id = OnlineId(device_type="hat", device_slug="boat")
        read_online_id.return_value = online_id
        candidate = CandidateDeviceFactory()

        subject = resolve_target(candidate)

        self.assertEqual(subject, get_target_by_online_id.return_value)
        read_online_id.assert_called_with(_get_all_htm_files_contents.return_value[0])
        get_target_by_online_id.assert_called_once_with(slug=online_id.device_slug, target_type=online_id.device_type)

    def test_raises_when_target_not_found(
        self, get_target_by_online_id, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        read_online_id.return_value = OnlineId(device_type="hat", device_slug="boat")
        get_target_by_online_id.side_effect = UnknownTarget
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoTargetForCandidate):
            resolve_target(candidate)


@mock.patch(
    "mbed_devices._internal.resolve_target._get_all_htm_files_contents",
    autospec=True,
    return_value=["who knows file contents"],
)
@mock.patch("mbed_devices._internal.resolve_target.read_product_code", autospec=True, return_value=None)
@mock.patch("mbed_devices._internal.resolve_target.read_online_id", autospec=True, return_value=None)
@mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code", autospec=True)
class TestResolveTargetUsingProductCodeFromSerial(TestCase):
    def test_resolves_targets_using_product_code_when_available(
        self, get_target_by_product_code, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        candidate = CandidateDeviceFactory()

        subject = resolve_target(candidate)

        self.assertEqual(subject, get_target_by_product_code.return_value)
        get_target_by_product_code.assert_called_once_with(candidate.serial_number[:4])

    def test_raises_when_target_not_found(
        self, get_target_by_product_code, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        get_target_by_product_code.side_effect = UnknownTarget
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoTargetForCandidate):
            resolve_target(candidate)


class TestGetAllHtmFilesContents(TestCase):
    def test_returns_contents_of_all_htm_files_in_given_directories(self):
        with Patcher() as patcher:
            patcher.fs.create_file("/test-1/mbed.htm", contents="foo")
            patcher.fs.create_file("/test-2/whatever.htm", contents="bar")
            patcher.fs.create_file("/test-1/file.txt", contents="txt files should not be read")
            patcher.fs.create_file("/test-1/._MBED.HTM", contents="hidden files should not be read")

            result = _get_all_htm_files_contents([pathlib.Path("/test-1"), pathlib.Path("/test-2")])

        self.assertEqual(result, ["foo", "bar"])
