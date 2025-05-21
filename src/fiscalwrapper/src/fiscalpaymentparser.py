import base64
import json
from xml.etree import cElementTree as eTree

from pos_model import TenderType
from typing import List

from fiscalpersistence import Tender


def convert_order_tenders_to_fiscal_tenders(order_picture):
    # type: (eTree) -> List[Tender]

    fiscal_tenders = []  # type: List[Tender]

    order_tenders = order_picture.findall('TenderHistory/Tender')

    for order_tender in order_tenders:
        fiscal_tender = Tender()
        fiscal_tender.tender_seq_id = order_tender.attrib["tenderId"]
        fiscal_tender.type = int(order_tender.attrib["tenderType"])
        fiscal_tender.amount = float(order_tender.attrib["tenderAmount"])
        fiscal_tender.change = float(order_tender.attrib['change']) if 'change' in order_tender.attrib else 0

        tender_details = order_tender.attrib['tenderDetail'] if 'tenderDetail' in order_tender.attrib else None
        if tender_details is not None:
            tender_details = json.loads(tender_details)

        if fiscal_tender.type in (TenderType.credit, TenderType.debit) and tender_details:
            fiscal_tender.auth_code = tender_details['AuthCode'] if 'AuthCode' in tender_details else ""
            fiscal_tender.bandeira = tender_details['Bandeira'] if 'Bandeira' in tender_details else ""
            fiscal_tender.cnpj_auth = tender_details['CNPJAuth'] if 'CNPJAuth' in tender_details else ""

            receipt_customer = tender_details['ReceiptCustomer'] if 'ReceiptCustomer' in tender_details else ""
            receipt_merchant = tender_details['ReceiptMerchant'] if 'ReceiptMerchant' in tender_details else ""
            if receipt_customer != "":
                receipt_customer = base64.b64decode(receipt_customer)
            if receipt_merchant != "":
                receipt_merchant = base64.b64decode(receipt_merchant)

            fiscal_tender.receipt_customer = receipt_customer
            fiscal_tender.receipt_merchant = receipt_merchant

        fiscal_tenders.append(fiscal_tender)

    return fiscal_tenders
