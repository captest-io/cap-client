"""
perform get and post requests
"""

import requests
import logging
import json
from os.path import isfile


def ends_slash(url):
    return url if url.endswith("/") else url + "/"


def api_get(url, token):
    """perform a get request

    :param url: string, url to api
    :param token: string, authorization token
    :return: output object
    """

    headers = {"Authorization": "Bearer "+token}
    logging.info("GET url: "+str(url))
    logging.info("GET header: "+str(headers))
    try:
        result = requests.get(url, headers=headers).json()
    except json.decoder.JSONDecodeError:
        result = "error parsing JSON response"
    logging.info("GET result: "+str(result))
    return result


def api_post(url, token, body):
    """perform a post request

    :param url: string, url to api
    :param token: string, authorization token
    :param body: dictionary with post body
    :return: output object
    """

    url = ends_slash(url)
    headers = {"Authorization": "Bearer "+token}
    logging.info("POST url: "+str(url))
    logging.info("POST header: "+str(headers))
    logging.info("POST body "+str(body))
    result = requests.post(url=url, headers=headers,
                           json=body).json()
    logging.info("POST result: "+str(result))
    return result


def api_upload(url, token, file_path, metadata):
    """perform a post request for a file upload

    :param url: string, url to api
    :param token: string, authorization token
    :param file_path: string, path to file
    :param metadata: dictionary with metadata
    :return: output object
    """

    url = ends_slash(url)
    headers = {"Authorization": "Bearer "+token}
    body = {"metadata": json.dumps(metadata)}
    logging.info("POST url: "+str(url))
    logging.info("POST header: "+str(headers))
    logging.info("POST body: "+str(body))
    filedata = None
    if isfile(file_path):
        filedata = {"filedata": open(file_path, "rb")}
    result = requests.post(url=url, headers=headers,
                           files=filedata, data=body).json()
    logging.info("POST result: "+str(result))
    return result
