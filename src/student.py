from math import ceil

from .util import http, get_request_json
from .global_obj import app
from .model import Student, Department, Dormitory
from .permission import get_permission_condition, check_permission_condition


def get_student_by_id(id: int) -> Student:
    return (
        Student
        .select()
        .where(Student.id == id)
        .get()
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


@app.route("/student/list/page/<int:page_num>", methods=["GET"])
def get_student_list_page(page_num: int):
    students = (
        Student
        .select()
        .where(get_permission_condition(["Management", "Self"], Student))
    )
    student_count = students.count()
    student_list = students.paginate(page_num)
    instance_list = [generate_student_info(student) for student in student_list]
    return http.Success(result={
        "page_count": int(ceil(student_count/20)),
        "list": instance_list,
    })


@app.route("/student/id/<int:id>", methods=["GET"])
def get_student_info(id: int):
    student = get_student_by_id(id)
    check_permission_condition(student, get_permission_condition(["Management", "Self"], Student))
    return http.Success(result=generate_student_info(student))


@app.route("/student/id/<int:id>", methods=["PUT"])
def update_student_info(id: int):
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
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
            "abnormal": {
                "type": "boolean",
            },
            "dormitory": {
                "type": "number",
            }
        },
        "additionalProperties": False,
    })
    student = get_student_by_id(id)
    check_permission_condition(student, get_permission_condition(["Management"], Student))

    if "department" in instance:
        department_id = instance["department"]
        department = Department.get(id=department_id)

    if "dormitory" in instance:
        dormitory_id = instance["dormitory"]
        dormitory = Dormitory.get(id=dormitory_id)

    for (key, value) in instance.items():
        setattr(student, key, value)

    student.save()
    return http.Success()
