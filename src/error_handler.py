from peewee import DoesNotExist
from .util import http
from .global_obj import app


@app.errorhandler(DoesNotExist)
def does_not_exist_handler(e):
    return http.NotFound(reason=e.__class__.__name__).get_response()
