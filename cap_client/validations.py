"""
validation of command-line arguments
"""

from os.path import isdir, isfile
from .errors import ValidationError


def validate_config(config):
    if config.action in ("publish", "create"):
        if config.collection is None:
            raise ValidationError("missing --collection")
    if config.action == "datafiles":
        if config.parent_uuid is None:
            raise ValidationError("missing --parent_uuid")
    if config.file is not None:
        if not isfile(config.file):
            raise ValidationError("file does not exist: "+str(config.file))
    if config.dir is not None:
        if not isdir(config.dir):
            raise ValidationError("directory does not exist: "+str(config.dir))
    if not config.api.endswith("/"):
        config.api += "/"
    if not config.api.startswith("http"):
        config.api = "http://"+config.api
    return config


def validate_collection(collection, header):
    """checks that a collection (from cli) is consistent with a file header"""
    if "collection" not in header:
        raise ValidationError("header does not specify collection")
    if collection != header["collection"]:
        two = "'" + collection + "' and '" + header["collection"] + "'"
        raise ValidationError("inconsistent collection: "+two)
