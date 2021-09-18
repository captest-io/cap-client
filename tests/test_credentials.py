"""
Tests for managing credentials (username and access token)
"""

import shutil
import tempfile
import unittest
from os.path import join
from cap_client.credentials import CredentialsManager
from cap_client.errors import ValidationError


# directory with test data files
data_dir = join("tests", "testdata")

# files with correct formatting
secrets_file = join(data_dir, "secrets.yaml")
secrets_two_file = join(data_dir, "secrets_two.yaml")
secrets_empty_file = join(data_dir, "secrets_empty.yaml")
# files with incorrect formatting
secrets_malformed_file = join(data_dir, "secrets_malformed.yaml")


class CredentialsTests(unittest.TestCase):
    """loading, getting, replacing, saving credentials (username, token)"""

    def test_get_default_username(self):
        """detect default username from contents of secrets file"""
        result = CredentialsManager(None, secrets_file)
        self.assertEqual(result.username, "abc")
        self.assertEqual(result.token, "abc_token")

    def test_use_new_username(self):
        """specify a new username"""
        result = CredentialsManager("xyz", secrets_file)
        self.assertEqual(result.username, "xyz")
        self.assertEqual(result.token, None)

    def test_leave_username_unspecified_if_missing(self):
        """empty does not specify a username nor a token"""
        result = CredentialsManager(None, secrets_empty_file)
        self.assertEqual(result.username, None)
        self.assertEqual(result.token, None)

    def test_init_if_no_file(self):
        """manager should initialize if secrets file does not yet exist"""
        result = CredentialsManager(None, join(data_dir, "zzz.yaml"))
        self.assertEqual(result.username, None)
        self.assertEqual(result.token, None)

    def test_signal_malformed_file(self):
        """secrets file that exists but has incorrect format should fail"""
        with self.assertRaises(ValidationError) as cm:
            CredentialsManager(None, secrets_malformed_file)
        self.assertTrue("malformed " in str(cm.exception))

    def test_use_provided_token(self):
        """init can provide a new token"""
        default = CredentialsManager("abc", secrets_file)
        self.assertEqual(default.username, "abc")
        self.assertEqual(default.token, "abc_token")
        result = CredentialsManager("abc", secrets_file, token="new_token")
        self.assertEqual(result.username, "abc")
        self.assertEqual(result.token, "new_token")

    def test_str(self):
        """string representation includes username and token"""
        result = str(CredentialsManager("abc", secrets_file))
        self.assertTrue("abc" in result)
        self.assertTrue("token" in result)

    def test_str_empty(self):
        """string representation for empty credentials"""
        result = str(CredentialsManager("abc", join(data_dir, "zzz.yaml")))
        self.assertTrue("username" in result)
        self.assertTrue("token" in result)

    def test_save_credentials(self):
        """use manager to replace content in an existing secrets file"""
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file = join(tempdir, "secrets_temp.yaml")
            shutil.copy(secrets_file, temp_file)
            # read the copy of the credentials
            result = CredentialsManager("abc", temp_file)
            result.token = "replaced_token"
            result.save()
            # re-read the credentials
            new_result = CredentialsManager(None, temp_file)
        self.assertEqual(result.username, "abc")
        self.assertEqual(result.token, "replaced_token")
        self.assertEqual(new_result.username, "abc")
        self.assertEqual(new_result.token, "replaced_token")

    def test_save_multiple_credentials(self):
        """save should preserve multiple username/token information"""
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file = join(tempdir, "secrets_temp.yaml")
            shutil.copy(secrets_two_file, temp_file)
            # read the copy of the credentials
            result = CredentialsManager("two", temp_file)
            result.token = "replaced_token"
            result.save()
            # re-read the credentials
            result_one = CredentialsManager("one", temp_file)
            result_two = CredentialsManager("two", temp_file)
        # original manager should have information about username "one"
        self.assertEqual(result.username, "two")
        self.assertEqual(result.token, "replaced_token")
        # new manager for "one" should have a new token
        self.assertEqual(result_one.username, "one")
        self.assertEqual(result_one.token, "token_one")
        # new manager for "two" should still have the old token
        self.assertEqual(result_two.token, "replaced_token")

    def test_save_new_credentials(self):
        """start with non-existent file, then save credentials"""
        with tempfile.TemporaryDirectory() as tempdir:
            temp_file = join(tempdir, "new_secrets.yaml")
            result = CredentialsManager("xyz", temp_file)
            result.token = "token_xyz"
            result.save()
            # re-read the credentials
            new_result = CredentialsManager("xyz", temp_file)
        self.assertEqual(new_result.username, "xyz")
        self.assertEqual(new_result.token, "token_xyz")
