import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase, mock
from mbed_targets import UnknownTarget

from tests.factories import CandidateDeviceFactory
from mbed_devices._internal.htm_file import OnlineId
from mbed_devices._internal.resolve_target import (
    NoTargetForCandidate,
    _resolve_target_using_file_contents,
    resolve_target,
)


class TestResolveTarget(TestCase):
    @mock.patch("mbed_devices._internal.resolve_target._resolve_target_using_file_contents")
    def test_resolves_target_using_file_contents_found_in_mount_points(self, _resolve_target_using_file_contents):
        files = [(pathlib.Path("/test-1/mbed.htm"), "foo"), (pathlib.Path("/test-2/whatever.htm"), "bar")]
        with Patcher() as patcher:
            for (path, contents) in files:
                patcher.fs.create_file(str(path), contents=contents)
            patcher.fs.create_file("/test-1/file.txt", contents="whatever")

            result = resolve_target(
                CandidateDeviceFactory(mount_points=[pathlib.Path("/test-1"), pathlib.Path("/test-2")])
            )

        self.assertEqual(result, _resolve_target_using_file_contents.return_value)
        _resolve_target_using_file_contents.assert_called_once_with(["foo", "bar"])


class TestResolveTargetUsingFileContents(TestCase):
    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code")
    def test_resolves_targets_using_product_code_when_available(self, get_target_by_product_code, read_product_code):
        read_product_code.return_value = "0123"

        self.assertEqual(
            _resolve_target_using_file_contents(["file contents"]), get_target_by_product_code.return_value
        )
        get_target_by_product_code.assert_called_once_with(read_product_code.return_value)
        read_product_code.assert_called_once_with("file contents")

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code")
    def test_raises_when_resolving_using_product_code_fails(self, get_target_by_product_code, read_product_code):
        read_product_code.return_value = "1234"
        get_target_by_product_code.side_effect = UnknownTarget

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["some file contents"])

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.read_online_id")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id")
    def test_resolves_targets_using_online_id_when_available(
        self, get_target_by_online_id, read_online_id, read_product_code
    ):
        online_id = OnlineId(device_type="hat", device_slug="boat")
        read_product_code.return_value = None
        read_online_id.return_value = online_id

        self.assertEqual(
            _resolve_target_using_file_contents(["some file contents"]), get_target_by_online_id.return_value
        )
        read_online_id.assert_called_with("some file contents")
        get_target_by_online_id.assert_called_once_with(slug=online_id.device_slug, target_type=online_id.device_type)

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.read_online_id")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id")
    def test_raises_when_resolving_using_online_id_fails(
        self, get_target_by_online_id, read_online_id, read_product_code
    ):
        read_product_code.return_value = None
        read_online_id.return_value = OnlineId(device_type="hat", device_slug="boat")
        get_target_by_online_id.side_effect = UnknownTarget

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["whatever"])

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.read_online_id")
    def test_raises_when_no_information_found_on_candidate(self, read_product_code, read_online_id):
        read_product_code.return_value = None
        read_online_id.return_value = None

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["zero information in this file"])
