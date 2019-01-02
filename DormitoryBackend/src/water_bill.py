from typing import List
import datetime

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, datetime_filter, decimal_filter, foreign_key_filter, get_filter_condition
from .global_obj import app
from .model import WaterBill, WaterMeter
from .permission import get_permission_condition, PermissionDenied, require_role


water_bill_filter_properties = {
    "id": id_filter,
    "water_meter": foreign_key_filter,
    "record_time": datetime_filter,
    "money": decimal_filter,
}


water_bill_updatable_properties = {
    "water_meter": {
        "type": "integer",
    },
    "record_time": {
        "type": "string",
        "format": "date-time",
    },
    "money": {
        "type": "number",
    },
}


water_bill_create_properties = {
    "water_meter": {
        "type": "integer",
    },
    "money": {
        "type": "number",
    },
}


def get_water_bills(filter: dict, allowed: List[str]):
    return WaterBill.select().where(
        get_filter_condition(filter, WaterBill)
        & get_permission_condition(allowed, WaterBill)
    )


def generate_water_bill_info(water_bill: WaterBill) -> dict:
    return {
        "id": water_bill.id,
        "water_meter": water_bill.water_meter_id,
        "record_time": water_bill.record_time,
        "money": float(water_bill.money),
    }


@app.route("/water_bill/list", methods=["POST"])
def get_water_bill_list():
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
                "properties": water_bill_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    water_bills = get_water_bills(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=water_bills,
        instance_generator=generate_water_bill_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/water_bill/update", methods=["POST"])
def update_water_bill_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": water_bill_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": water_bill_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_water_bill = get_water_bills(instance["filter"], ["Management", "Self"])
    if allow_read_water_bill.count() < 1:
        raise WaterBill.DoesNotExist()

    allow_write_water_bill = get_water_bills(instance["filter"], ["Management"])
    if allow_write_water_bill.count() < 1:
        raise PermissionDenied()

    if allow_write_water_bill.count() > 1:
        raise http.NotImplemented(detail="OnlySingleRecordUpdateSupported")

    water_bill = allow_write_water_bill[0]
    water_meter = WaterMeter.get(id=water_bill.water_meter_id)
    water_meter.remaining = water_meter.remaining - water_bill.money
    water_meter.save()

    if "water_meter" in instance["obj"]:
        water_bill.water_meter = instance["obj"]["water_meter"]
    if "record_time" in instance["obj"]:
        water_bill.record_time = instance["obj"]["record_time"]
    if "money" in instance["obj"]:
        water_bill.money = instance["obj"]["money"]

    water_meter = WaterMeter.get(id=water_bill.water_meter_id)
    water_meter.remaining = water_meter.remaining + water_bill.money
    water_meter.save()

    water_bill.save()
    return http.Success()


@app.route("/water_bill/create", methods=["POST"])
@require_role(["Admin"])
def create_water_bill():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": water_bill_create_properties,
                "required": list(water_bill_create_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })

    water_bill = WaterBill()
    for (key, value) in instance["obj"].items():
        setattr(water_bill, key, value)
    water_bill.record_time = datetime.datetime.now()

    water_meter = WaterMeter.get(id=water_bill.water_meter_id)
    water_meter.remaining = water_meter.remaining + water_bill.money
    water_meter.save()

    water_bill.save()
    return http.Success(result={
        "id": water_bill.id,
    })
