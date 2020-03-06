import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase, mock
from mbed_targets import UnknownTarget

from tests.factories import CandidateDeviceFactory
from mbed_devices._internal.htm_file import HTMFileContentsParser, OnlineId
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


@mock.patch("mbed_devices._internal.resolve_target.HTMFileContentsParser")
class TestResolveTargetUsingFileContents(TestCase):
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code")
    def test_resolves_targets_using_product_code_when_available(
        self, get_target_by_product_code, MockedHTMFileContentsParser
    ):
        parser = mock.Mock(spec_set=HTMFileContentsParser, product_code="0123")
        MockedHTMFileContentsParser.return_value = parser

        self.assertEqual(
            _resolve_target_using_file_contents(["file contents"]), get_target_by_product_code.return_value
        )
        MockedHTMFileContentsParser.assert_called_once_with("file contents")
        get_target_by_product_code.assert_called_once_with(parser.product_code)

    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code")
    def test_raises_when_resolving_using_product_code_fails(
        self, get_target_by_product_code, MockedHTMFileContentsParser
    ):
        parser = mock.Mock(spec_set=HTMFileContentsParser, product_code="0123")
        MockedHTMFileContentsParser.return_value = parser
        get_target_by_product_code.side_effect = UnknownTarget

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["some file contents"])

    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id")
    def test_resolves_targets_using_online_id_when_available(
        self, get_target_by_online_id, MockedHTMFileContentsParser
    ):
        online_id = OnlineId(device_type="hat", device_slug="boat")
        parser = mock.Mock(spec_set=HTMFileContentsParser, product_code=None, online_id=online_id)
        MockedHTMFileContentsParser.return_value = parser

        self.assertEqual(
            _resolve_target_using_file_contents(["some file contents"]), get_target_by_online_id.return_value
        )
        MockedHTMFileContentsParser.assert_called_with("some file contents")
        get_target_by_online_id.assert_called_once_with(slug=online_id.device_slug, target_type=online_id.device_type)

    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id")
    def test_raises_when_resolving_using_online_id_fails(self, get_target_by_online_id, MockedHTMFileContentsParser):
        online_id = OnlineId(device_type="hat", device_slug="boat")
        parser = mock.Mock(spec_set=HTMFileContentsParser, product_code=None, online_id=online_id)
        MockedHTMFileContentsParser.return_value = parser
        get_target_by_online_id.side_effect = UnknownTarget

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["whatever"])

    def test_raises_when_no_information_found_on_candidate(self, MockedHTMFileContentsParser):
        parser = mock.Mock(spec_set=HTMFileContentsParser, product_code=None, online_id=None)
        MockedHTMFileContentsParser.return_value = parser

        with self.assertRaises(NoTargetForCandidate):
            _resolve_target_using_file_contents(["zero information in this file"])
