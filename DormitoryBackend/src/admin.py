from typing import List

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, string_filter, get_filter_condition
from .global_obj import app
from .model import Admin
from .auth import calc_password_hash
from .permission import get_permission_condition, PermissionDenied, require_role


admin_filter_properties = {
    "id": id_filter,
    "name": string_filter,
}


admin_updatable_properties = {
    "name": {
        "type": "string",
    },
    "password": {
        "type": "string",
    },
}


def get_admins(filter: dict, allowed: List[str]):
    return Admin.select().where(
        get_filter_condition(filter, Admin)
        & get_permission_condition(allowed, Admin)
    )


def generate_admin_info(admin: Admin) -> dict:
    return {
        "id": admin.id,
        "name": admin.name,
    }


@app.route("/admin/list", methods=["POST"])
def get_admin_list():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
            },
            "limit": {
                "type": "integer",
            },
            "filter": {
                "type": "object",
                "properties": admin_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    admins = get_admins(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=admins,
        instance_generator=generate_admin_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


def obj_process(obj: dict):
    if "password" in obj:
        password: str = obj["password"]
        obj.pop("password")
        password_hash = calc_password_hash(password)
        obj["password_hash"] = password_hash


@app.route("/admin/update", methods=["POST"])
def update_admin_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": admin_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": admin_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    allow_read_admin = get_admins(instance["filter"], ["Management", "Self"])
    if allow_read_admin.count() < 1:
        raise Admin.DoesNotExist()

    allow_write_admin = get_admins(instance["filter"], ["Management"])
    if allow_write_admin.count() < 1:
        raise PermissionDenied()

    for admin in allow_write_admin:
        for (key, value) in instance["obj"].items():
            setattr(admin, key, value)
        admin.save()

    return http.Success()


@app.route("/admin/create", methods=["POST"])
@require_role(["Admin"])
def create_admin():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": admin_updatable_properties,
                "required": list(admin_updatable_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    admin = Admin()
    for (key, value) in instance["obj"].items():
        setattr(admin, key, value)

    admin.save()
    return http.Success(result={
        "id": admin.id,
    })
