from salecomp.model import State, OrderType
from salecomp.repository import OrderRepository
from xml.etree import cElementTree as eTree
from pytz import timezone
from tzlocal import get_localzone


class OrderPictureInteractor(object):
    def __init__(self, order_repository):
        # type: (OrderRepository) -> None
        self.order_repository = order_repository

    def execute(self, order_id):
        order = self.order_repository.get_order(None, order_id)
        return self.convert_order_to_xml(order)

    def convert_order_to_xml(self, order):
        order_xml = eTree.Element("Order")
        order_xml.set("orderId", str(order.id))
        order_xml.set("stateId", str(order.state.value))
        order_xml.set("state", self.get_state_description(order.state))
        order_xml.set("typeId", str(order.type.value))
        order_xml.set("type", self.get_type_description(order.type))
        order_xml.set("originatorId", "POS{:02d}".format(order.originator_id))
        order_xml.set("createdAt", order.created_at.astimezone(get_localzone()).strftime("%Y-%m-%dT%H:%M:%S"))
        order_xml.set("createdAtGMT", order.created_at.strftime("%Y-%m-%dT%H:%M:%S"))
        order_xml.set("businessPeriod", order.business_period.strftime("%Y%m%d"))
        order_xml.set("podType", order.pod_type)
        order_xml.set("sessionId", order.session_id)
        order_xml.set("priceList", ",".join(order.price_lists))
        order_xml.set("priceBasis", order.price_basis)
        order_xml.set("saleType", str(order.sale_type.id))
        order_xml.set("saleTypeDescr", order.sale_type.name)
        return eTree.tostring(order_xml)

    def get_state_description(self, state):
        # type: (State) -> str
        state_map = {
            state.in_progress: "IN_PROGRESS",
            state.abandoned: "ABANDONED",
            state.paid: "PAID",
            state.recalled: "RECALLED",
            state.stored: "STORED",
            state.system_voided: "SYSTEM_VOIDED",
            state.totaled: "TOTALED",
            state.undefined: "UNDEFINED",
            state.voided: "VOIDED"
        }

        return state_map[state]

    def get_type_description(self, order_type):
        # type: (OrderType) -> str
        order_type_map = {
            OrderType.sale: "SALE"
        }

        return order_type_map[order_type]
