class LoginSummaryBodyDto(object):
    def __init__(self, initial_value, pos_type, authorizer):
        # type: (float, unicode, unicode) -> ()
        self.initial_value = initial_value
        self.pos_type = pos_type
        self.authorizer = authorizer
