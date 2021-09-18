"""
Tests for parser with common options
"""

import unittest
from cap_client.parser import parser, subparsers


class ParserTests(unittest.TestCase):
    """parsing command-line argument"""

    def test_parser_description(self):
        self.assertTrue("captest" in parser.description)

    def test_parser_defaults(self):
        """parser should have default values for some arguments"""
        self.assertEqual(parser.get_default("secrets"), "secrets.yaml")

    def test_parser_help(self):
        help_str = parser.format_help()
        self.assertTrue("usage" in help_str)

    def test_subparsers_dest(self):
        """subparsers should be identified by a dest=action"""
        self.assertEqual(subparsers.dest, "action")
