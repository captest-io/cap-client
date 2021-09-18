"""
Tests for validating certain objects
"""

import unittest
import tempfile
from os.path import join
from unittest.mock import patch
from cap_client.credentials import CredentialsManager
from cap_client.errors import ValidationError
from cap_client.validations import \
    validate_collection, \
    validate_config, \
    validate_credentials, \
    validate_notes


class MockConfig:
    api = "www.captest.io"
    file = None
    dir = None
    action = None
    collection = None
    parent_uuid = None

    def __contains__(self, item):
        return item in self.__dict__


class ValidateConfigTests(unittest.TestCase):
    """ensures cmd arguments are proper"""

    def test_standardize_api(self):
        # add a slash if there isn't one already
        result_append = validate_config(MockConfig())
        self.assertEqual(result_append.api, "https://www.captest.io/")
        # do not add a slash if there is one already
        raw = MockConfig()
        raw.api += "https://www.captest.io/"
        result_good = validate_config(raw)
        self.assertEqual(result_good.api, raw.api)

    def test_signal_invalid_file(self):
        config = MockConfig()
        with tempfile.TemporaryDirectory() as tempdir:
            config.file = join(tempdir, "zzz.txt")
            with self.assertRaises(ValidationError) as cm:
                validate_config(config)
            self.assertTrue("file does not exist" in str(cm.exception))

    def test_signal_invalid_dir(self):
        config = MockConfig()
        with tempfile.TemporaryDirectory() as tempdir:
            config.dir = join(tempdir, "zzz")
            with self.assertRaises(ValidationError) as cm:
                validate_config(config)
            self.assertTrue("directory does not exist" in str(cm.exception))


class ValidateCredentialsTests(unittest.TestCase):
    """ensures a credentials manager has both a username and password"""

    def test_good_credentials(self):
        """credentials with username and token should pass"""
        credentials = CredentialsManager("abc", "nonexistent.yaml")
        credentials.token = "abc"
        result = validate_credentials(credentials)
        self.assertEqual(result.username, "abc")

    def test_missing_username(self):
        credentials = CredentialsManager(None, "nonexistent.yaml")
        with self.assertRaises(ValidationError) as cm:
            validate_credentials(credentials)
        self.assertTrue("username" in str(cm.exception))

    @patch('getpass.getpass')
    def test_interactive_token(self, token):
        """get an token string from an interactive prompt"""
        credentials = CredentialsManager("abc", "nonexistent.yaml")
        token.return_value = "getpass_token"
        result = validate_credentials(credentials)
        self.assertEqual(result.token, "getpass_token")

    @patch('getpass.getpass')
    def test_missing_token(self, token):
        """signal a token is missing"""
        credentials = CredentialsManager("abc", "nonexistent.yaml")
        token.return_value = ""
        with self.assertRaises(ValidationError) as cm:
            validate_credentials(credentials)
        self.assertTrue("token" in str(cm.exception))


class ValidateCollectionTests(unittest.TestCase):
    """ensures collection string is specified and consistent"""

    def test_missing_collection(self):
        header = dict(title="my title")
        with self.assertRaises(ValidationError) as cm:
            validate_collection(header, "blog")
        self.assertTrue("collection" in str(cm.exception))

    def test_incompatible_collection(self):
        header = dict(collection="resource", title="my title")
        with self.assertRaises(ValidationError) as cm:
            validate_collection(header, "blog")
        self.assertTrue("inconsistent" in str(cm.exception))

    def test_collection_ok(self):
        header = dict(collection="Resource", title="my title")
        result = validate_collection(header, "resource")
        self.assertEqual(result["collection"], "resource")


class ValidateNotesTests(unittest.TestCase):
    """ensures notes are included with a doc header"""

    def test_fill_notes(self):
        """insert an empty notes field"""
        header = dict(collection="blog", title="my title")
        result = validate_notes(header)
        self.assertEqual(result["notes"], "")

    def test_missing_notes_challenge(self):
        """challenge docs must have a non-empty notes field"""
        header = dict(collection="challenge", title="my title")
        with self.assertRaises(ValidationError) as cm:
            validate_notes(header)
        self.assertTrue("short" in str(cm.exception))

    def test_notes_as_text(self):
        """challenge docs must have a non-empty notes field"""
        header = dict(collection="challenge", title="my title",
                      notes="notes for a challenge")
        result = validate_notes(header)
        self.assertGreater(len(result["notes"]), 0)

    def test_notes_as_list(self):
        """challenge docs must have a non-empty notes field"""
        header = dict(collection="challenge", title="my title",
                      notes=["notes for a challenge"])
        result = validate_notes(header)
        self.assertGreater(len(result["notes"]), 0)

