"""
validation of command-line arguments
"""

import getpass
import logging
from os.path import isdir, isfile, basename
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
    return config


def validate_credentials(credentials):
    if credentials.username is None:
        raise ValidationError("could not determine username")
    # attempt to get token through an interactive prompt
    if credentials.token is None:
        credentials.token = getpass.getpass("Oauth token: ")
    if credentials.token is None or credentials.token == "":
        raise ValidationError("could not determine authorization token")
    return credentials


def validate_collection(header, collection):
    """checks that a collection (from cli) is consistent with a file header"""
    if "collection" not in header:
        raise ValidationError("header does not specify collection")
    header["collection"] = header["collection"].lower()
    if collection != header["collection"]:
        two = "'" + collection + "' and '" + header["collection"] + "'"
        raise ValidationError("inconsistent collection: "+two)
    return header


def validate_notes(header):
    """check that certain documents have a notes field in the header"""
    notes = header.get("notes", "")
    header["notes"] = notes
    if header["collection"] not in ("challenge", "resource", "image"):
        return header
    if len(str(notes)) < 4:
        raise ValidationError("notes are short (use more than 4 characters)")
    return header


def validate_naming(header, file_path):
    """check naming conventions (information in header matches with filename)

    These checks can log warnings, but do not raise errors.
    """
    file_basename = basename(file_path)
    if header["name"].replace(".", "-") not in file_basename.replace(".", "-"):
        logging.warning("file name and document name do not overlap:")
        logging.warning("file name: " + file_path)
        logging.warning("document name: " + header["name"])
    if str(header["version"]) not in file_basename:
        logging.warning("file name and document version do not overlap:")
        logging.warning("file name: " + file_path)
        logging.warning("document version: " + str(header["version"]))
    return header
