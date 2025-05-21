from typing import Dict


class ApiRequest(object):
    def __init__(self, method, api_path, path_parameters, query_parameters, headers, body):
        # type: (str, str, Dict[str, str], Dict[str, str], Dict[str, str], bytes) -> None
        self.method = method
        self.api_path = api_path
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.headers = headers
        self.body = body

    def __str__(self):
        body = self.body
        if isinstance(self.body, str):
            body = self.body.decode("utf-8")
        return u"ApiRequest('{}', {}, {}, '{}', {}, '{}')".format(self.method,
                                                                  self.api_path,
                                                                  self.path_parameters,
                                                                  self.query_parameters,
                                                                  self.headers,
                                                                  body)

    def __repr__(self):
        return self.__str__()
