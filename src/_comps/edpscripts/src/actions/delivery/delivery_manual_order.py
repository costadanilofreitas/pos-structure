import json
from xml.etree import cElementTree as eTree

def create_delivery_manual_order_json(pos_ot, xml_order):
    name = _get_custom_property(xml_order, "CUSTOMER_NAME")
    phone = _get_custom_property(xml_order, "CUSTOMER_PHONE")
    document = _get_custom_property(xml_order, "CUSTOMER_DOC")
    city = _get_custom_property(xml_order, "CITY")
    neighborhood = _get_custom_property(xml_order, "NEIGHBORHOOD")
    reference = _get_custom_property(xml_order, "ADDRESS_REFERENCE")
    complement = _get_custom_property(xml_order, "COMPLEMENT")
    zip_code = _get_custom_property(xml_order, "POSTAL_CODE")
    number = _get_custom_property(xml_order, "STREET_NUMBER")
    street = _get_custom_property(xml_order, "STREET_NAME")

    all_sale_lines = xml_order.findall("SaleLine")
    main_sale_lines = [x for x in all_sale_lines if x.get("level") == "0"]
    manual_delivery_order_json = {
        "items": _get_items(all_sale_lines, main_sale_lines),
        "custom_properties": [
            {
                "key": "contact_number",
                "value": phone
            }, {
                "key": "customer_doc",
                "value": document
            }, {
                "key": "customer_name",
                "value": name
            }, {
                "key": "customer_phone",
                "value": phone
            }
        ],
        "pickup": {
            "address": {
                "city": city,
                "neighborhood": neighborhood,
                "reference": reference,
                "complement": complement,
                "postalCode": zip_code,
                "formattedAddress": street + ", " + number if street and number else "",
                "streetNumber": number,
                "streetName": street
            }
        },
        "totalPrice": float(xml_order.get("totalGross", 0)),
        "partner": "Delivery",
        "shortReference": xml_order.get("orderId", "-"),
        "subTotal": float(xml_order.get("totalGross", 0)),
        "createAt": xml_order.get("createdAt", "") + "Z"
    }

    pos_ot.setOrderCustomProperty("MANUAL_DELIVERY_ORDER_JSON", json.dumps(manual_delivery_order_json))


def _get_custom_property(xml_order, custom_property):
    value = ""
    current_property = xml_order.find("CustomOrderProperties/OrderProperty[@key='{}']".format(custom_property))
    if current_property is not None:
        value = current_property.get("value", "")
        
    return value


def _get_items(all_sale_lines, sale_lines, level=0):
    items = []
    for sale_line in sale_lines:
        quantity = int(sale_line.get("qty", 0))
        if quantity == 0:
            continue

        line_number = sale_line.get("lineNumber")
        price = float(sale_line.get("itemPrice", 0)) / quantity
        child_sale_lines = [x for x in all_sale_lines if
                            x.get("lineNumber") == line_number and
                            x.get("level") == str(level + 1) and
                            x.get("itemId") == (sale_line.get("itemId") + "." + sale_line.get("partCode"))]
        items.append(
                {
                    "price": price,
                    "parts": _get_items(all_sale_lines, child_sale_lines, level + 1),
                    "partCode": sale_line.get("partCode", ""),
                    "observation": "",
                    "quantity": quantity if sale_line.get("itemType", "") != "OPTION" else 1,
                    "itemType": sale_line.get("itemType", "")
                }
        )
        
    return items
