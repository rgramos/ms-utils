import json

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
                response = json.loads(response.content)
                user = response['data']
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
        response = json.loads(response.content)
        g.setdefault('user', response['data'])
        return super(IsAuthenticate, self).dispatch_request(**kwargs)


class ApiPermission(object):
    """
    Api Permission Class
    """
    permission_required = None
    permission_type = 'api'

    def dispatch_request(self, **kwargs):
        if self.permission_required is not None:
            config = current_app.config
            if not config.get('AUTH_MS_API'):
                abort_bad_request('The authentication API (AUTH_MS_API) is not configured')
            if not config.get('APP_NAME'):
                abort_bad_request('The app name (APP_NAME) is not configured')
            if not (isinstance(self.permission_required, tuple)
                    or isinstance(self.permission_required, list)
                    or isinstance(self.permission_required, set)):
                abort_bad_request('The permission_required variable must be iterable')
            response = request_get(f'{current_app.config.get("AUTH_MS_API")}/user-rol-permission/me', params={
                'not_paginate': True,
                'permission_type': self.permission_type,
                'app': config.get('APP_NAME')
            })
            if not response.status_code == 200:
                abort_unauthorized()
            response = json.loads(response.content)
            permissions = response['data']
            for permission in self.permission_required:
                if not any(permission == p['permission'] for p in permissions):
                    abort_forbidden("You do not have permission for this request")
        return super(ApiPermission, self).dispatch_request(**kwargs)
