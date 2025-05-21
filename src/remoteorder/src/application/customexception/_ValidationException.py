class ValidationException(Exception):
    def __init__(self, error_code, localized_error_message, i18n_tag=""):
        # type: (unicode, unicode, unicode) -> None
        self.error_code = error_code
        self.message = self.localized_error_message = localized_error_message
        self.i18n_tag = i18n_tag

    def __str__(self):
        # type: () -> unicode
        return '{}{}: {}'.format(type(self), self.error_code, self.localized_error_message)

    def __repr__(self):
        # type: () -> unicode
        return self.__str__()
