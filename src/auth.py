import hashlib
from typing import Union
from enum import Enum
from flask import g
from itsdangerous import TimedJSONWebSignatureSerializer

from .util import http
from .util import get_request_json
from .global_obj import app
from .model import Manager, Student


serializer = TimedJSONWebSignatureSerializer(
    secret_key=app.config["SERVER_SECRET_KEY"],
    expires_in=app.config["LOGIN_EXPIRE_TIME"],
)


class AuthRoleType(Enum):
    manager = "Manager"
    student = "Student"


class AuthInfo:
    role: AuthRoleType
    token: str

    obj: Union[Manager, Student]


@app.route("/auth/manager/real_name/<string:real_name>", methods=["POST"])
def auth_student_by_real_name(real_name: str):
    manager = Manager.get(real_name=real_name)

    return auth_by_password(AuthRoleType.manager, manager)


@app.route("/auth/student/card_id/<string:card_id>", methods=["POST"])
def auth_student_by_card_id(card_id: str):
    student = Student.get(card_id=card_id)

    return auth_by_password(AuthRoleType.student, student)


def auth_by_password(role: AuthRoleType, obj: Union[Manager, Student]):
    instance = get_request_json({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "password": {
                "type": "string",
            },
        },
        "required": ["password"],
        "additionalProperties": False,
    })

    password_hash = calc_password_hash(instance["password"])

    if obj.password_hash == password_hash:
        auth_info = AuthInfo()
        auth_info.role = role
        auth_info.token = generate_token(role, obj)
        auth_info.obj = obj
        g.auth_info = auth_info
        return make_auth_echo()
    else:
        raise http.Conflict(reason="PasswordMismatch")


def calc_password_hash(password: str):
    salt: str = app.config["PASSWORD_HASH_SALT"]
    text: str = password + salt
    sha512 = hashlib.sha512()
    sha512.update(text.encode('UTF-8'))
    return sha512.hexdigest()


def generate_token(role: AuthRoleType, obj: Union[Manager, Student]):
    info = {
        "role": role.value,
        "id": obj.id,
    }
    return serializer.dumps(info).decode('ASCII')


def make_auth_echo():
    auth_info = g.auth_info
    if auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj
        result = {
            "token": auth_info.token,
            "realName": manager.real_name,
        }
    else:
        assert auth_info.role == AuthRoleType.student
        student: Student = auth_info.obj
        result = {
            "token": auth_info.token,
            "cardID": student.card_id,
            "realName": student.real_name,
        }
    return http.Success(result=result)
