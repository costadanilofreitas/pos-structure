# -*- coding: utf-8 -*-

import base64
import logging

from sitef import SitefProcessor

logger = logging.getLogger("Sitef")


class FakeSitefProcessor(SitefProcessor):
    def __init__(self):
        super(FakeSitefProcessor, self).__init__()
        self.sitef_service_finder = FakeSitefServiceFinder()

    def process(self, bus_msg, pos_id, order_id, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api=False, ip_sitef=None):
        nome_instituicao = 'VISA'
        ret = '0'
        bin_cartao = '4111XXXXXXXXXXXX'
        auth_code = '1302'
        rede_autorizadora = '08496898000142'
        bandeira = '4'
        b64_receipt_customer = base64.b64encode("Recibo de teste.\nSitef FAKE")
        b64_receipt_merchant = base64.b64encode("Recibo de teste.\nSitef FAKE")
        expiration_date = '05/2020'
        nsu = '1234'
        transaction_processor = "00051"
        cnpj_authorizer = "68536379000192"
        last_digits = "1111"

        response = SitefProcessor.RESPONSE_XML % (nome_instituicao, ret, bin_cartao, auth_code, amount, rede_autorizadora, cnpj_authorizer, bandeira, b64_receipt_merchant, b64_receipt_customer, expiration_date, nsu, transaction_processor, last_digits)
        return True, response

    def finalizar(self, posid, orderid, data_fiscal, hora_fiscal, status):
        return None

    def cancel(self):
        raise Exception()

    def terminate(self):
        pass


class FakeSitefServiceFinder(object):
    def __init__(self):
        pass

    def lock_sitef(self):
        pass

    def release_sitef(self):
        pass
