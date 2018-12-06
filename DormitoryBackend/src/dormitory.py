from math import ceil

from .util import http
from .global_obj import app
from .model import Dormitory
from .permission import get_permission_condition, check_permission_condition


def generate_dormitory_info(dormitory: Dormitory):
    return {
        "id": dormitory.id,
        "number": dormitory.number,
        "building": {
            "id": dormitory.building_id,
            "name": dormitory.building.name,
        },
        "electricity_meter_id": dormitory.electricity_meter_id,
        "water_meter_id": dormitory.water_meter_id,
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
