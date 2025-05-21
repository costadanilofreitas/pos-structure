from cfgtools import read


class ConfiguratorReader:
    def __init__(self, loader_cfg, service_name, manager_name):
        self.service_name = service_name
        self.manager_name = manager_name

        self.reader = read(loader_cfg)

    def get_configuration(self, param):
        return self.reader.find_value(self.service_name + "." + self.manager_name + "." + param)
