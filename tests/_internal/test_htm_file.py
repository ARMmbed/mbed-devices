from unittest import TestCase
from pyfakefs.fake_filesystem_unittest import Patcher

from mbed_devices._internal.htm_file import HTMFileContentsParser, OnlineId


class TestCode(TestCase):
    def test_reads_code_from_code_attribute(self):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.code, code)

    def test_reads_code_from_auth_attribute(self):
        code = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={code}&loader=11972&firmware=16457&configuration=4" />'
        )

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.code, code)

    def test_none_if_no_code(self):
        parser = HTMFileContentsParser("")
        self.assertIsNone(parser.code)


class TestOnlineId(TestCase):
    def test_reads_online_id_from_url(self):
        url = "https://os.mbed.com/platforms/THIS-IS_a_SLUG_123/"
        file_contents = f"window.location.replace({url});"

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.online_id, OnlineId(device_type="platform", device_slug="THIS-IS_a_SLUG_123"))

    def test_none_if_not_found(self):
        url = "https://os.mbed.com/about"
        file_contents = f"window.location.replace({url});"

        parser = HTMFileContentsParser(file_contents)
        self.assertIsNone(parser.online_id)


class TestFromFile(TestCase):
    def test_initialises_parser_with_file_contents(self):
        file_path = "/foo/bar.txt"
        file_contents = "some contents"
        with Patcher() as patcher:
            patcher.fs.create_file(file_path, contents=file_contents)
            parser = HTMFileContentsParser.from_file(file_path)
        self.assertEqual(parser._file_contents, file_contents)
