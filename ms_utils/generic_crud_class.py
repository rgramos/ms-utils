"""
Generic Views
"""
from flask.views import MethodView, View
from ms_utils import ViewGeneralMethods


class ApiView(MethodView, ViewGeneralMethods):
    """
    Api Class
    """
    init_every_request = False
    post_validator = None
    patch_validator = None

    def get_post_validator(self):
        """
        Get validator
        """
        if self.post_validator is None:
            raise ValueError("'Validator' is not defined.")
        return self.post_validator

    def get_patch_validator(self):
        """
        Get validator
        """
        if self.patch_validator is None:
            raise ValueError("'Validator' is not defined.")
        return self.patch_validator


class BasicApiView(View, ViewGeneralMethods):
    init_every_request = False


class GenericItemCrud(ApiView):
    def get(self, object_id):
        return self.details(object_id)

    def patch(self, object_id):
        return self.update_or_create(self.get_patch_validator(), object_id)

    def delete(self, object_id):
        return super().delete(object_id)


class GenericGroupCrud(ApiView):
    def get(self):
        return self.list()

    def post(self):
        return self.update_or_create(self.get_post_validator())


class UrlsApi:
    blueprint = None
    url_name = 'generic-api'
    item_crud_class = GenericItemCrud
    group_crud_class = GenericGroupCrud

    def __init__(self):
        self.register_api()

    def get_blueprint(self):
        """
        Get validator
        """
        if self.blueprint is None:
            raise ValueError("'Blueprint' is not defined.")
        return self.blueprint

    def register_api(self):
        item = self.item_crud_class.as_view(f"{self.url_name}-item")
        self.add_url(f"/{self.url_name}/<int:object_id>", item)
        group = self.group_crud_class.as_view(f"{self.url_name}-group")
        self.add_url(f"/{self.url_name}/", group)

    def add_url(self, url, view_func):
        self.get_blueprint().add_url_rule(url, view_func=view_func)
