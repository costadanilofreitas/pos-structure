from application.model.configuration import DefaultManagerConfig


class CatalogConfigurations(DefaultManagerConfig):
    def __init__(self):

        super(CatalogConfigurations, self).__init__()
        self.endpoints = Endpoints()


class Endpoints(object):
    def __init__(self):
        self.get_latest_version = None
        self.download = None
        self.update_to = None
