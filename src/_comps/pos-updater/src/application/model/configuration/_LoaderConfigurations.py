from application.model.configuration import DefaultManagerConfig


class LoaderConfigurations(DefaultManagerConfig):
    def __init__(self):
        super(LoaderConfigurations, self).__init__()
        self.endpoints = Endpoints()


class Endpoints(object):
    def __init__(self):
        self.download_loaders = None
