from typing import List

from .util import http, get_request_json, generate_pagination_list, get_filter_condition
from .global_obj import app
from .model import Manager, Building
from .auth import calc_password_hash
from .permission import get_permission_condition, check_permission_condition, PermissionDenied, require_role


manager_normal_properties = {
    "building": {
        "oneOf": [
            {
                "type": "null",
            },
            {
                "type": "integer",
            },
        ],
    },
    "leaved": {
        "type": "boolean",
    },
    "real_name": {
        "type": "string",
    },
    "enter_date": {
        "type": "string",
        "format": "date",
    },
    "leave_date": {
        "oneOf": [
            {
                "type": "string",
                "format": "date",
            },
            {
                "type": "null",
            },
        ],
    },
}


manager_filter_properties = dict(manager_normal_properties, id={
    "type": "integer",
})


manager_updatable_properties = dict(manager_normal_properties, password={
    "type": "string",
})


def get_managers(filter: dict, allowed: List[str]):
    return Manager.select().where(
        get_filter_condition(filter, Manager)
        & get_permission_condition(allowed, Manager)
    )


def generate_manager_info(manager: Manager) -> dict:
    return {
        "id": manager.id,
        "building": {
            "id": manager.building_id,
            "name": manager.building.name,
        },
        "leaved": manager.leaved,
        "real_name": manager.real_name,
        "enter_date": manager.enter_date,
        "leave_date": manager.leave_date,
    }


@app.route("/manager/list", methods=["POST"])
def get_manager_list():
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
                "properties": manager_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    managers = get_managers(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=managers,
        instance_generator=generate_manager_info,
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

    if "building" in obj:
        building_id = obj["building"]
        if building_id is not None:
            building = Building.get(id=building_id)
            check_permission_condition(building, get_permission_condition(["Management"], Building))


@app.route("/manager/update", methods=["POST"])
def update_manager_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": manager_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": manager_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    allow_read_manager = get_managers(instance["filter"], ["Management", "Self"])
    if allow_read_manager.count() < 1:
        raise Manager.DoesNotExist()

    allow_write_manager = get_managers(instance["filter"], ["Management"])
    if allow_write_manager.count() < 1:
        raise PermissionDenied()

    for manager in allow_write_manager:
        for (key, value) in instance["obj"].items():
            setattr(manager, key, value)
        manager.save()

    return http.Success()


@app.route("/manager/create", methods=["POST"])
@require_role(["Admin"])
def create_manager():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": manager_updatable_properties,
                "required": list(manager_updatable_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    manager = Manager()
    for (key, value) in instance["obj"].items():
        setattr(manager, key, value)

    manager.save()
    return http.Success(result={
        "id": manager.id,
    })
