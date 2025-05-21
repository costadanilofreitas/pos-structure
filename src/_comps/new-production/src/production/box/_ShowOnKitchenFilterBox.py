from ._ItemFilterBox import ItemFilterBox


class ShowOnKitchenFilterBox(ItemFilterBox):

    def __init__(self, name, sons, product_repository, logger=None):
        super(ShowOnKitchenFilterBox, self).__init__(name,
                                                     sons,
                                                     None,
                                                     product_repository.get_not_show_on_kitchen(),
                                                     None,
                                                     "False",
                                                     logger)
