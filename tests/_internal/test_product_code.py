import pathlib
from unittest import TestCase, mock
from pyfakefs.fake_filesystem_unittest import Patcher

from tests.factories import CandidateDeviceFactory
from mbed_devices._internal.htm_file import HTMFileContentsParser
from mbed_devices._internal.product_code import (
    MissingProductCode,
    _extract_product_code_from_htm_file,
    _get_all_htm_files,
    extract_product_code,
)


@mock.patch("mbed_devices._internal.product_code._extract_product_code_from_htm_file")
@mock.patch("mbed_devices._internal.product_code._get_all_htm_files")
class TestExtractProductCode(TestCase):
    def test_returns_first_found_product_code_from_htm_files(
        self, _get_all_htm_files, _extract_product_code_from_htm_file
    ):
        expected_product_code = "1234"
        file_1 = pathlib.Path("/Volumes/MBED 1/PRODINFO.HTM")
        file_2 = pathlib.Path("/Volumes/MBED 1/MBED.HTM")
        _get_all_htm_files.return_value = [file_1, file_2]
        _extract_product_code_from_htm_file.side_effect = [None, expected_product_code]
        candidate_device = CandidateDeviceFactory(mount_points=[pathlib.Path("/Volumes/MBED 1")])

        subject = extract_product_code(candidate_device)

        self.assertEqual(subject, expected_product_code)
        _extract_product_code_from_htm_file.assert_has_calls([mock.call(file_1), mock.call(file_2)])
        _get_all_htm_files.assert_called_once_with(candidate_device.mount_points)

    def test_raises_if_product_code_cannot_be_found(self, _get_all_htm_files, _extract_product_code_from_htm_file):
        _get_all_htm_files.return_value = [pathlib.Path("/Volumes/DAPLINK/FOO.HTM")]
        _extract_product_code_from_htm_file.return_value = None
        candidate_device = CandidateDeviceFactory(mount_points=[pathlib.Path("/Volumes/DAPLINK")])

        with self.assertRaises(MissingProductCode):
            extract_product_code(candidate_device)


class TestGetAllHTMFiles(TestCase):
    def test_yields_all_htm_files_found_in_given_directories(self):
        file_paths = [
            pathlib.Path("/test-1/mbed.htm"),
            pathlib.Path("/test-1/whatever.htm"),
            pathlib.Path("/test-2/foo.HTM"),
        ]
        with Patcher() as patcher:
            for path in file_paths:
                patcher.fs.create_file(str(path))
            patcher.fs.create_file("/test-1/file.txt")

            htm_files = _get_all_htm_files([pathlib.Path("/test-1"), pathlib.Path("/test-2")])

        stringified_paths = [str(path) for path in htm_files]
        for file_path in file_paths:
            self.assertIn(str(file_path), stringified_paths)


@mock.patch("mbed_devices._internal.product_code.HTMFileContentsParser.from_file")
class TestExtractProductCodeFromHTMFile(TestCase):
    def test_uses_htm_file_parser_to_extract_product_code(self, from_file):
        code = "0123456"
        instance = mock.Mock(spec_set=HTMFileContentsParser, product_code=code)
        from_file.return_value = instance
        file = pathlib.Path("/foo/bar.htm")

        subject = _extract_product_code_from_htm_file(file)

        self.assertEqual(subject, code)
        from_file.assert_called_once_with(str(file))
