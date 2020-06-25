import base64
import logging
import time
from datetime import datetime
from threading import Thread
from xml.etree import cElementTree as eTree

import msgbus
import persistence
from persistence import Driver
from typing import List

logger = logging.getLogger("FiscalWrapper")


class FiscalDataRepository:
    def __init__(self, mbcontext):
        # type: (msgbus.MBEasyContext) -> FiscalDataRepository
        self.mbcontext = mbcontext
        self.conn = None  # type: persistence.Connection

    def __enter__(self):
        self.conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def get_tenders(self, orderid):
        # type: (str) -> List
        params_fiscal = {
            "order_id": orderid
        }
        tenders = [Tender(int(x.get_entry(0)), int(x.get_entry(1)), float(x.get_entry(2)), float(x.get_entry(3)), x.get_entry(4), x.get_entry(5), x.get_entry(6), x.get_entry(7), x.get_entry(8))
                   for x in self.conn.pselect("fiscal_getTenders", **params_fiscal)]
        return tenders

    def start_save_fiscal_data_thread(self, posid, order, xml_request, numero_sat, sent_to_nfce, xml_response):
        save_fiscal_data_thread = Thread(target=self.save_fiscal_data(posid, order, xml_request, numero_sat, sent_to_nfce, xml_response))
        save_fiscal_data_thread.daemon = True
        save_fiscal_data_thread.start()

    def save_fiscal_data(self, posid, order, xml_request, numero_sat, sent_to_nfce, xml_response):
        retrys = 0
        while retrys < 3:
            try:
                xml = base64.b64decode(xml_request)
                parsed_xml = eTree.XML(xml)

                from nfce import NfceRequestBuilder
                numero_nota_element = parsed_xml.find("infCFe/ide/nCFe")
                if numero_nota_element is None:
                    # TODO: Obter o numero da nota via parametro e remover esta logica daqui
                    numero_nota_element = parsed_xml.find(
                        "{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}nNF".format(
                            NfceRequestBuilder.NAMESPACE_NFE))
                    if numero_nota_element is None:
                        numero_nota_element = parsed_xml.find(
                            "{{{0}}}infNFe/{{{0}}}ide/{{{0}}}nNF".format(
                                NfceRequestBuilder.NAMESPACE_NFE))

                numero_nota = numero_nota_element.text

                data_nota_element = parsed_xml.find("infCFe/ide/dEmi")
                hora_nota_element = parsed_xml.find("infCFe/ide/hEmi")
                if data_nota_element is None:
                    dh_elment = parsed_xml.find(
                        "{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}dhEmi".format(
                            NfceRequestBuilder.NAMESPACE_NFE))
                    if dh_elment is None:
                        dh_elment = parsed_xml.find(
                            "{{{0}}}infNFe/{{{0}}}ide/{{{0}}}dhEmi".format(
                                NfceRequestBuilder.NAMESPACE_NFE))

                    data_nota_str = dh_elment.text

                    data_emissao_date_utc = data_nota_str[:19]
                    data_nota_date = datetime.strptime(data_emissao_date_utc, "%Y-%m-%dT%H:%M:%S")
                else:
                    data_nota_str = data_nota_element.text
                    hora_nota_str = hora_nota_element.text
                    data_nota_date = datetime.strptime(data_nota_str + hora_nota_str, "%Y%m%d%H%M%S")

                data_nota_seconds = int(time.mktime(data_nota_date.timetuple()))

                params_fiscal = {
                    "pos_id": posid,
                    "order_id": order.get("orderId"),
                    "data_nota": data_nota_seconds,
                    "numero_nota": numero_nota,
                    "numero_sat": numero_sat,
                    "xml_request": xml_request,
                    "sent_to_nfce": sent_to_nfce,
                    "xml_response": xml_response
                }

                self.conn.pquery("fiscal_saveFiscalData", **params_fiscal)
                break
            except Exception as _:
                logger.exception("Error saving fiscal data on database. RetryNum: {}".format(retrys))
                retrys += 1
        else:
            logger.error(">>> Save fiscal data failed after maximum retrys!")

    def set_order_picture(self, order_id, order_picture):
        # type: (str, str) -> None
        params = {
            "order_id": order_id,
            "order_picture": order_picture
        }
        self.conn.pquery("fiscal_setOrderPicture", **params)

    def set_order_canceled(self, order_id):
        # type: (str) -> None
        params = {
            "order_id": order_id,
        }
        self.conn.pquery("fiscal_setOrderCanceled", **params)

    def get_nfce_orders_to_send(self, limit):
        # type: (int) -> List
        params_fiscal = {
            "limit": limit
        }
        orders = [Order(x.get_entry(0), x.get_entry(1), x.get_entry(2), x.get_entry(3), x.get_entry(4)) for
                  x in self.conn.pselect("fiscal_getNfceToSend", **params_fiscal)]
        return orders

    def get_count_nfce_orders_to_send(self):
        # type: () -> int
        return [int(x.get_entry(0)) for x in self.conn.pselect("fiscal_getNfceToSendCount")][0]

    def set_nfce_sent(self, order_id, status):
        # type: (str, int) -> None
        params_fiscal = {
            "status": status,
            "order_id": order_id
        }
        self.conn.pquery("fiscal_setNfceSent", **params_fiscal)

    def set_nfce_sent_with_xml(self, order_id, xml_base64, status):
        # type: (str, str, int) -> None
        params_fiscal = {
            "status": status,
            "xml_request": xml_base64,
            "order_id": order_id
        }
        self.conn.pquery("fiscal_setNfceSentXml", **params_fiscal)

    def set_nfce_sent_with_xml_bkoffice(self, order_id, xml_base64, status, bkoffice_status):
        # type: (str, str, int) -> None
        params_fiscal = {
            "status": status,
            "xml_request": xml_base64,
            "order_id": order_id,
            "sent_to_bkoffice": bkoffice_status
        }
        self.conn.pquery("fiscal_setNfceSentXmlBKOffice", **params_fiscal)

    def retry_fiscal_orders_with_exception(self, range_of_days):
        # type: (str) -> None
        params_fiscal = {
            "range_of_days": "-{} days".format(range_of_days),
        }
        self.conn.pquery("fiscal_retryFiscalOrdersWithException", **params_fiscal)

    def get_xml_request(self, order_id):
        # type: (str, str, str, int) -> str
        params_fiscal = {
            "order_id": order_id
        }
        cursor = self.conn.pselect("fiscal_getRequestXMLFiscalData", **params_fiscal)
        if cursor.rows() > 0:
            ret = [x.get_entry(0) for x in cursor][0]
            return ret
        return

    def get_xml_response(self, order_id):
        # type: (str, str, str, int) -> str
        params_fiscal = {
            "order_id": order_id
        }
        cursor = self.conn.pselect("fiscal_getResponseXMLFiscalData", **params_fiscal)
        if cursor.rows() > 0:
            ret = [x.get_entry(0) for x in cursor][0]
            return ret
        return

    def get_numero_sat_and_xml_request(self, order_id):
        # type: (str, str, str, int) -> str
        params_fiscal = {
            "order_id": order_id
        }
        cursor = self.conn.pselect("fiscal_getSatNumberAndRequestXMLFiscalData", **params_fiscal)
        if cursor.rows() > 0:
            ret = [(x.get_entry(0), x.get_entry(1)) for x in cursor][0]
            return ret
        return


class Order:
    def __init__(self, order_id, pos_id, xml, num_nota, order_picture):
        self.order_id = order_id
        self.pos_id = pos_id
        self.xml = xml
        self.num_nota = num_nota
        self.order_picture = order_picture


class Tender:
    def __init__(self, tender_seq_id="", tender_type="", amount="", change="", bandeira="", auth_code="", cnpj_auth="", receipt_customer="", receipt_merchant=""):
        # type: (int, int, float, float, str, str, str, str) -> Tender
        self.tender_seq_id = tender_seq_id
        self.type = tender_type
        self.amount = amount
        self.change = change
        self.bandeira = bandeira
        self.auth_code = auth_code
        self.cnpj_auth = cnpj_auth
        self.receipt_customer = receipt_customer
        self.receipt_merchant = receipt_merchant
