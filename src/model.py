from peewee import ForeignKeyField
from peewee import CharField, DecimalField
from peewee import DateTimeField, DateField
from peewee import BooleanField
from src.global_obj import database as db


class Building(db.Model):
    name = CharField(255, null=False)


class Department(db.Model):
    name = CharField(255, null=False)


class ElectricityMeter(db.Model):
    state = CharField(20, null=False)


class ElectricityBill(db.Model):
    electricity_meter = ForeignKeyField(ElectricityMeter, null=False)
    remaining = DecimalField(10, 2, null=False)
    record_time = DateTimeField(null=False)


class WaterMeter(db.Model):
    state = CharField(20, null=False)


class WaterBill(db.Model):
    water_meter = ForeignKeyField(WaterMeter, null=False)
    remaining = DecimalField(10, 2, null=False)
    record_time = DateTimeField(null=False)


class Dormitory(db.Model):
    number = CharField(20, null=False)
    building = ForeignKeyField(Building, null=False)
    electricity_meter = ForeignKeyField(ElectricityMeter, null=False)
    water_meter = ForeignKeyField(WaterMeter, null=False)


class Manager(db.Model):
    password_hash = CharField(255, null=False)

    building = ForeignKeyField(Building, null=True)

    leaved = BooleanField(null=False)
    real_name = CharField(255, null=False)
    enter_date = DateField(null=False)
    leave_date = DateField(null=True)


class Student(db.Model):
    card_id = CharField(10, null=False)
    password_hash = CharField(255, null=False)

    real_name = CharField(255, null=False)
    gender = CharField(20, null=False)
    birth_date = DateField(null=False)
    enroll_date = DateField(null=False)
    graduate_date = DateField(null=True)
    department = ForeignKeyField(Department, null=False)

    leaved = BooleanField(null=False)
    abnormal = BooleanField(null=False)
    dormitory = ForeignKeyField(Dormitory, null=True)


model_list = [
    Building,
    Department,
    ElectricityMeter,
    ElectricityBill,
    WaterMeter,
    WaterBill,
    Dormitory,
    Manager,
    Student,
]
