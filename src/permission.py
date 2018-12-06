from typing import List
from flask import g
from peewee import fn

from .model import Manager, Student
from .model import Building
from .model import Department
from .model import Dormitory
from .model import ElectricityMeter, ElectricityBill
from .model import WaterMeter, WaterBill
from .auth import AuthRoleType, AuthInfo


def get_management_condition(model: type):
    auth_info: AuthInfo = g.auth_info
    if auth_info.role == AuthRoleType.manager:
        manager: Manager = g.auth_info.obj

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
    if auth_info.role == AuthRoleType.manager:
        manager: Manager = auth_info.obj
        if issubclass(model, Manager):
            return model.id == manager.id
        else:
            return False
    else:
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


def get_permission_condition(allowed: List[str], model: type):
    auth_info: AuthInfo = g.auth_info

    condition = False
    if "Anyone" in allowed:
        condition = True
        return condition

    if "Anonymous" in allowed:
        condition = condition|(auth_info.role==AuthRoleType.anonymous)
    if "Manager" in allowed:
        condition = condition|(auth_info.role==AuthRoleType.manager)
    if "Student" in allowed:
        condition = condition|(auth_info.role==AuthRoleType.student)

    if "Management" in allowed:
        condition = condition|get_management_condition(model)
    if "Self" in allowed:
        condition = condition|get_self_condition(model)

    return condition
