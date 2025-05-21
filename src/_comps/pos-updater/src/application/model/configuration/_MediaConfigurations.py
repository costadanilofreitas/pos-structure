from application.model.configuration import DefaultManagerConfig


class MediaConfigurations(DefaultManagerConfig):
    def __init__(self):

        super(MediaConfigurations, self).__init__()
        self.images_directory = None
        self.endpoints = Endpoints()


class Endpoints(object):
    def __init__(self):
        self.get_download_image_permission = None
