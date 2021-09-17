"""
validation of command-line arguments
"""

from os.path import isdir, isfile
from getpass import getpass
from .errors import ValidationError


def validate_config(config):
    if "file" in config and config.file is not None:
        if not isfile(config.file):
            raise ValidationError("file does not exist: "+str(config.file))
    if "dir" in config and config.dir is not None:
        if not isdir(config.dir):
            raise ValidationError("directory does not exist: "+str(config.dir))
    if not config.api.endswith("/"):
        config.api += "/"
    if not config.api.startswith("http"):
        config.api = "https://"+config.api
    if config.action == "list" and config.collection == "datafile":
        if config.parent_uuid is None:
            raise ValidationError("parent_uuid is required")
    return config


def validate_credentials(credentials):
    if credentials.username is None:
        raise ValidationError("could not determine username")
    # get credentials from interactive prompt if not yet available
    if credentials.token is None:
        credentials.token = getpass("Oauth token: ")
    if credentials.token is None:
        raise ValidationError("could not identify authorization token")
    return credentials


def validate_collection(collection, header):
    """checks that a collection (from cli) is consistent with a file header"""
    if "collection" not in header:
        raise ValidationError("header does not specify collection")
    if collection != header["collection"]:
        two = "'" + collection + "' and '" + header["collection"] + "'"
        raise ValidationError("inconsistent collection: "+two)


def validate_notes(header):
    """check that certain documents have a notes field in the header"""
    notes = header.get("notes", "")
    header["notes"] = notes
    if header["collection"] not in ("challenge", "resource", "image"):
        return header
    if len(str(notes)) < 4:
        raise ValidationError("notes are short (use more than 4 characters)")
    return header

