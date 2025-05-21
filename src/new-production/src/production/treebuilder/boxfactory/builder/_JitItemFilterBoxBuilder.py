from production.box import JitItemFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class JitItemFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(JitItemFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> JitItemFilterBox

        excluded_jit_lines = self.get_extra(config, "ExcludedJitLines", None)
        forbidden_jit_lines = self.get_extra(config, "ForbiddenJitLines", excluded_jit_lines)

        return JitItemFilterBox(config.name,
                                config.sons,
                                self.product_repository,
                                self.get_extra(config, "AllowedJitLines", None),
                                forbidden_jit_lines,
                                self.get_extra(config, "ShowAllItems", "False"),
                                self.get_logger(config))
