from typing import List

from .util import http, get_request_json, generate_all_list, generate_pagination_list, get_filter_condition
from .global_obj import app
from .model import Department
from .permission import get_permission_condition, PermissionDenied, require_role


department_normal_properties = {
    "name": {
        "type": "string",
    },
}


department_filter_properties = dict(department_normal_properties, id={
    "type": "integer",
})
department_updatable_properties = dict(department_normal_properties)


def get_departments(filter: dict, allowed: List[str]):
    return Department.select().where(
        get_filter_condition(filter, Department)
        & get_permission_condition(allowed, Department)
    )


def generate_department_info(department: Department) -> dict:
    return {
        "id": department.id,
        "name": department.name,
    }


@app.route("/department/all", methods=["POST"])
def get_department_all():
    departments = get_departments({}, ["Management", "Self"])
    return http.Success(result=generate_all_list(departments, generate_department_info))


@app.route("/department/list", methods=["POST"])
def get_department_list():
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
                "properties": department_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    departments = get_departments(instance["filter"], ["Management", "Self"])
    result = generate_pagination_list(
        objs=departments,
        instance_generator=generate_department_info,
        page=instance["page"],
        limit=instance["limit"]
    )
    return http.Success(result=result)


@app.route("/department/update", methods=["POST"])
def update_department_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": department_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": department_updatable_properties,
                "additionalProperties": False,
            },
        },
        "required": ["filter", "obj"],
        "additionalProperties": False,
    })

    allow_read_department = get_departments(instance["filter"], ["Management", "Self"])
    if allow_read_department.count() < 1:
        raise Department.DoesNotExist()

    allow_write_department = get_departments(instance["filter"], ["Management"])
    if allow_write_department.count() < 1:
        raise PermissionDenied()

    for department in allow_write_department:
        for (key, value) in instance["obj"].items():
            setattr(department, key, value)
        department.save()

    return http.Success()


@app.route("/department/create", methods=["POST"])
@require_role(["Admin"])
def create_department():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "obj": {
                "type": "object",
                "properties": department_updatable_properties,
                "required": list(department_updatable_properties.keys()),
                "additionalProperties": False,
            },
        },
        "required": ["obj"],
        "additionalProperties": False,
    })

    department = Department()
    for (key, value) in instance["obj"].items():
        setattr(department, key, value)

    department.save()
    return http.Success(result={
        "id": department.id,
    })
