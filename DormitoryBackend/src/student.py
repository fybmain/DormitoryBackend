from typing import List

from .util import http, get_request_json, generate_pagination_list, generate_all_list, get_filter_condition
from .global_obj import app
from .model import Student, Department, Dormitory
from .permission import get_permission_condition, check_permission_condition, PermissionDenied


student_normal_properties = {
    "card_id": {
        "type": "string",
        "pattern": "^[0-9]+$",
    },
    "real_name": {
        "type": "string",
    },
    "gender": {
        "type": "string",
        "pattern": "^(Male|Female)$",
    },
    "birth_date": {
        "type": "string",
        "format": "date",
    },
    "enroll_date": {
        "type": "string",
        "format": "date",
    },
    "graduate_date": {
        "type": "string",
        "format": "date",
    },
    "department": {
        "type": "number",
    },
    "leaved": {
        "type": "boolean",
    },
    "dormitory": {
        "type": "number",
    },
}


student_filter_properties = dict(student_normal_properties, id={
    "type": "number",
})


def get_students(filter: dict, allowed: List[str]):
    return Student.select().where(
        get_filter_condition(filter, Student)
        & get_permission_condition(allowed, Student)
    )


def generate_student_info(student: Student) -> dict:
    return {
        "card_id": student.card_id,
        "real_name": student.real_name,
        "gender": student.gender,
        "birth_date": student.birth_date,
        "enroll_date": student.enroll_date,
        "graduate_date": student.graduate_date,
        "department": {
            "id": student.department_id,
            "name": student.department.name,
        },
        "leaved": student.leaved,
        "abnormal": student.abnormal,
        "dormitory": (None if student.dormitory is None else{
            "id": student.dormitory_id,
            "number": student.dormitory.number,
            "building": {
                "id": student.dormitory.building_id,
                "name": student.dormitory.building.name,
            },
        }),
    }


@app.route("/student/list", methods=["POST"])
def get_student_list():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "page": {
                "type": "number",
            },
            "limit": {
                "type": "number",
            },
            "filter": {
                "type": "object",
                "properties": student_filter_properties,
                "additionalProperties": False,
            },
        },
        "required": ["page", "limit", "filter"],
        "additionalProperties": False,
    })
    students = get_students(instance["filter"], ["Management", "Self"])
    return http.Success(result=generate_pagination_list(
        objs=students,
        instance_generator=generate_student_info,
        page=instance["page"],
        limit=instance["limit"]
    ))


@app.route("/student/update", methods=["POST"])
def update_student_info():
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": student_filter_properties,
                "additionalProperties": False,
            },
            "obj": {
                "type": "object",
                "properties": student_normal_properties,
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    })

    if "department" in instance:
        department_id = instance["department"]
        department = Department.get(id=department_id)
        check_permission_condition(department, get_permission_condition(["Management"], Department))

    if "dormitory" in instance:
        dormitory_id = instance["dormitory"]
        dormitory = Dormitory.get(id=dormitory_id)
        check_permission_condition(dormitory, get_permission_condition(["Management"], Dormitory))

    allow_read_student = get_students(instance["filter"], ["Management", "Self"])
    if allow_read_student.count() < 1:
        raise Student.DoesNotExist()

    allow_write_student = get_students(instance["filter"], ["Management"])
    if allow_write_student.count() < 1:
        raise PermissionDenied()

    for student in allow_write_student:
        for (key, value) in instance["obj"].items():
            setattr(student, key, value)
        student.save()

    return http.Success(result=generate_all_list(allow_write_student, generate_student_info))
