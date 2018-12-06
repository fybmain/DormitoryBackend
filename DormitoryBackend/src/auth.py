import hashlib
from typing import Union, Tuple, Optional
from enum import Enum
from flask import g, request
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired

from .util import http
from .util import get_request_json
from .global_obj import app
from .model import Manager, Student


serializer = TimedJSONWebSignatureSerializer(
    secret_key=app.config["SERVER_SECRET_KEY"],
    expires_in=app.config["LOGIN_EXPIRE_TIME"],
)


class AuthRoleType(Enum):
    anonymous = "Anonymous"

    manager = "Manager"
    student = "Student"


class TokenStateType(Enum):
    not_exist = "TokenNotExist"
    broken = "BrokenToken"
    expired = "ExpiredToken"
    valid = "ValidToken"


class AuthInfo:
    token: str
    token_state: TokenStateType

    role: AuthRoleType
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

        auth_info.token = generate_token(role, obj)
        auth_info.token_state = TokenStateType.valid

        auth_info.role = role
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


def parse_token(token: str) -> Tuple[TokenStateType, Optional[AuthRoleType], Optional[int]]:
    try:
        info = serializer.loads(token)
    except BadSignature:
        return TokenStateType.broken, None, None
    except SignatureExpired:
        return TokenStateType.expired, None, None

    return TokenStateType.valid, AuthRoleType(info["role"]), info["id"]


def load_obj_by_id(role: AuthRoleType, id: int) -> Union[Manager, Student]:
    if role == AuthRoleType.manager:
        return Manager.get(id)
    elif role == AuthRoleType.student:
        return Student.get(id)
    else:
        raise ValueError()


def make_auth_echo():
    auth_info: AuthInfo = g.auth_info
    if auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj
        result = {
            "token": auth_info.token,
            "role": auth_info.role.value,
            "realName": manager.real_name,
        }
    elif auth_info.role == AuthRoleType.student:
        student: Student = auth_info.obj
        result = {
            "token": auth_info.token,
            "role": auth_info.role.value,
            "cardID": student.card_id,
            "realName": student.real_name,
        }
    else:
        result = {
            "token": auth_info.token,
            "role": auth_info.role.value,
        }
    return http.Success(result=result)


@app.before_request
def add_auth_info():
    auth_info: AuthInfo = AuthInfo()

    header_name = app.config["AUTH_TOKEN_HTTP_HEADER"]
    if header_name in request.headers:
        token = request.headers[header_name]
        auth_info.token = token

        (state, role, id) = parse_token(token)
        auth_info.token_state = state
    else:
        auth_info.token = None
        auth_info.token_state = TokenStateType.not_exist

    if auth_info.token_state == TokenStateType.valid:
        obj = load_obj_by_id(role, id)
        auth_info.role = role
        auth_info.obj = obj
    else:
        auth_info.role = AuthRoleType.anonymous
        auth_info.obj = None

    g.auth_info = auth_info
