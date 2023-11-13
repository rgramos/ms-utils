from functools import wraps

from flask import g, current_app

from ms_utils import abort_bad_request, abort_unauthorized, request_get, abort_forbidden


class NotAuthenticate(object):
    """
    Not Authentication Class
    """

    def dispatch_request(self, **kwargs):
        user = None
        try:
            response = request_get(f'{current_app.config.get("AUTH_MS_API")}/auth/check-authentication')
            if response.status_code == 200:
                user = response.json()['data']
        except Exception:
            pass
        g.setdefault('user', user)
        return super(NotAuthenticate, self).dispatch_request(**kwargs)


class IsAuthenticate(object):
    """
    Is Authenticate Class
    """

    def dispatch_request(self, **kwargs):
        config = current_app.config
        if not config.get('AUTH_MS_API'):
            abort_bad_request('The authentication API (AUTH_MS_API) is not configured')

        response = request_get(f'{current_app.config.get("AUTH_MS_API")}/auth/check-authentication')
        if not response.status_code == 200:
            abort_unauthorized()
        g.setdefault('user', response.json()['data'])
        return super(IsAuthenticate, self).dispatch_request(**kwargs)


def validate_permission(permission_required=None, permission_type="api"):
    if permission_required is None:
        abort_forbidden("You do not have permission for this request")

    config = current_app.config
    if not config.get('AUTH_MS_API'):
        abort_bad_request('The authentication API (AUTH_MS_API) is not configured')
    if not config.get('APP_NAME'):
        abort_bad_request('The app name (APP_NAME) is not configured')
    if not (isinstance(permission_required, tuple)
            or isinstance(permission_required, list)
            or isinstance(permission_required, set)):
        abort_bad_request('The permission_required variable must be iterable')
    response = request_get(f'{current_app.config.get("AUTH_MS_API")}/user-rol-permission/me', params={
        'not_paginate': True,
        'permission_type': permission_type,
        'app': config.get('APP_NAME')
    })
    if not response.status_code == 200:
        abort_unauthorized()
    permissions = response.json()['data']
    for permission in permission_required:
        if not any(permission == p['permission'] for p in permissions):
            abort_forbidden("You do not have permission for this request")
    return True


class ApiPermission(object):
    """
    Api Permission Class
    """
    permission_required = None
    permission_type = 'api'

    def dispatch_request(self, **kwargs):
        validate_permission(self.permission_required, self.permission_type)
        return super(ApiPermission, self).dispatch_request(**kwargs)


def view_decorator(func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            if func():
                return view_func(*args, **kwargs)
            abort_forbidden()

        return _wrapped_view

    return decorator


def permission_decorator(permissions):
    def check_perms():
        if isinstance(permissions, str):
            perms = (permissions,)
        else:
            perms = permissions
        return validate_permission(permissions)

    return view_decorator(check_perms)
