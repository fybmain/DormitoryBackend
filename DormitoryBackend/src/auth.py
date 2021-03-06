import hashlib
from typing import Union, Tuple, Optional
from enum import Enum
from flask import g, request
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, SignatureExpired

from .util import http
from .util import get_request_json
from .global_obj import app
from .model import Admin, Manager, Student


serializer = TimedJSONWebSignatureSerializer(
    secret_key=app.config["SERVER_SECRET_KEY"],
    expires_in=app.config["LOGIN_EXPIRE_TIME"],
)


class AuthRoleType(Enum):
    anonymous = "Anonymous"

    admin = "Admin"
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


@app.route("/auth/getinfo", methods=["POST"])
def getinfo():
    from flask import request
    if not(request.get_json()):
        return http.Success()
    instance = get_request_json({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "token": {
                "type": "string",
            },
        },
        "required": ["token"],
        "additionalProperties": False,
    })

    valid, role, user_id = parse_token(instance['token'])
    if not valid:
        return http.Success()
    if role == AuthRoleType.admin:
        user = Admin.get(id=user_id)
        result = {
            "roles": [role.value],
            "name": user.name
        }
    elif role == AuthRoleType.manager:
        user = Manager.get(id=user_id)
        result = {
            "roles": [role.value],
            "name": user.real_name
        }
    else:
        user = Student.get(id=user_id)
        result = {
            "roles": [role.value],
            "name": user.real_name
        }

    return http.Success(result=result)


@app.route("/auth/login", methods=["POST"])
def login():
    from flask import request
    print(request.get_json())
    instance = get_request_json({
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "pattern": "^(Admin|Manager|Student)$",
            },
            "account": {
                "type": "string",
            },
            "password": {
                "type": "string",
            },
        },
        "required": ["role", "account", "password"],
        "additionalProperties": False,
    })

    role = AuthRoleType(instance["role"])
    account = instance["account"]
    if role == AuthRoleType.admin:
        user = Admin.get(name=account)
    elif role == AuthRoleType.manager:
        user = Manager.get(real_name=account)
    else:
        user = Student.get(card_id=account)

    password_hash = calc_password_hash(instance["password"])

    if user.password_hash == password_hash:
        auth_info = AuthInfo()

        auth_info.token = generate_token(role, user)
        auth_info.token_state = TokenStateType.valid

        auth_info.role = role
        auth_info.obj = user

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
    if role == AuthRoleType.admin:
        return Admin.get(id)
    elif role == AuthRoleType.manager:
        return Manager.get(id)
    elif role == AuthRoleType.student:
        return Student.get(id)
    else:
        raise ValueError()


def make_auth_echo():
    auth_info: AuthInfo = g.auth_info
    if auth_info.role == AuthRoleType.admin:
        admin: Admin = auth_info.obj
        result = {
            "token": auth_info.token,
            "role": [auth_info.role.value],
            "name": admin.name,
        }
    elif auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj
        result = {
            "token": auth_info.token,
            "role": [auth_info.role.value],
            "name": manager.real_name,
        }
    elif auth_info.role == AuthRoleType.student:
        student: Student = auth_info.obj
        result = {
            "token": auth_info.token,
            "role": [auth_info.role.value],
            "card_id": student.card_id,
            "name": student.real_name,
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


@app.route("/auth/echo", methods=["POST"])
def auth_echo_request_handler():
    return make_auth_echo()
