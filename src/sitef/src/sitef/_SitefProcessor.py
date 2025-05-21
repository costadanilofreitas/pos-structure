# -*- coding: utf-8 -*-


class SitefProcessor(object):
    RESPONSE_XML = """<EftXml Media='%s' Result='%s' CardNumber='%sXXXXXXXXXX' AuthCode='%s' ApprovedAmount='%s' IdAuth='%s' CNPJAuth='%s' Bandeira='%s' ReceiptMerchant='%s' ReceiptCustomer='%s' ExpirationDate='%s' NSU='%s' TransactionProcessor='%s' LastDigits='%s'/>"""

    def __init__(self):
        pass

    def process(self, bus_msg, pos_id, order_id, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api, ip_sitef):
        raise NotImplementedError()

    def finalizar(self, posid, orderid, data_fiscal, hora_fiscal, status):
        raise NotImplementedError()

    def cancel(self):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()
