from typing import List
import datetime

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, datetime_filter, decimal_filter, foreign_key_filter, get_filter_condition
from .global_obj import app
from .model import ElectricityBill, ElectricityMeter
from .permission import get_permission_condition, PermissionDenied, require_role


electricity_bill_filter_properties = {
    "id": id_filter,
    "electricity_meter": foreign_key_filter,
    "record_time": datetime_filter,
    "money": decimal_filter,
}


electricity_bill_updatable_properties = {
    "electricity_meter": {
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


electricity_bill_create_properties = {
    "electricity_meter": {
        "type": "integer",
    },
    "money": {
        "type": "number",
    },
}


def get_electricity_bills(filter: dict, allowed: List[str]):
    return ElectricityBill.select().where(
        get_filter_condition(filter, ElectricityBill)
        & get_permission_condition(allowed, ElectricityBill)
    )


def generate_electricity_bill_info(electricity_bill: ElectricityBill) -> dict:
    return {
        "id": electricity_bill.id,
        "electricity_meter": electricity_bill.electricity_meter_id,
        "record_time": electricity_bill.record_time,
        "money": float(electricity_bill.money),
    }


@app.route("/electricity_bill/list", methods=["POST"])
def get_electricity_bill_list():
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
                "properties": electricity_bill_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    electricity_bills = get_electricity_bills(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=electricity_bills,
        instance_generator=generate_electricity_bill_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/electricity_bill/update", methods=["POST"])
def update_electricity_bill_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": electricity_bill_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": electricity_bill_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_electricity_bill = get_electricity_bills(instance["filter"], ["Management", "Self"])
    if allow_read_electricity_bill.count() < 1:
        raise ElectricityBill.DoesNotExist()

    allow_write_electricity_bill = get_electricity_bills(instance["filter"], ["Management"])
    if allow_write_electricity_bill.count() < 1:
        raise PermissionDenied()

    if allow_write_electricity_bill.count() > 1:
        raise http.NotImplemented(detail="OnlySingleRecordUpdateSupported")

    electricity_bill = allow_write_electricity_bill[0]
    electricity_meter = ElectricityMeter.get(id=electricity_bill.electricity_meter_id)
    electricity_meter.remaining = electricity_meter.remaining - electricity_bill.money
    electricity_meter.save()

    if "electricity_meter" in instance["obj"]:
        electricity_bill.electricity_meter = instance["obj"]["electricity_meter"]
    if "record_time" in instance["obj"]:
        electricity_bill.record_time = instance["obj"]["record_time"]
    if "money" in instance["obj"]:
        electricity_bill.money = instance["obj"]["money"]

    electricity_meter = ElectricityMeter.get(id=electricity_bill.electricity_meter_id)
    electricity_meter.remaining = electricity_meter.remaining + electricity_bill.money
    electricity_meter.save()

    electricity_bill.save()
    return http.Success()


@app.route("/electricity_bill/create", methods=["POST"])
@require_role(["Admin"])
def create_electricity_bill():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": electricity_bill_create_properties,
                "required": list(electricity_bill_create_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })

    electricity_bill = ElectricityBill()
    for (key, value) in instance["obj"].items():
        setattr(electricity_bill, key, value)
    electricity_bill.record_time = datetime.datetime.now()

    electricity_meter = ElectricityMeter.get(id=electricity_bill.electricity_meter_id)
    electricity_meter.remaining = electricity_meter.remaining + electricity_bill.money
    electricity_meter.save()

    electricity_bill.save()
    return http.Success(result={
        "id": electricity_bill.id,
    })
