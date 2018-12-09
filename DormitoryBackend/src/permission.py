from functools import wraps
from typing import List
from flask import g
from peewee import fn

from .util import http
from .global_obj import database as db
from .model import Admin, Manager, Student
from .model import Building
from .model import Department
from .model import Dormitory
from .model import ElectricityMeter, ElectricityBill
from .model import WaterMeter, WaterBill
from .auth import AuthRoleType, AuthInfo


def get_management_condition(model: type):
    auth_info: AuthInfo = g.auth_info
    if auth_info.role == AuthRoleType.admin:
        return True
    elif auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj

        if issubclass(model, Building):
            return model.id == manager.building
        elif issubclass(model, Department):
            return False
        elif issubclass(model, Dormitory):
            return model.building == manager.building
        elif issubclass(model, ElectricityMeter):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == manager.building)&(DM.electricity_meter == model.id))
            )
        elif issubclass(model, ElectricityBill):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == manager.building)&(DM.electricity_meter == model.electricity_meter))
            )
        elif issubclass(model, WaterMeter):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == manager.building)&(DM.water_meter == model.id))
            )
        elif issubclass(model, WaterBill):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == manager.building)&(DM.water_meter == model.water_meter))
            )
        elif issubclass(model, Manager):
            return False
        elif issubclass(model, Student):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == manager.building)&(model.dormitory == DM.id))
            )
        else:
            assert False
    else:
        return False


def get_self_condition(model: type):
    auth_info: AuthInfo = g.auth_info
    if auth_info.role == AuthRoleType.admin:
        admin: Admin = auth_info.obj
        if issubclass(model, Admin):
            return model.id == admin.id
        else:
            return False
    if auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj
        if issubclass(model, Manager):
            return model.id == manager.id
        else:
            return False
    elif auth_info.role == AuthRoleType.student:
        student: Student = auth_info.obj

        if issubclass(model, Building):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == model.id)&(DM.id == student.dormitory))
            )
        elif issubclass(model, Department):
            return False
        elif issubclass(model, Dormitory):
            return model.id == student.dormitory
        elif issubclass(model, ElectricityMeter):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.electricity_meter == model.id)&(DM.id == student.dormitory))
            )
        elif issubclass(model, ElectricityBill):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.electricity_meter == model.electricity_meter)&(DM.id == student.dormitory))
            )
        elif issubclass(model, WaterMeter):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                    .select()
                    .where((DM.water_meter == model.id) & (DM.id == student.dormitory))
            )
        elif issubclass(model, ElectricityBill):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.electricity_meter == model.water_meter)&(DM.id == student.dormitory))
            )
        elif issubclass(model, Manager):
            DM = Dormitory.alias()
            return fn.EXISTS(
                DM
                .select()
                .where((DM.building == model.building)&(DM.id == student.dormitory))
            )
        elif issubclass(model, Student):
            return model.id == student.id
        else:
            assert False
    elif auth_info.role == AuthRoleType.anonymous:
        return False


def get_permission_condition(allowed: List[str], model: type):
    auth_info: AuthInfo = g.auth_info

    condition = False
    if "Anyone" in allowed:
        condition = True
        return condition

    if "Anonymous" in allowed:
        condition = condition|(auth_info.role == AuthRoleType.anonymous)
    if "Admin" in allowed:
        condition = condition|(auth_info.role == AuthRoleType.admin)
    if "Manager" in allowed:
        condition = condition|(auth_info.role == AuthRoleType.manager)
    if "Student" in allowed:
        condition = condition|(auth_info.role == AuthRoleType.student)

    if "Management" in allowed:
        condition = condition|get_management_condition(model)
    if "Self" in allowed:
        condition = condition|get_self_condition(model)

    return condition


class PermissionDenied(http.Forbidden):
    def __init__(self):
        super().__init__(reason="PermissionDenied")


def check_permission_condition(obj: db.Model, condition):
    model = obj.__class__
    count = (
        model
        .select()
        .where((model.id == obj.id) & condition)
        .count()
    )
    if count < 1:
        raise PermissionDenied()
    else:
        return


def require_role(allowed_rule: List[str]):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_info: AuthInfo = g.auth_info
            if auth_info.role.value in allowed_rule:
                return func(*args, **kwargs)
            else:
                raise PermissionDenied()

        return wrapper

    return decorator
