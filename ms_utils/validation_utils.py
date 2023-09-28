"""
Validation utils
"""
from marshmallow import Schema, EXCLUDE

from .prepare_json_response import prepare_json_response


def validate_generic_form(validation_class, body):
    """
    Generic validation form
    :param validation_class: Validation class
    :param body: dict
    :return: jsonfy | None
    """
    if body is None:
        raise TypeError('Cannot validate an object of type None')
    errors = validation_class().validate(body)
    if errors:
        return prepare_json_response('Validation Error', False, {'errors': errors}, 422)
    return None


class BaseSchema(Schema):
    class Meta:
        """
        Meta
        """
        unknown = EXCLUDE
