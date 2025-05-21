from production.box import NoJitAddTagBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class NoJitAddTagBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(NoJitAddTagBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> NoJitAddTagBox
        if u"Tag" not in config.extra_config:
            raise Exception("NoJitAddTagBoxBuilder without tag: {}".format(config.name))

        tag = config.extra_config[u"Tag"]

        return NoJitAddTagBox(config.name,
                              config.sons,
                              self.product_repository,
                              tag,
                              self.get_logger(config))
