from logging import Logger

from production.box import ProductionBox
from production.command import ProductionCommandProcessor
from production.manager import PublishScheduler, OrderChanger, StatisticUpdater
from production.repository import ProductRepository
from production.treebuilder import BoxConfiguration
from production.treebuilder.boxfactory.builder import OrderStateFilterBoxBuilder, OrderSubTypeFilterBoxBuilder, \
    JitItemFilterBoxBuilder, HideOptionBoxBuilder, AllDoneBlinkBoxBuilder, ComboDoneWhenAllDoneBoxBuilder, \
    OrderSequencerBoxBuilder, RemoveDoingWhenDoneBoxBuilder, OrderStateTimerBoxBuilder, \
    FromOrderStateFilterBoxBuilder, CustomParamCourseBoxBuilder, CustomParamPrepTimeBoxBuilder, \
    ShowOnKitchenFilterBoxBuilder, NoJitAddTagBoxBuilder, ItemPropertiesFilterBoxBuilder, AllServedItemsBoxBuilder, \
    SendMomentTimerBuilder, ConditionBoxBuilder, CFHHiderBoxBuilder, CustomPropertyFilterBoxBuilder, \
    ComboFilterBoxBuilder, DistributorBoxBuilder, CustomParamPointerBoxBuilder, OrderRoundRobinBoxBuilder, \
    RemoveDeletedItemsBoxBuilder, FilterDeletedItemsBeforeFirstStateBoxBuilder, OrderSpreaderBoxBuilder, \
    OrderStampBoxBuilder, OrderMergerBoxBuilder, RecalledOrderStampBoxBuilder, ComboServedWhenAllServedBoxBuilder, \
    FilterOrderIfNotAllItemsHaveTagBoxBuilder, AllItemsDoneBoxBuilder, RemoveReprocessedOrdersBoxBuilder, \
    ProductCodeFilterBoxBuilder, OrderProductCategoryFilterBoxBuilder, PodTypeFilterBoxBuilder, \
    SaleTypeFilterBoxBuilder, SkipCourseBoxBuilder, CollapseSameItemsBoxBuilder, StampItemsViewBoxBuilder, \
    ItemSequencerBoxBuilder, StatisticBoxBuilder, AddTimeTagBoxBuilder, ProdStateFilterBoxBuilder, \
    CustomPropertyValueFilterBoxBuilder, ItemSorterBoxBuilder, DisplayTimeFilterBoxBuilder, ProdStateTimerBoxBuilder, \
    DecreaseTimeTagBoxBuilder, AllItemHasAtLeastOneTagFilterBoxBuilder, FilterOrderIfAllItemsHaveTagBoxBuilder, \
    FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBoxBuilder, ComboTaggedWhenAllHasTagBoxBuilder, SorterBoxBuilder, \
    TagItemsWhenProdStateBoxBuilder, FilterDefaultQuantityIngredientsBoxBuilder, JitAddTagBoxBuilder, \
    ReprocessOrdersBoxBuilder

from production.view import ProductionView
from typing import Dict

from .builder import TagFilterBoxBuilder, ViewBoxBuilder


class ProductionBoxFactory(object):
    def __init__(self, command_processor, publish_scheduler, order_changer, statistic_updater, product_repository, loggers):
        # type: (ProductionCommandProcessor, PublishScheduler, OrderChanger, StatisticUpdater, ProductRepository, Dict[str, Logger]) -> None  # noqa
        self.command_processor = command_processor
        self.publish_scheduler = publish_scheduler
        self.order_changer = order_changer
        self.product_repository = product_repository
        self.loggers = loggers

        self.builders = {
            u"TagFilterBox": TagFilterBoxBuilder(loggers),
            u"OrderStateFilterBox": OrderStateFilterBoxBuilder(product_repository, loggers),
            u"OrderSubTypeFilterBox": OrderSubTypeFilterBoxBuilder(product_repository, loggers),
            u"JitItemFilterBox": JitItemFilterBoxBuilder(product_repository, loggers),
            u"HideOptionBox": HideOptionBoxBuilder(product_repository, loggers),
            u"ComboDoneWhenAllDoneBox": ComboDoneWhenAllDoneBoxBuilder(loggers),
            u"ComboServedWhenAllServedBox": ComboServedWhenAllServedBoxBuilder(loggers),
            u"AllDoneBlinkBox": AllDoneBlinkBoxBuilder(loggers),
            u"OrderSequencerBox": OrderSequencerBoxBuilder(product_repository, loggers),
            u"RemoveDoingWhenDoneBox": RemoveDoingWhenDoneBoxBuilder(loggers),
            u"OrderStateTimerBox": OrderStateTimerBoxBuilder(loggers),
            u"FromOrderStateFilterBox": FromOrderStateFilterBoxBuilder(product_repository, loggers),
            u"CustomParamCourseBox": CustomParamCourseBoxBuilder(product_repository, publish_scheduler, loggers),
            u"CFHHiderBox": CFHHiderBoxBuilder(product_repository, loggers),
            u"ComboFilterBox": ComboFilterBoxBuilder(loggers),
            u"DistributorBox": DistributorBoxBuilder(loggers),
            u"CustomParamPrepTimeBox": CustomParamPrepTimeBoxBuilder(product_repository, publish_scheduler, loggers),
            u"ShowOnKitchenFilterBox": ShowOnKitchenFilterBoxBuilder(product_repository, loggers),
            u"NoJitAddTagBox": NoJitAddTagBoxBuilder(product_repository, loggers),
            u"ItemPropertiesFilterBox": ItemPropertiesFilterBoxBuilder(loggers),
            u"AllServedItemsBox": AllServedItemsBoxBuilder(loggers),
            u"SendMomentTimerBox": SendMomentTimerBuilder(loggers),
            u"ConditionBox": ConditionBoxBuilder(loggers),
            u"CustomPropertyFilterBox": CustomPropertyFilterBoxBuilder(loggers),
            u"CustomParamPointerBox": CustomParamPointerBoxBuilder(product_repository, loggers),
            u"OrderRoundRobinBox": OrderRoundRobinBoxBuilder(order_changer, loggers),
            u"RemoveDeletedItemsBox": RemoveDeletedItemsBoxBuilder(loggers),
            u"FilterDeletedItemsBeforeFirstStateBox": FilterDeletedItemsBeforeFirstStateBoxBuilder(loggers),
            u"OrderSpreaderBox": OrderSpreaderBoxBuilder(loggers),
            u"OrderStampBox": OrderStampBoxBuilder(loggers),
            u"OrderMergerBox": OrderMergerBoxBuilder(loggers),
            u"RecalledOrderStampBox": RecalledOrderStampBoxBuilder(loggers),
            u"FilterOrderIfNotAllItemsHaveTagBox": FilterOrderIfNotAllItemsHaveTagBoxBuilder(loggers),
            u"AllItemsDoneBox": AllItemsDoneBoxBuilder(loggers),
            u"RemoveReprocessedOrdersBox": RemoveReprocessedOrdersBoxBuilder(loggers),
            u"ProductCodeFilterBox": ProductCodeFilterBoxBuilder(loggers),
            u"OrderProductCategoryFilterBox": OrderProductCategoryFilterBoxBuilder(loggers),
            u"PodTypeFilterBox": PodTypeFilterBoxBuilder(loggers),
            u"SaleTypeFilterBox": SaleTypeFilterBoxBuilder(loggers),
            u"SkipCourseBox": SkipCourseBoxBuilder(loggers),
            u"CollapseSameItemsBox": CollapseSameItemsBoxBuilder(loggers),
            u"ItemSequencerBox": ItemSequencerBoxBuilder(order_changer, loggers),
            u"StatisticBox": StatisticBoxBuilder(statistic_updater, loggers),
            u"AddTimeTagBox": AddTimeTagBoxBuilder(loggers),
            u"ProdStateFilterBox": ProdStateFilterBoxBuilder(product_repository, loggers),
            u"CustomPropertyValueFilterBox": CustomPropertyValueFilterBoxBuilder(loggers),
            u"ItemSorterBox": ItemSorterBoxBuilder(product_repository, loggers),
            u"SorterBox": SorterBoxBuilder(product_repository, loggers),
            u"DisplayTimeFilterBox": DisplayTimeFilterBoxBuilder(loggers),
            u"ProdStateTimerBox": ProdStateTimerBoxBuilder(loggers),
            u"DecreaseTimeTagBox": DecreaseTimeTagBoxBuilder(loggers),
            u"AllItemHasAtLeastOneTagFilterBox": AllItemHasAtLeastOneTagFilterBoxBuilder(loggers),
            u"FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox": FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBoxBuilder(loggers),
            u"ComboTaggedWhenAllHasTagBox": ComboTaggedWhenAllHasTagBoxBuilder(loggers),
            u"TagItemsWhenProdStateBox": TagItemsWhenProdStateBoxBuilder(loggers),
            u"FilterOrderIfAllItemsHaveTagBox": FilterOrderIfAllItemsHaveTagBoxBuilder(loggers),
            u"FilterDefaultQuantityIngredientsBox": FilterDefaultQuantityIngredientsBoxBuilder(loggers),
            u"JitAddTagBox": JitAddTagBoxBuilder(product_repository, loggers),
            u"ReprocessOrdersBox": ReprocessOrdersBoxBuilder(publish_scheduler, loggers)
        }

    def set_views(self, views):
        # type: (Dict[str, ProductionView]) -> None
        self.builders[u"ViewBox"] = ViewBoxBuilder(self.command_processor, self.order_changer, views, self.loggers)
        self.builders[u"StampItemsView"] = StampItemsViewBoxBuilder(self.order_changer, views, self.loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ProductionBox
        if config.type not in self.builders:
            raise Exception("Builder not found for box: {} - {}".format(config.name, config.type))

        return self.builders[config.type].build(config)
