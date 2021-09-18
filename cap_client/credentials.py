"""
Manager for credentials.

Features:
 - extracts oauth tokens from a local disk file
 - extracts passwords from a local disk file
 - saves tokens and passwords into a local disk file
 - fetches new oauth token from an api
 - does not save passwords into local disk file unless already present
"""

from os.path import exists
from yaml import safe_load, safe_dump
from .errors import ValidationError


class CredentialsManager:
    """Manages username, password, tokens using a disk file"""

    def __init__(self, username, path, token=None):
        """manages credentials for one username

        :param username: string, username
        :param path: string, path to local file with secrets
        :param token: set a token for the username
        """
        self.path = path
        self.data = None
        if exists(path):
            with open(path, "r") as f:
                self.data = safe_load(f)
        if self.data is None:
            self.data = dict()
        if type(self.data) is not dict:
            raise ValidationError("malformed secrets file")
        # if username is not specified, fetch it from the secrets file
        if username is None:
            try:
                username = list(self.data.keys())[0]
            except (AttributeError, IndexError):
                username = None
        self.username = username
        if username not in self.data:
            self.data[username] = dict()
        if token is not None:
            self.data[username]["token"] = token

    def __str__(self):
        str_username = "username: " + str(self.username)
        str_token = "token: "+str(self.token)
        return str_username + "\n" + str_token

    @property
    def token(self):
        try:
            return self.data[self.username]["token"]
        except KeyError:
            return None

    @token.setter
    def token(self, token):
        self.data[self.username]["token"] = token

    def save(self):
        """write secrets into a yaml file"""
        with open(self.path, "w") as f:
            safe_dump(self.data, f)
