from production.box import DecreaseTimeTagBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class DecreaseTimeTagBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(DecreaseTimeTagBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> DecreaseTimeTagBox
        def get_config(config_name):
            return self.get_extra_config(config, config_name)

        return DecreaseTimeTagBox(config.name,
                                  config.sons,
                                  self.get_logger(config),
                                  get_config)

    def get_extra_config(self, config, config_name):
        config_value = self.get_extra(config, config_name, None)
        if config_value is None:
            self.loggers['DEBUG'].info("({}) does not exist".format(config_name))
            raise Exception("({}) does not exist".format(config_name))

        return config_value
