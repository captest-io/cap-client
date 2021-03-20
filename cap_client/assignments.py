"""
handling api requests for assignments
"""

from .api import api_get, api_post


def list_assignments(api_url, credentials):
    url = api_url+"assignment/"+credentials.username
    return api_get(url, credentials.token)


def submit(api_url, credentials, uuid):
    url = api_url+"assignment/submit/"+uuid
    return api_post(url, credentials.token, {})
