from typing import List

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, string_filter, decimal_filter, get_filter_condition
from .global_obj import app
from .model import ElectricityMeter
from .permission import get_permission_condition, PermissionDenied


electricity_meter_filter_properties = {
    "id": id_filter,
    "state": string_filter,
    "remaining": decimal_filter,
}


electricity_meter_updatable_properties = {
    "state": {
        "type": "string",
    },
}


def get_electricity_meters(filter: dict, allowed: List[str]):
    return ElectricityMeter.select().where(
        get_filter_condition(filter, ElectricityMeter)
        & get_permission_condition(allowed, ElectricityMeter)
    )


def generate_electricity_meter_info(electricity_meter: ElectricityMeter) -> dict:
    return {
        "id": electricity_meter.id,
        "state": electricity_meter.state,
        "remaining": float(electricity_meter.remaining),
    }


@app.route("/electricity_meter/list", methods=["POST"])
def get_electricity_meter_list():
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
                "properties": electricity_meter_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    electricity_meters = get_electricity_meters(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=electricity_meters,
        instance_generator=generate_electricity_meter_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/electricity_meter/update", methods=["POST"])
def update_electricity_meter_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": electricity_meter_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": electricity_meter_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_electricity_meter = get_electricity_meters(instance["filter"], ["Management", "Self"])
    if allow_read_electricity_meter.count() < 1:
        raise ElectricityMeter.DoesNotExist()

    allow_write_electricity_meter = get_electricity_meters(instance["filter"], ["Management"])
    if allow_write_electricity_meter.count() < 1:
        raise PermissionDenied()

    for electricity_meter in allow_write_electricity_meter:
        for (key, value) in instance["obj"].items():
            setattr(electricity_meter, key, value)
        electricity_meter.save()

    return http.Success()

