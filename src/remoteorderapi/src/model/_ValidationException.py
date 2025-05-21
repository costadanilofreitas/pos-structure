class ValidationException(Exception):
    def __init__(self, error_code, localized_error_message):
        # type: (unicode, unicode) -> None
        self.error_code = error_code
        self.localized_error_message = localized_error_message
