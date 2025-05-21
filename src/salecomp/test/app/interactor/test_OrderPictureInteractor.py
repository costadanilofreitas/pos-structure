from datetime import datetime, date
from pytz import timezone

from salecomp.interactor import OrderPictureInteractor
from xml.etree import cElementTree as eTree

from salecomp.model import Order, State, SaleType, OrderType
from testdouble import OrderRepositoryStub, OrderRepositorySpy


class TestOrderPictureInteractor(object):
    def test_orderRepositoryIsCalledWithTheCorrectAttributes(self):
        order_repository = OrderRepositorySpy(get_order_response=an_order())
        interactor = OrderPictureInteractor(order_repository)
        interactor.execute(123)
        assert order_repository.get_order_call.args[0] is None
        assert order_repository.get_order_call.args[1] == 123

    def test_orderAttributesAreCorreclyMapped(self):
        order_repository = OrderRepositoryStub(get_order_response=an_order())
        interactor = OrderPictureInteractor(order_repository)
        order_xml_str = interactor.execute(123)
        order_xml = eTree.XML(order_xml_str)
        assert order_xml.get("orderId") == "123"
        assert order_xml.get("stateId") == "1"
        assert order_xml.get("state") == "IN_PROGRESS"
        assert order_xml.get("typeId") == "0"
        assert order_xml.get("typeId") == "0"
        assert order_xml.get("type") == "SALE"
        assert order_xml.get("originatorId") == "POS04"
        assert order_xml.get("createdAt") == "2019-10-12T10:25:49"
        assert order_xml.get("createdAtGMT") == "2019-10-12T13:25:49"
        assert order_xml.get("businessPeriod") == "20191012"
        assert order_xml.get("podType") == "TS"
        assert order_xml.get("sessionId") == "session_id"
        assert order_xml.get("priceList") == "EI,DL"
        assert order_xml.get("priceBasis") == "PB"
        assert order_xml.get("saleType") == "0"
        assert order_xml.get("saleTypeDescr") == "EAT_IN"


def an_order():
    return Order(id=123,
                 state=State.in_progress,
                 type=OrderType.sale,
                 originator_id=4,
                 created_at=datetime(2019, 10, 12, 13, 25, 49, 125, tzinfo=timezone('UTC')),
                 business_period=date(2019, 10, 12),
                 pod_type="TS",
                 session_id="session_id",
                 price_lists=["EI", "DL"],
                 price_basis="PB",
                 sale_type=SaleType(0, "EAT_IN"),
                 lines=[])
