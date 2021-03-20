"""
Tests for reading files in formats used by the client
"""

import unittest
from os.path import join
from cap_client.docs import read_header_content as read_hc


# directory with test data files
data_dir = join("tests", "testdata")


class HeaderContentTests(unittest.TestCase):
    """reading md files with a yaml header section"""

    def test_read_when_format_is_good(self):
        """can extract header and content from a properly formatted file"""

        header, content = read_hc(join(data_dir, "doc_good.md"))
        self.assertEqual(type(header), dict)
        self.assertEqual(type(content), str)

    def test_read_detects_emptyline(self):
        """reader does not allow headers with empty lines"""

        with self.assertRaises(Exception):
            read_hc(join(data_dir, "doc_empty_line.md"))

    def test_read_detects_no_header(self):
        """reader requires the presence of a header section"""

        with self.assertRaises(Exception):
            read_hc(join(data_dir, "doc_no_header.md"))

    def test_read_detects_unclosed(self):
        """reader does not allow headers with empty lines"""

        with self.assertRaises(Exception):
            read_hc(join(data_dir, "doc_empty_line.md"))
