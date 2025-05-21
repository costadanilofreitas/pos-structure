from production.box import JitAddTagBox
from production.model import TagNotFoundException
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class JitAddTagBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(JitAddTagBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> JitAddTagBox
        if u"Tag" not in config.extra_config:
            raise TagNotFoundException("JitAddTagBoxBuilder without tag: {}".format(config.name))

        tag = config.extra_config[u"Tag"]

        return JitAddTagBox(config.name,
                            config.sons,
                            self.product_repository,
                            tag,
                            self.get_extra(config, "JitLines", []),
                            self.get_logger(config))
