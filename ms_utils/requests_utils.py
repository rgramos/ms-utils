import requests
from flask import request


def prepare_header(headers):
    """
    Prepare header
    """
    if headers is None:
        headers = {}
    authorization = ''
    app = ''
    if request:
        authorization = request.headers['Authorization'] if 'Authorization' in request.headers.keys() else ''
        app = request.headers['App'] if 'App' in request.headers.keys() else ''
    return {**{'Authorization': authorization, 'App': app}, **headers}


def request_get(url, params=None, headers=None):
    """
    Add authentication when sending "get" requests
    """
    if params is None:
        params = {}
    return requests.get(url, params=params, headers=prepare_header(headers))


def request_post(url, data=None, headers=None):
    """
    Add authentication when sending "post" requests
    """
    if data is None:
        data = {}
    return requests.post(url, json=data, headers=prepare_header(headers))
