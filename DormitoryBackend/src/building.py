from .util import http, get_request_json, generate_all_list, generate_pagination_list, get_filter_condition
from .global_obj import app
from .model import Building
from .permission import get_permission_condition


def get_buildings(filter: dict):
    return Building.select().where(
        get_filter_condition(filter, Building)
        & get_permission_condition(["Management", "Self"], Building)
    )


def generate_building_info(building: Building) -> dict:
    return {
        "id": building.id,
        "name": building.name,
    }


@app.route("/building/all", methods=["POST"])
def get_building_all():
    buildings = get_buildings({})
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
                "properties": {
                    "id": {
                        "type": "integer",
                    },
                    "name": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    buildings = get_buildings(instance["filter"])
    result = generate_pagination_list(
        objs=buildings,
        instance_generator=generate_building_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)
