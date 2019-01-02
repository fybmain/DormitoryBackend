from typing import List

from .util import http, get_request_json, generate_pagination_list
from .util import id_filter, foreign_key_filter, date_filter, decimal_filter, get_filter_condition
from .global_obj import app
from .model import DormitoryRating, Dormitory
from .permission import get_permission_condition, check_permission_condition, PermissionDenied


dormitoryrating_filter_properties = {
    "id": id_filter,
    "dormitory": foreign_key_filter,
    "date": date_filter,
    "rating": decimal_filter,
}


dormitoryrating_updatable_properties = {
    "dormitory": {
        "type": "integer",
    },
    "date": {
        "type": "string",
        "format": "date",
    },
    "rating": {
        "type": "number",
    },
}


def get_dormitories(filter: dict, allowed: List[str]):
    return DormitoryRating.select().where(
        get_filter_condition(filter, DormitoryRating)
        & get_permission_condition(allowed, DormitoryRating)
    )


def generate_dormitoryrating_info(dormitoryrating: DormitoryRating):
    return {
        "id": dormitoryrating.id,
        "dormitory": {
            "id": dormitoryrating.dormitory_id,
            "name": dormitoryrating.dormitory.name,
        },
        "date": dormitoryrating.date,
        "rating": dormitoryrating.rating,
    }


@app.route("/dormitoryrating/list", methods=["POST"])
def get_dormitoryrating_list():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
            },
            "limit": {
                "oneOf": [
                    {
                        "type": "null",
                    },
                    {
                        "type": "integer",
                    },
                ],
            },
            "filter": {
                "type": "object",
                "properties": dormitoryrating_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    dormitories = get_dormitories(instance["filter"], ["Management", "Self"])
    if instance["limit"] is None:
        instance["limit"] = dormitories.count()
    return http.Success(result=generate_pagination_list(
        objs=dormitories,
        instance_generator=generate_dormitoryrating_info,
        page=instance["page"],
        limit=instance["limit"]
    ))


def obj_process(obj: dict):
    if "dormitory" in obj:
        dormitory_id = obj["dormitory"]
        dormitory = Dormitory.get(id=dormitory_id)
        check_permission_condition(dormitory, get_permission_condition(["Management"], Dormitory))


@app.route("/dormitoryrating/update", methods=["POST"])
def update_dormitoryrating_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": dormitoryrating_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": dormitoryrating_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    allow_read_dormitoryrating = get_dormitories(instance["filter"], ["Management", "Self"])
    if allow_read_dormitoryrating.count() < 1:
        raise DormitoryRating.DoesNotExist()

    allow_write_dormitoryrating = get_dormitories(instance["filter"], ["Management"])
    if allow_write_dormitoryrating.count() < 1:
        raise PermissionDenied()

    for dormitoryrating in allow_write_dormitoryrating:
        for(key, value) in instance["obj"].items():
            setattr(dormitoryrating, key, value)
        dormitoryrating.save()

    return http.Success()


@app.route("/dormitoryrating/create", methods=["POST"])
def create_dormitoryrating():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": dormitoryrating_updatable_properties,
                "required": list(dormitoryrating_updatable_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })
    obj_process(instance["obj"])

    dormitoryrating = DormitoryRating()
    for (key, value) in instance["obj"].items():
        setattr(dormitoryrating, key, value)

    dormitoryrating.save()
    return http.Success(result={
        "id": dormitoryrating.id,
    })
