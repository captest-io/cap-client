"""
handling api requests for search
"""

from .api import api_post, api_get


def build(api_url, credentials, **kwargs):
    """send a request to create a new search index"""
    url = api_url + "search/build/"
    return api_post(url, credentials.token, dict())


def summary(api_url, credentials, **kwargs):
    """send a request to create a new search index"""
    url = api_url + "search/summary/"
    return api_get(url, credentials.token)
