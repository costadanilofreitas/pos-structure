from ._SwaggerMessage import SwaggerMessage


class JsonSwaggerMessage(SwaggerMessage):
    def __init__(self, status_code, body=None, headers=None):
        if headers is None:
            headers = {}

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json; charset=utf-8"

        super(JsonSwaggerMessage, self).__init__(status_code, body, headers)
