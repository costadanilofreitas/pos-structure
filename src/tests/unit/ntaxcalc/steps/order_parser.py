from typing import List
from behave import *
from robber import expect
from taxcalculator import OrderParser
from taxcalculator.model import SaleItem, Order


@when("the parse_order is called with an order with just one product with quantity = 1")
def step_impl(context):
    context.order_xml = u"""
<Order orderId="10" sessionId="pos=1,user=1,count=1,period=20171121">
    <SaleLine lineNumber="1" level="0" itemId="1" partCode="6012" productName="MD Batata" lastOrderedQty="1" multipliedQty="1" qty="1" incQty="0" decQty="0" itemPrice="6.50" unitPrice="6.50" addedUnitPrice="0.00" itemType="PRODUCT" priceKey="200072" productPriority="100" measureUnit="UN"/>
</Order>"""


@when("the parse_order is called with an order with just one product with quantity = 3")
def step_impl(context):
    context.order_xml = u"""
    <Order orderId="10" sessionId="pos=1,user=1,count=1,period=20171121">
        <SaleLine lineNumber="1" level="0" itemId="1" partCode="6012" productName="MD Batata" lastOrderedQty="1" multipliedQty="3" qty="3" incQty="0" decQty="0" itemPrice="19.50" unitPrice="6.50" addedUnitPrice="0.00" itemType="PRODUCT" priceKey="200072" productPriority="100" measureUnit="UN"/>
    </Order>"""


@when("the parse_order is called with an order with a combo and a canadd")
def step_impl(context):
    context.order_xml = u"""
        <Order orderId="10" sessionId="pos=1,user=1,count=1,period=20171121">
            <SaleLine lineNumber="1" level="0" itemId="1" partCode="1051" productName="CM Whopper/Q" lastOrderedQty="1" multipliedQty="3" qty="3" incQty="2" decQty="0" itemType="COMBO" productPriority="100" measureUnit="UN"/>
                <SaleLine lineNumber="1" level="1" itemId="1.1051" partCode="7300000" productName="*** FRITOS ***" multipliedQty="3" qty="1" incQty="1" decQty="0" defaultQty="1" addedQty="0" subQty="0" itemType="OPTION" chosenQty="1" productPriority="100" measureUnit="UN"/>
                    <SaleLine lineNumber="1" level="2" itemId="1.1051.7300000" partCode="6012" productName="MD Batata" multipliedQty="3" qty="1" incQty="1" decQty="0" itemPrice="3.00" unitPrice="3.00" addedUnitPrice="0.00" itemType="CANADD" priceKey="200073" productPriority="100" measureUnit="UN"/>
        </Order>"""


@when("the parse_order is called with an order with a combo and a canadd with discount")
def step_impl(context):
    context.order_xml = u"""
            <Order orderId="10" sessionId="pos=1,user=1,count=1,period=20171121">
                <SaleLine lineNumber="1" level="0" itemId="1" partCode="1051" productName="CM Whopper/Q" lastOrderedQty="1" multipliedQty="3" qty="3" incQty="2" decQty="0" itemType="COMBO" productPriority="100" measureUnit="UN"/>
                    <SaleLine lineNumber="1" level="1" itemId="1.1051" partCode="7300000" productName="*** FRITOS ***" multipliedQty="3" qty="1" incQty="1" decQty="0" defaultQty="1" addedQty="0" subQty="0" itemType="OPTION" chosenQty="1" productPriority="100" measureUnit="UN"/>
                        <SaleLine lineNumber="1" level="2" itemId="1.1051.7300000" partCode="6012" productName="MD Batata" multipliedQty="3" qty="1" incQty="1" decQty="0" itemPrice="3.00" unitPrice="3.00" addedUnitPrice="0.00" itemType="CANADD" priceKey="200073" productPriority="100" measureUnit="UN" itemDiscount="0.9"/>
            </Order>"""

@when("the order has a combo with a product with ingredients")
def step_impl(context):
    context.order_xml = u"""
        <Order orderId="10" sessionId="pos=1,user=1,count=1,period=20171121">
            <SaleLine lineNumber="1" level="0" itemId="1" partCode="1051" productName="CM Whopper/Q" lastOrderedQty="1" multipliedQty="3" qty="3" incQty="2" decQty="0" itemType="COMBO" productPriority="100" measureUnit="UN"/>
            <SaleLine lineNumber="1" level="1" itemId="1.1051" partCode="10025000" productName="**BK MIX + 5**" multipliedQty="0" qty="0" incQty="0" decQty="0" defaultQty="0" addedQty="0" subQty="0" itemType="OPTION" productPriority="100" measureUnit="UN"/>
            <SaleLine lineNumber="1" level="1" itemId="1.1051" partCode="1050" productName="Whopper/Q" multipliedQty="3" qty="1" incQty="1" decQty="0" itemPrice="11.00" defaultQty="1" addedQty="0" subQty="0" unitPrice="11.00" addedUnitPrice="0.00" itemType="PRODUCT" priceKey="199789" productPriority="100" measureUnit="UN"/>
                <SaleLine lineNumber="1" level="2" itemId="1.1051.1050" partCode="8200000" productName="*** COND SANDW ***" multipliedQty="9" qty="3" incQty="0" decQty="0" defaultQty="0" addedQty="3" subQty="0" itemType="OPTION" chosenQty="3" productPriority="100" measureUnit="UN"/>
                    <SaleLine lineNumber="1" level="3" itemId="1.1051.1050.8200000" partCode="8700002" productName="Catchup" defaultQty="1" multipliedQty="0" qty="0" incQty="0" decQty="0" itemPrice="0.00" unitPrice="0.00" addedUnitPrice="1.00" itemType="CANADD" priceKey="201255" productPriority="100" measureUnit="UN"/>
                    <SaleLine lineNumber="1" level="3" itemId="1.1051.1050.8200000" partCode="8700012" productName="Alface " defaultQty="1" multipliedQty="6" qty="2" incQty="2" decQty="0" itemPrice="2.00" unitPrice="0.00" addedUnitPrice="1.00" itemType="CANADD" priceKey="201275" productPriority="100" measureUnit="UN"/>
                    <SaleLine lineNumber="1" level="3" itemId="1.1051.1050.8200000" partCode="8700020" productName="Bacon" defaultQty="0" multipliedQty="3" qty="1" incQty="1" decQty="0" itemPrice="1.00" unitPrice="0.00" addedUnitPrice="1.00" itemType="CANADD" priceKey="201291" productPriority="100" measureUnit="UN"/>
        </Order>"""


@when("the parse_order method is called")
def step_impl(context):
    order_parser = OrderParser()
    context.order = order_parser.parse_order(context.order_xml)


@then("a list with a single SaleItem is created")
def step_impl(context):
    sale_items = context.order.sale_items  # type: List[SaleItem]
    expect(sale_items).to.be.instanceof(list)
    expect(len(sale_items)).to.eq(1)
    _check_sale_item(sale_items[0],
                     line_number=1,
                     level=0,
                     item_id="1",
                     part_code=6012,
                     quantity=1,
                     unit_price=6.5,
                     item_price=6.5,
                     added_unit_price=0.0,
                     item_discount=0.0,
                     unit_discount=0.0)


@then("the correct orderId and posId are returned")
def step_impl(context):
    order = context.order  # type: Order
    expect(order.pos_id).to.eq(1)
    expect(order.order_id).to.eq(10)


@then("a list with a single multiplied SaleItem is created")
def step_impl(context):
    sale_items = context.order.sale_items  # type: List[SaleItem]
    expect(sale_items).to.be.instanceof(list)
    expect(len(sale_items)).to.eq(1)
    _check_sale_item(sale_items[0],
                     line_number=1,
                     level=0,
                     item_id="1",
                     part_code=6012,
                     quantity=3,
                     unit_price=6.5,
                     item_price=19.5,
                     added_unit_price=0.0,
                     item_discount=0.0,
                     unit_discount=0.0)


@then("a list with a all the SaleItems of the canadd are returned")
def step_impl(context):
    sale_items = context.order.sale_items  # type: List[SaleItem]
    expect(sale_items).to.be.instanceof(list)
    expect(len(sale_items)).to.eq(1)
    _check_sale_item(sale_items[0],
                     line_number=1,
                     level=2,
                     item_id="1.1051.7300000",
                     part_code=6012,
                     quantity=3,
                     unit_price=3.0,
                     item_price=9.0,
                     added_unit_price=0.0,
                     item_discount=0.0,
                     unit_discount=0.0)


@then("a list with a all the SaleItems of the product and ingredients are returned")
def step_impl(context):
    sale_items = context.order.sale_items  # type: List[SaleItem]
    expect(sale_items).to.be.instanceof(list)
    expect(len(sale_items)).to.eq(3)
    _check_sale_item(sale_items[0],
                     line_number=1,
                     level=1,
                     item_id="1.1051",
                     part_code=1050,
                     quantity=3,
                     unit_price=11.0,
                     item_price=33.0,
                     added_unit_price=0.0,
                     item_discount=0.0,
                     unit_discount=0.0)
    _check_sale_item(sale_items[1],
                     line_number=1,
                     level=3,
                     item_id="1.1051.1050.8200000",
                     part_code=8700012,
                     quantity=3,
                     unit_price=1.0,
                     item_price=3.0,
                     added_unit_price=1.0,
                     item_discount=0.0,
                     unit_discount=0.0)
    _check_sale_item(sale_items[2],
                     line_number=1,
                     level=3,
                     item_id="1.1051.1050.8200000",
                     part_code=8700020,
                     quantity=3,
                     unit_price=1.0,
                     item_price=3.0,
                     added_unit_price=1.0,
                     item_discount=0.0,
                     unit_discount=0.0)


@then("a list with a all the SaleItems of the canadd are returned with the correct discount")
def step_impl(context):
    sale_items = context.order.sale_items  # type: List[SaleItem]
    expect(sale_items).to.be.instanceof(list)
    expect(len(sale_items)).to.eq(1)
    _check_sale_item(sale_items[0],
                     line_number=1,
                     level=2,
                     item_id="1.1051.7300000",
                     part_code=6012,
                     quantity=3,
                     unit_price=3.0,
                     item_price=9.0,
                     added_unit_price=0.0,
                     item_discount=0.9,
                     unit_discount=0.3)

def _check_sale_item(sale_item, line_number, level, item_id, part_code, quantity, item_price, unit_price, added_unit_price, item_discount, unit_discount):
    # type: (SaleItem, int, int, unicode, int, int, float, float, float) -> None
    expect(sale_item.line_number).to.eq(line_number)
    expect(sale_item.level).to.eq(level)
    expect(sale_item.item_id).to.eq(item_id)
    expect(sale_item.part_code).to.eq(part_code)

    expect(sale_item.quantity).to.eq(quantity)
    expect(sale_item.item_price).to.eq(item_price)
    expect(sale_item.unit_price).to.eq(unit_price)
    expect(sale_item.added_unit_price).to.eq(added_unit_price)
    expect(sale_item.item_discount).to.eq(item_discount)
    expect(sale_item.unit_discount).to.eq(unit_discount)
