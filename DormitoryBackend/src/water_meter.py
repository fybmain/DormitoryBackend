from typing import List

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, string_filter, decimal_filter, get_filter_condition
from .global_obj import app
from .model import WaterMeter
from .permission import get_permission_condition, PermissionDenied


water_meter_filter_properties = {
    "id": id_filter,
    "state": string_filter,
    "remaining": decimal_filter,
}


water_meter_updatable_properties = {
    "state": {
        "type": "string",
    },
}


def get_water_meters(filter: dict, allowed: List[str]):
    return WaterMeter.select().where(
        get_filter_condition(filter, WaterMeter)
        & get_permission_condition(allowed, WaterMeter)
    )


def generate_water_meter_info(water_meter: WaterMeter) -> dict:
    return {
        "id": water_meter.id,
        "state": water_meter.state,
        "remaining": float(water_meter.remaining),
    }


@app.route("/water_meter/list", methods=["POST"])
def get_water_meter_list():
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
                "properties": water_meter_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    water_meters = get_water_meters(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=water_meters,
        instance_generator=generate_water_meter_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/water_meter/update", methods=["POST"])
def update_water_meter_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": water_meter_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": water_meter_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_water_meter = get_water_meters(instance["filter"], ["Management", "Self"])
    if allow_read_water_meter.count() < 1:
        raise WaterMeter.DoesNotExist()

    allow_write_water_meter = get_water_meters(instance["filter"], ["Management"])
    if allow_write_water_meter.count() < 1:
        raise PermissionDenied()

    for water_meter in allow_write_water_meter:
        for (key, value) in instance["obj"].items():
            setattr(water_meter, key, value)
        water_meter.save()

    return http.Success()

