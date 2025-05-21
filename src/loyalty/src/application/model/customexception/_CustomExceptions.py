import json
from logging import Logger

from helper import json_serialize, remove_accents
from requests import Response


class ConfigurationReaderException(Exception):
    pass


class NotFound(Exception):
    pass


class ValidationError(Exception):
    pass


class ResponseError(Exception):
    def __init__(self, logger, response):
        # type: (Logger, Response) -> None

        self.logger = logger
        self.response = response
        self.error_status_code = response.status_code
        self.message = remove_accents(json.loads(response.content).get("detail"))

        self.logger.exception("Unexpected response received: {}. Response: \n{}".format(self.message,
                                                                                        json_serialize(response)))

        super(ResponseError, self).__init__(self.message)
