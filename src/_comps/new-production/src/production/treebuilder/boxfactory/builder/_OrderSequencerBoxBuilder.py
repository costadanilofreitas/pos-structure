from production.box import OrderSequencerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderSequencerBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(OrderSequencerBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository
        self.pod_types = []
        self.invert = False

    def build(self, config):
        # type: (BoxConfiguration) -> OrderSequencerBox
        if u"Sorters" not in config.extra_config:
            raise Exception("Sequencer without Sorters: {}".format(config.name))

        sorted_sorters = self.get_sorted_sorters(config.extra_config[u"Sorters"])

        if u"PodTypes" in config.extra_config:
            self.pod_types = config.extra_config[u"PodTypes"]
        if u"Invert" in config.extra_config:
            self.invert = (config.extra_config[u"Invert"].lower() or "") == "true"

        sorters = []
        for sorter_config in sorted_sorters:
            sorters.append(self.build_sorter(sorter_config))

        return OrderSequencerBox(config.name,
                                 config.sons,
                                 sorters,
                                 self.get_logger(config))

    def get_sorted_sorters(self, sorters):
        sorters_list = []
        for sorter in sorters.keys():
            sorters_list.append((sorter, sorters[sorter]))

        return sorted(sorters_list, self.sorter_comparator)

    def sorter_comparator(self, s1, s2):
        return int(s1[1]) - int(s2[1])

    def build_sorter(self, sorter):
        if sorter[0] == "DoneInFrontSorter":
            return OrderSequencerBox.DoneInFrontSorter()
        elif sorter[0] == "LastModifiedSorter":
            return OrderSequencerBox.LastModifiedSorter(self.invert)
        elif sorter[0] == "DisplayTimeSorter":
            return OrderSequencerBox.DisplayTimeSorter(self.invert)
        elif sorter[0] == "PriorityCustomerSorter":
            return OrderSequencerBox.PriorityCustomerSorter()
        elif sorter[0] == "OrderIdSorter":
            return OrderSequencerBox.OrderIdSorter()
        elif sorter[0] == "DoneSorter":
            return OrderSequencerBox.DoneSorter()
        elif sorter[0] == "PodTypeSorter":
            return OrderSequencerBox.PodTypeSorter(
                self.pod_types[sorter[0]].split("|") if sorter[0] in self.pod_types else []
            )
        else:
            raise Exception("Not implemented sorter: {}".format(sorter))
