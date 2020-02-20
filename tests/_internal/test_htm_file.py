from unittest import TestCase
from pyfakefs.fake_filesystem_unittest import Patcher

from mbed_devices._internal.htm_file import HTMFileContentsParser


class TestTargetId(TestCase):
    def test_reads_target_id_from_code_attribute(self):
        target_id = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={target_id}"/>'

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.target_id, target_id)

    def test_reads_target_id_from_auth_attribute(self):
        target_id = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={target_id}&loader=11972&firmware=16457&configuration=4" />'
        )

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.target_id, target_id)

    def test_none_if_no_target_id(self):
        parser = HTMFileContentsParser("")
        self.assertIsNone(parser.target_id)


class TestFromFile(TestCase):
    def test_initialises_parser_with_file_contents(self):
        file_path = "/foo/bar.txt"
        file_contents = "some contents"
        with Patcher() as patcher:
            patcher.fs.create_file(file_path, contents=file_contents)
            parser = HTMFileContentsParser.from_file(file_path)
        self.assertEqual(parser._file_contents, file_contents)
