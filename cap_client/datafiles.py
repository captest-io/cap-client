"""
handling api requests for assignments
"""

from os.path import basename
from .api import api_get, api_post, api_upload


def list_datafiles(api_url, credentials, parent_uuid):
    """fetch all datafiles associated with a given parent object"""
    url = api_url + "data/list/" + parent_uuid + "/"
    return api_get(url, credentials.token)


def upload(api_url, credentials, file_path, file_role,
           parent_uuid, parent_type):
    url = api_url + "data/upload/"
    metadata = {
        "file_role": file_role,
        "file_name": basename(file_path),
        "parent_uuid": parent_uuid,
        "parent_type": parent_type
    }
    return api_upload(url, credentials.token, file_path, metadata)


def remove(api_url, credentials, uuid):
    url = api_url + "data/remove/"
    body = {"uuid": uuid}
    return api_post(url, credentials.token, body)
