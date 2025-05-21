from production.box.condition import ConditionBox, CustomPropertyCondition, PodTypeCondition, \
    CustomPropertyValuesCondition, OrderStateCondition
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ConditionBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ConditionBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ConditionBox
        return ConditionBox(config.name,
                            self.get_condition(config.extra_config),
                            config.sons[0],
                            config.sons[1],
                            self.get_logger(config))

    def get_condition(self, config):
        condition_config = config["Condition"]
        if condition_config["Name"] == "CustomPropertyCondition":
            return CustomPropertyCondition(condition_config["PropertyName"])
        if condition_config["Name"] == "CustomPropertyValuesCondition":
            return CustomPropertyValuesCondition(condition_config["PropertyName"], condition_config.get("AllowedValues"), condition_config.get("ExcludedValues"))
        if condition_config["Name"] == "PodTypeCondition":
            return PodTypeCondition(condition_config["ValidPodTypes"])
        if condition_config["Name"] == "OrderStateCondition":
            return OrderStateCondition(condition_config["OrderStates"])
