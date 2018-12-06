import jsonschema
from flask import request, json

from .http import BadRequest


def get_request_json(schema: dict, force=True, silent=False, cache=True):
    instance = request.get_json(force=force, silent=silent, cache=cache)
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError:
        raise BadRequest(reason="InvalidRequestInstance")
    return instance


def to_json(obj: dict):
    return json.dumps(obj)
