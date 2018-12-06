from math import ceil

from .util import http, get_request_json
from .global_obj import app
from .model import Dormitory, Building, ElectricityMeter, WaterMeter
from .permission import get_permission_condition, check_permission_condition


def generate_dormitory_info(dormitory: Dormitory):
    return {
        "id": dormitory.id,
        "number": dormitory.number,
        "building": {
            "id": dormitory.building_id,
            "name": dormitory.building.name,
        },
        "electricity_meter": dormitory.electricity_meter_id,
        "water_meter": dormitory.water_meter_id,
    }


@app.route("/dormitory/list/page/<int:page_num>", methods=["GET"])
def get_dormitory_list(page_num: int):
    dormitories = (
            Dormitory
            .select()
            .where(get_permission_condition(["Management", "Self"], Dormitory))
    )
    dormitory_count = dormitories.count()
    dormitory_list = dormitories.paginate(page_num)
    instance_list = [generate_dormitory_info(dormitory) for dormitory in dormitory_list]
    return http.Success(result={
        "page_count": int(ceil(dormitory_count/20)),
        "list": instance_list,
    })


@app.route("/dormitory/id/<int:id>", methods=["GET"])
def get_dormitory_by_id(id: int):
    dormitory = Dormitory.get(id=id)
    check_permission_condition(dormitory, get_permission_condition(["Management", "Self"], Dormitory))
    return http.Success(result=generate_dormitory_info(dormitory))


@app.route("/dormitory/id/<int:id>", methods=["PUT"])
def update_dormitory_info(id: int):
    instance = get_request_json(schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "number": {
                "type": "string",
            },
            "building": {
                "type": "number",
            },
            "electricity_meter": {
                "type": "number",
            },
            "water_meter": {
                "type":"number",
            },
        },
        "additionalProperties": False,
    })
    dormitory = Dormitory.get(id=id)
    check_permission_condition(dormitory, get_permission_condition(["Management"], Dormitory))

    if "building" in instance:
        building_id = instance["building"]
        building = Building.get(id=building_id)

    if "electricity_meter" in instance:
        electricity_meter_id = instance["electricity_meter"]
        electricity_meter = ElectricityMeter.get(id=electricity_meter_id)

    if "water_meter" in instance:
        water_meter_id = instance["water_meter"]
        water_meter = WaterMeter.get(id=water_meter_id)

    for (key, value) in instance.items():
        setattr(dormitory, key, value)

    dormitory.save()
    return http.Success()
