"""
Manager for credentials.

Features:
 - extracts oauth tokens from a local disk file
 - extracts passwords from a local disk file
 - saves tokens and passwords into a local disk file
 - fetches new oauth token from an api
 - does not save passwords into local disk file unless already present
"""

from os import getcwd
from os.path import join, exists, abspath
from yaml import safe_load, safe_dump


def default_secrets_path():
    return join(getcwd(), "secrets.yaml")


class CredentialsManager:
    """Manages username, password, tokens using a disk file"""

    def __init__(self, username, path, token=None):
        """manages credentials for one username

        :param username: string, username
        :param path: string, path to local file with secrets
        :param token: set a token for the username
        """
        print(str(path))
        print(str(abspath(path)))
        self._path = path
        self._password = None
        self._token = None
        self._data = dict()
        if exists(path):
            with open(path, "r") as f:
                self._data = safe_load(f)
        # if username is not specified, fetch it from the secrets file
        if username is None:
            try:
                username = list(self._data.keys())[0]
            except IndexError:
                username = None
        self._username = username
        if username not in self._data:
            self._data[username] = dict()
        if token is not None:
            self.token = token

    def __str__(self):
        return "username: "+self._username + "\ntoken: "+self._token

    @property
    def username(self):
        return self._username

    def _get(self, key):
        try:
            return self._data[self._username][key]
        except KeyError:
            return None

    @property
    def token(self):
        if self._token is None:
            self._token = self._get("token")
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        if "token" in self._data[self._username]:
            self._data[self._username]["token"] = token

    def save(self):
        """write secrets into a yaml file"""

        path = self._path
        if path is None:
            path = default_secrets_path()
        with open(path, "w") as f:
            safe_dump(self._data, f)
