from .util import http
from .global_obj import app
from .model import Student
from .permission import get_permission_condition


@app.route("/student/id/<int:id>", methods=["GET"])
def get_student_info(id: int):
    student = (
        Student
        .select()
        .where((Student.id==id)&(get_permission_condition(["Management", "Self"], Student)))
        .get()
    )

    return http.Success(result={
        "cardID": student.card_id,
        "realName": student.real_name,
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
        }),
    })
