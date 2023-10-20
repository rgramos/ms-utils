import requests
from flask import request


def request_get(url, params=None, headers=None):
    """
    Add authentication when sending "get" requests
    """
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    authorization = request.headers['Authorization'] if 'Authorization' in request.headers.keys() else ''
    return requests.get(url, params=params, headers={**{'Authorization': authorization}, **headers})


def request_post(url, data=None, headers=None):
    """
    Add authentication when sending "post" requests
    """
    if headers is None:
        headers = {}
    if data is None:
        data = {}
    authorization = request.headers['Authorization'] if 'Authorization' in request.headers.keys() else ''
    return requests.post(url, json=data, headers={**{'Authorization': authorization}, **headers})
