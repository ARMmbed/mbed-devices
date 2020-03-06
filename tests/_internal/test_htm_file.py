from unittest import TestCase

from mbed_devices._internal.htm_file import HTMFileContentsParser, OnlineId


class TestProductCode(TestCase):
    def test_reads_product_code_from_code_attribute(self):
        code = "02400201B80ECE4A45F033F2"
        file_contents = f'<meta http-equiv="refresh" content="0; url=http://mbed.org/device/?code={code}"/>'

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.product_code, code[:4])

    def test_reads_product_code_from_auth_attribute(self):
        auth = "101000000000000000000002F7F35E602eeb0bb9b632205c51f6c357aeee7bc9"
        file_contents = (
            '<meta http-equiv="refresh" '
            f'content="0; url=http://mbed.org/start?auth={auth}&loader=11972&firmware=16457&configuration=4" />'
        )

        parser = HTMFileContentsParser(file_contents)
        self.assertEqual(parser.product_code, auth[:4])

    def test_none_if_no_product_code(self):
        parser = HTMFileContentsParser("")
        self.assertIsNone(parser.product_code)


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
