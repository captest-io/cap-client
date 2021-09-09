"""
handling api requests for assignments
"""

from urllib.request import urlretrieve
from .api import api_get, api_post
from .datafiles import list_datafiles


def list_assignments(api_url, credentials):
    url = api_url+"assignment/"+credentials.username
    return api_get(url, credentials.token)


def submit(api_url, credentials, uuid, tags=None):
    url = api_url+"assignment/submit/"+uuid
    tags = "" if tags is None else tags
    return api_post(url, credentials.token, {"tags": tags})


def start(api_url, credentials, uuid=None, name=None, version=None):
    """start a new assignment"""
    url = api_url+"assignment/create/"
    body = {"name": name, "version": version}
    if uuid is not None:
        body = {"uuid": uuid}
    return api_post(url, credentials.token, body)


def download(api_url, credentials, uuid):
    """download data files from the server for one assignment"""
    datafiles = list_datafiles(api_url, credentials, uuid)
    for f in datafiles:
        f_url = api_url+"static/"+f["path"]
        f_basename = f_url.split("/")[-1]
        urlretrieve(f_url, f_basename)
    return datafiles


def view(api_url, credentials, uuid):
    """view the status (including score) of an assignment"""
    url = api_url+"assignment/view/"+uuid
    return api_get(url, credentials.token)

