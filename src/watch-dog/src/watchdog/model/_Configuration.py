class Configuration(object):
    def __init__(self, service_name, time_to_wait_to_start_watching, components):
        self.service_name = service_name
        self.time_to_wait_to_start_watching = time_to_wait_to_start_watching
        self.components = components
