"""
perform get and post requests
"""

import requests
import logging
import json
from os.path import isfile


def starts_slash(url):
    """ensure that a string starts with a slash"""
    return url if url.startswith("/") else "/" + url


def ends_slash(url):
    """ensure that a string ends with a slash"""
    return url if url.endswith("/") else url + "/"


class Api:
    """Base class for interfacing with captest API endpoints"""

    def __init__(self, api_url, credentials):
        """base class for interfacing with API endpoints

        :param api_url: base url for api
        :param credentials: object with authorization token
        """
        self.api_url = api_url
        while self.api_url.endswith("/"):
            self.api_url = self.api_url[:-1]
        self.credentials = credentials
        self.username = credentials.username
        self.token = credentials.token

    def get(self, url):
        """perform a GET request

        :param url: string, api endpoint
        :return: output object
        """
        headers = {"Authorization": "Bearer " + self.token}
        full_url = self.api_url + starts_slash(url)
        logging.info("GET url: " + str(full_url))
        logging.info("GET header: " + str(headers))
        try:
            result = requests.get(full_url, headers=headers).json()
        except json.decoder.JSONDecodeError:
            result = "error parsing JSON response"
        logging.info("GET result: " + str(result))
        return result

    def post(self, url, body):
        """perform a POST request

        :param url: string, api endpoint
        :param body: dictionary with post body
        :return: output object
        """
        full_url = self.api_url + starts_slash(ends_slash(url))
        headers = {"Authorization": "Bearer " + self.token}
        logging.info("POST url: " + str(full_url))
        logging.info("POST header: " + str(headers))
        logging.info("POST body " + str(body))
        result = requests.post(url=full_url, headers=headers,
                               json=body).json()
        logging.info("POST result: " + str(result))
        return result

    def post_upload(self, url, file_path, metadata):
        """perform a post request for a file upload

        :param url: string, api endpoint
        :param file_path: string, path to file
        :param metadata: dictionary with metadata
        :return: output object
        """
        full_url = self.api_url + starts_slash(ends_slash(url))
        headers = {"Authorization": "Bearer " + self.token}
        body = {"metadata": json.dumps(metadata)}
        logging.info("POST url: " + str(full_url))
        logging.info("POST header: " + str(headers))
        logging.info("POST body: " + str(body))
        filedata = None
        if isfile(file_path):
            filedata = {"filedata": open(file_path, "rb")}
        result = requests.post(url=full_url, headers=headers,
                               files=filedata, data=body).json()
        logging.info("POST result: "+str(result))
        return result
