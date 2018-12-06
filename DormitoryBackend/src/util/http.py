import werkzeug.exceptions
from flask import json
from flask import Response


OK = 200


class Success(Response):
    def __init__(self, *args, **kwargs):
        body = {
            "status": "Success"
        }

        if len(args) > 0:
            assert(len(args) == 1)
            body.update(args[0])

        body.update(kwargs)

        response = json.dumps(body)

        super().__init__(response, status=200, mimetype="application/json")


class HTTPException(werkzeug.exceptions.HTTPException):
    code = None
    _reason = None

    @property
    def reason(self) -> str:
        if self._reason is None:
            return self.__class__.__name__
        else:
            return self._reason

    def __init__(self, *args, **kwargs):
        super().__init__()

        body = {
            "status": "Failed",
            "reason": self.reason
        }

        if len(args) > 0:
            assert(len(args) == 1)
            body.update(args[0])

        body.update(kwargs)

        if body["reason"] != self.reason:
            self._reason = body["reason"]

        self.body = body

    @property
    def description(self) -> str:
        return json.dumps(self.body)

    def get_description(self, environ=None) -> str:
        return self.description

    def get_body(self, environ=None) -> str:
        return self.get_description()

    def get_headers(self, environ=None):
        return [("Content-Type", "application/json")]


class BadRequest(HTTPException):
    code = 400


class Unauthorized(HTTPException):
    code = 401


class Forbidden(HTTPException):
    code = 403


class NotFound(HTTPException):
    code = 404


class NotAcceptable(HTTPException):
    code = 406


class Conflict(HTTPException):
    code = 409


class Gone(HTTPException):
    code = 410


class InternalServerError(HTTPException):
    code = 500


class NotImplemented(HTTPException):
    code = 501
