import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase, mock
from mbed_targets import UnknownTarget

from tests.factories import CandidateDeviceFactory
from mbed_devices._internal.htm_file import OnlineId
from mbed_devices._internal.resolve_target import (
    UnableToBuildResolver,
    NoTargetForCandidate,
    _get_all_htm_files_contents,
    resolve_target,
    _build_target_resolver,
)


@mock.patch("mbed_devices._internal.resolve_target._build_target_resolver")
class TestResolveTarget(TestCase):
    def test_returns_target_resolved_using_built_target_resolver(self, _build_target_resolver):
        candidate = CandidateDeviceFactory()

        subject = resolve_target(candidate)

        self.assertEqual(subject, _build_target_resolver.return_value.return_value)
        _build_target_resolver.assert_called_once_with(candidate)

    def test_raises_when_resolver_cannot_be_built(self, _build_target_resolver):
        _build_target_resolver.side_effect = UnableToBuildResolver
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoTargetForCandidate):
            resolve_target(candidate)

    def test_raises_when_target_cannot_be_resolved(self, _build_target_resolver):
        resolver = mock.Mock(side_effect=UnknownTarget)
        _build_target_resolver.return_value = resolver
        candidate = CandidateDeviceFactory()

        with self.assertRaises(NoTargetForCandidate):
            resolve_target(candidate)


@mock.patch("mbed_devices._internal.resolve_target._get_all_htm_files_contents")
class TestBuildTargetResolver(TestCase):
    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_product_code")
    def test_will_resolve_targets_using_product_code_when_available(
        self, get_target_by_product_code, read_product_code, _get_all_htm_files_contents
    ):
        _get_all_htm_files_contents.return_value = ["file contents"]
        read_product_code.return_value = "0123"
        candidate = CandidateDeviceFactory()

        subject = _build_target_resolver(candidate)()

        self.assertEqual(subject, get_target_by_product_code.return_value)
        get_target_by_product_code.assert_called_once_with(read_product_code.return_value)
        read_product_code.assert_called_once_with("file contents")
        _get_all_htm_files_contents.assert_called_once_with(candidate.mount_points)

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.read_online_id")
    @mock.patch("mbed_devices._internal.resolve_target.get_target_by_online_id")
    def test_will_resolve_targets_using_online_id_when_available(
        self, get_target_by_online_id, read_online_id, read_product_code, _get_all_htm_files_contents
    ):
        _get_all_htm_files_contents.return_value = ["some file contents"]
        online_id = OnlineId(device_type="hat", device_slug="boat")
        read_product_code.return_value = None
        read_online_id.return_value = online_id
        candidate = CandidateDeviceFactory()

        subject = _build_target_resolver(candidate)()

        self.assertEqual(subject, get_target_by_online_id.return_value)
        read_online_id.assert_called_with("some file contents")
        get_target_by_online_id.assert_called_once_with(slug=online_id.device_slug, target_type=online_id.device_type)

    @mock.patch("mbed_devices._internal.resolve_target.read_product_code")
    @mock.patch("mbed_devices._internal.resolve_target.read_online_id")
    def test_raises_when_no_information_found_on_candidate(
        self, read_product_code, read_online_id, _get_all_htm_files_contents
    ):
        _get_all_htm_files_contents.return_value = ["foo"]
        read_product_code.return_value = None
        read_online_id.return_value = None

        with self.assertRaises(UnableToBuildResolver):
            _build_target_resolver(CandidateDeviceFactory())()


class TestGetAllHtmFilesContents(TestCase):
    def test_returns_contents_of_all_htm_files_in_given_directories(self):
        with Patcher() as patcher:
            patcher.fs.create_file("/test-1/mbed.htm", contents="foo")
            patcher.fs.create_file("/test-2/whatever.htm", contents="bar")
            patcher.fs.create_file("/test-1/file.txt", contents="txt files should not be read")
            patcher.fs.create_file("/test-1/._MBED.HTM", contents="hidden files should not be read")

            result = _get_all_htm_files_contents([pathlib.Path("/test-1"), pathlib.Path("/test-2")])

        self.assertEqual(result, ["foo", "bar"])
