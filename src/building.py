from .util import http
from .global_obj import app
from .model import Building


@app.route("/building/list/all", methods=["GET"])
def get_all_building_list():
    building_list = Building.select()
    instance_list = [{
        "id": building.id,
        "name": building.name,
    } for building in building_list]

    return http.Success(result={
        "list": instance_list,
    })
