class DefaultManagerConfig(object):
    def __init__(self):

        self.enabled = None
        self.name = None
        self.active_frequency = None
        self.window = Window()


class Window(object):
    def __init__(self):
        self.start_time = None
        self.end_time = None
