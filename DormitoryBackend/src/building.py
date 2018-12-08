from .util import http, get_request_json, generate_all_list, generate_pagination_list
from .global_obj import app
from .model import Building
from .permission import get_permission_condition


def get_buildings():
    return Building.select().where(get_permission_condition(["Management", "Self"], Building))


def generate_building_info(building: Building) -> dict:
    return {
        "id": building.id,
        "name": building.name,
    }


@app.route("/building/all", methods=["POST"])
def get_building_all():
    buildings = get_buildings()
    return http.Success(result=generate_all_list(buildings, generate_building_info))


@app.route("/building/list", methods=["POST"])
def get_building_list():
    request = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "page": {
                "type": "number",
            },
            "limit": {
                "type": "number",
            },
        },
        "required": ["page", "limit"],
        "additionalProperties": False,
    })
    buildings = get_buildings()
    result = generate_pagination_list(buildings, generate_building_info, **request)
    return http.Success(result=result)
