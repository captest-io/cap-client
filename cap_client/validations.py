"""
validation of command-line arguments
"""

from os.path import isdir, isfile
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


def validate_collection(collection, header):
    """checks that a collection (from cli) is consistent with a file header"""
    if "collection" not in header:
        raise ValidationError("header does not specify collection")
    if collection != header["collection"]:
        two = "'" + collection + "' and '" + header["collection"] + "'"
        raise ValidationError("inconsistent collection: "+two)
