from typing import List

from .util import http, get_request_json, generate_all_list, generate_pagination_list
from .util import id_filter, string_filter, get_filter_condition
from .global_obj import app
from .model import Building
from .permission import get_permission_condition, PermissionDenied, require_role


building_normal_properties = {
    "name": {
        "type": "string",
    },
}
building_updatable_properties = dict(building_normal_properties)

building_filter_properties = {
    "id": id_filter,
    "name": string_filter,
}


def get_buildings(filter: dict, allowed: List[str]):
    return Building.select().where(
        get_filter_condition(filter, Building)
        & get_permission_condition(allowed, Building)
    )


def generate_building_info(building: Building) -> dict:
    return {
        "id": building.id,
        "name": building.name,
    }


@app.route("/building/all", methods=["POST"])
def get_building_all():
    buildings = get_buildings({}, ["Management", "Self"])
    return http.Success(result=generate_all_list(buildings, generate_building_info))


@app.route("/building/list", methods=["POST"])
def get_building_list():
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
                "properties": building_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    buildings = get_buildings(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=buildings,
        instance_generator=generate_building_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/building/update", methods=["POST"])
def update_building_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": building_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": building_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_building = get_buildings(instance["filter"], ["Management", "Self"])
    if allow_read_building.count() < 1:
        raise Building.DoesNotExist()

    allow_write_building = get_buildings(instance["filter"], ["Management"])
    if allow_write_building.count() < 1:
        raise PermissionDenied()

    for building in allow_write_building:
        for (key, value) in instance["obj"].items():
            setattr(building, key, value)
        building.save()

    return http.Success()


@app.route("/building/create", methods=["POST"])
@require_role(["Admin"])
def create_building():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": building_updatable_properties,
                "required": list(building_updatable_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })

    building = Building()
    for (key, value) in instance["obj"].items():
        setattr(building, key, value)

    building.save()
    return http.Success(result={
        "id": building.id,
    })
