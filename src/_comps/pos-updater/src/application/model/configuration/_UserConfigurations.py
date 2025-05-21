from application.model.configuration import DefaultManagerConfig


class UserConfigurations(DefaultManagerConfig):
    def __init__(self):

        super(UserConfigurations, self).__init__()
        self.endpoints = Endpoints()


class Endpoints(object):
    def __init__(self):
        self.employee = None
