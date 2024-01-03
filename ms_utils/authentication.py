from functools import wraps

from flask import g, current_app, request

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


class HasHierarchy(object):
    """
    Has Hierarchy Class

    Class to verify users has a hierarchy, in that case modify a get_queryset method
    """
    config = current_app.config
    hierarchy_field = config.get('HIERARCHY_PAYLOAD_FIELD')

    def handle_validations(self):
        if not self.hierarchy_field:
            abort_bad_request('The hierarchy field (HIERARCHY_PAYLOAD_FIELD) is not configured')

        if not self.config.get('AUTH_MS_API'):
            abort_bad_request('The authentication API (AUTH_MS_API) is not configured')

    def get_hierarchy_users_list(self):
        """
        Return a list of users in my hierarchy
        :return:
        """
        try:
            response = request_get(f'{self.config.get("AUTH_MS_API")}/rol/hierarchy', params={
                'not_paginate': True
            })
            if not response.status_code == 200:
                abort_unauthorized()
            return response.json()['data']
        except Exception as e:
            abort_forbidden('Error al buscar el rol/hierarchy')

    def get_queryset(self):
        queryset = super(HasHierarchy, self).get_queryset()
        # Una vez obetnido el queryset aplicar el filtro de la herencia sobre el queryset obtenido y retornar
        hierarchy_users_list = self.get_hierarchy_users_list()
        if request.args.get(self.hierarchy_field) and request.args.get(self.hierarchy_field) in hierarchy_users_list:
            return queryset.filter_by(**{self.hierarchy_field: request.args.get(self.hierarchy_field)})
        # Aplicar el filtro cuando el id configurado(hierarchy_field) ente la lista
        condition = getattr(self.model, self.hierarchy_field).in_(hierarchy_users_list)
        queryset = queryset.filter_by(condition)
        return queryset

    def dispatch_request(self, **kwargs):
        # Valida que tenga configurada la variable HIERARCHY_PAYLOAD_FIELD y AUTH_MS_API
        self.handle_validations()

        # si hierarchy_field esta en los argumentos de la peticion o el "id" viene en la url entra
        if self.hierarchy_field in request.args or 'id' not in request.view_args:
            # Obtengo la lista de jerarqui por usuario (No vi que hubiera que pasarle ningun parametro)
            hierarchy_users_list = self.get_hierarchy_users_list()
            # Si el valor del hierarchy_field (el id que quiero buscar) esta en la lista de jerarquias de usuario o
            # el "id" viene en la url esta en la lista de jerarquias de usuario y no es el del usuario logado
            if (request.args.get(self.hierarchy_field) in hierarchy_users_list or
                    (request.view_args.get('id') in hierarchy_users_list
                     and request.view_args.get('id') != g.get('user')['id'])):
                # Devolver queryset para el id del campo hierarchy_field
                # Si llega aqui solo llama al super porque supuestamente al hacer super llamaria al get_queryset que seria el
                # que tendria q aplicar la jerarquia cuando le toque
                return super(HasHierarchy, self).dispatch_request(**kwargs)
            else:
                abort_forbidden("You do not have permission for this request")

        # Si llega aqui solo llama al super porque supuestamente al hacer super llamaria al get_queryset que seria el
        # que tendria q aplicar la jerarquia cuando le toque
        return super(HasHierarchy, self).dispatch_request(**kwargs)


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
