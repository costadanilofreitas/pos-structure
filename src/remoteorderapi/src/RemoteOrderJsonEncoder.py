from flask.json import JSONEncoder
from InternalError import InternalError
from customexception import ValidationException


class RemoteOrderJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, InternalError):
            return {
                "errorMessage": obj.error_message
            }

        if isinstance(obj, ValidationException):
            return {
                "errorCode": obj.error_code,
                "localizedErrorMessage": obj.localized_error_message
            }

        return super(RemoteOrderJsonEncoder, self).default(obj)
