# -*- coding: utf-8 -*-

import base64
import json
from xml.etree import ElementTree as eTree
import sysactions
from fiscalpersistence import Tender
from msgbus import MBEasyContext
from typing import Dict, List, Optional

from _AposA8PrintLine import AposA8PrintLine
from _AposA8Align import AposA8Align
from _AposA8CommandType import AposA8CommandType
from _AposA8Constants import AposA8Constants

from printer import FiscalPrinter, get_payment_description
from printer_wrapper import insert_space
from old_helper import F, get_sale_line_priced_items
from clichehelper import ClicheHelper


class SatAposA8FiscalPrinter(FiscalPrinter):
    def __init__(self, mb_context, print_customer_name, cliche_helper, customer_text_field, tip_config):
        # type: (MBEasyContext, bool, ClicheHelper, str, Dict[str]) -> None
        super(SatAposA8FiscalPrinter, self).__init__(mb_context, print_customer_name, cliche_helper)
        self.customer_text_field = customer_text_field
        self.tip_config = tip_config

    def print_fiscal(self, posid, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        # type: (str, eTree.Element, list, eTree.Element, eTree.Element, dict, str, str) -> str
        xml = base64.b64decode(fiscal_request.text.strip())
        parsed_xml = eTree.XML(xml)
        n_c_fe = parsed_xml.find("infCFe/ide/nCFe").text
        model = sysactions.get_model(posid)

        report = self._fiscal_report(order, tenders, fiscal_response, total_taxes, n_c_fe, customer_name, model)

        qr_code = fiscal_response.find("QRCode").text.strip()

        report.append(AposA8PrintLine(AposA8Align.CENTER, fiscal_response.find("satkey").text.strip(),
                                      AposA8CommandType.PRINT_BAR_CODE))
        report.append(AposA8PrintLine(AposA8Align.CENTER, '', AposA8CommandType.PRINT_BAR_CODE))
        report.append(AposA8PrintLine(AposA8Align.CENTER, qr_code, AposA8CommandType.PRINT_QR_CODE))
        return json.dumps(report, default=lambda x: x.__dict__)

    def print_cancel(self, posid, data):
        return

    def _cancel_report(self, sat_fiscal_response, nCFe, total):
        return

    def _fiscal_report(self, order, tenders, sat_fiscal_response, total_taxes, nCFe, customer_name, model=None):
        # type: (eTree, List[Tender], eTree, dict, str, str, Optional[eTree]) -> List[AposA8PrintLine]

        whopper_wifi_code = order.find("CustomOrderProperties/OrderProperty[@key='WHOPPER_WIFI_CODE']").get(
            "value") if order.find(
            "CustomOrderProperties/OrderProperty[@key='WHOPPER_WIFI_CODE']") is not None else None
        if whopper_wifi_code is not None:
            whopper_wifi_code = whopper_wifi_code[0:4] + " " + whopper_wifi_code[4:8]

        report = []

        for line in self.cliche_helper.get_cliche():
            report.append(AposA8PrintLine(AposA8Align.CENTER, line, AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER, "EXTRATO No. %s" % nCFe, AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER, "CUPOM FISCAL ELETRONICO - SAT", AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))

        cpf_cnpj = sat_fiscal_response.find("CustomerCPF").text
        cpf_text = "CPF/CNPJ do Consumidor: %s" % ("Nao informado" if not cpf_cnpj else cpf_cnpj)
        report.append(AposA8PrintLine(AposA8Align.CENTER, cpf_text, AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))

        product_header = "COD     DESCR          QTD UN    VL UNIT   TOTAL"
        report.append(AposA8PrintLine(AposA8Align.CENTER, product_header, AposA8CommandType.PRINT_TEXT))

        order_voided = order.get("state") == "VOIDED"
        items_amount = 0

        sale_lines = order.findall("SaleLine")
        sale_lines = get_sale_line_priced_items(sale_lines)

        for line in sale_lines:
            item_price, unit_price, item_qty, name, part_code = map(line.get,
                                                                    ("correctItemPrice",
                                                                     "correctUnitPrice",
                                                                     "correctQty",
                                                                     "productName",
                                                                     "partCode"))
            un = "un"
            items_amount += 1
            line = "%-7.7s %-14.14s%5.3f%2.2s%9.02f" % (part_code, name, F(item_qty), un, F(unit_price))
            string = ("%-38.38s %9.02f" % (line, F(item_price)))

            report.append(AposA8PrintLine(AposA8Align.CENTER, string, AposA8CommandType.PRINT_TEXT))

        if order.get("tip", 0) and float(order.get("tip")) > 0:
            order_tip = F(order.get("tip"))
            tip_line = "%-7.7s %-14.14s%5.3f%2.2s%9.02f" % (self.tip_config['TipCode'],
                                                            sysactions.translate_message(model, "TIP_GIVEN").upper(),
                                                            F(1),
                                                            "un",
                                                            order_tip)
            tip_text = ("%-38.38s %9.02f" % (tip_line, order_tip))
            report.append(AposA8PrintLine(AposA8Align.CENTER, tip_text, AposA8CommandType.PRINT_TEXT))

        factor = -1 if order_voided else 1

        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))

        qty_total = "%-36s         %3d" % ("QTD. TOTAL DE ITENS", items_amount)
        report.append(AposA8PrintLine(AposA8Align.CENTER, qty_total, AposA8CommandType.PRINT_TEXT))

        total_amount = "%-36s   R$%7.2f" % ("VALOR TOTAL", float(order.get("totalAmount")) + float(order.get("taxTotal")))
        report.append(AposA8PrintLine(AposA8Align.CENTER, total_amount, AposA8CommandType.PRINT_TEXT))

        discount = "%-36s   R$%7.2f" % ("DESCONTO", float(order.get("discountAmount")))
        report.append(AposA8PrintLine(AposA8Align.CENTER, discount, AposA8CommandType.PRINT_TEXT))

        total_payable = "%-36s   R$%7.2f" % ("VALOR A PAGAR",
                                             float(order.get("totalAmount"))
                                             + float(order.get("taxTotal"))
                                             - float(order.get("discountAmount")))
        report.append(AposA8PrintLine(AposA8Align.CENTER, total_payable, AposA8CommandType.PRINT_TEXT))

        payment = "%-36s  %s" % ("FORMA DE PAGAMENTO", "Valor Pago")
        report.append(AposA8PrintLine(AposA8Align.CENTER, payment, AposA8CommandType.PRINT_TEXT))

        for tender in tenders:
            tender_descr = get_payment_description(self.mb_context, tender)
            tender_amount = tender.amount
            report.append(AposA8PrintLine(AposA8Align.CENTER, "%-36s   R$%7.2f" % (tender_descr, tender_amount),
                                          AposA8CommandType.PRINT_TEXT))

        # Get "Change" (sixth value of tender tuple) from last tender in tenders
        change = tenders[len(tenders) - 1].change

        if change > 0:
            report.append(AposA8PrintLine(AposA8Align.CENTER, "%-36s   R$%7.2f" % ("Troco", change * factor),
                                          AposA8CommandType.PRINT_TEXT))

        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))
        if self.print_customer_name:
            char_amount = 21

            content = (customer_name or '')[:(char_amount - 2)] or order.get('orderId')[-3:]
            report.append(AposA8PrintLine(AposA8Align.CENTER, "PAINEL DE RETIRADA - VOCE SERA CHAMADO POR:",
                                          AposA8CommandType.PRINT_TEXT))

            report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_HASH,
                                          AposA8CommandType.PRINT_TEXT))
            report.append(AposA8PrintLine(AposA8Align.CENTER, content.upper(), AposA8CommandType.PRINT_TEXT))
            report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_HASH,
                                          AposA8CommandType.PRINT_TEXT))

        if whopper_wifi_code is not None and model is not None:
            report.append(AposA8PrintLine(AposA8Align.CENTER,
                                          sysactions.translate_message(model, "WIFI_PRINTER_MESSAGE"),
                                          AposA8CommandType.PRINT_TEXT))
            report.append(AposA8PrintLine(AposA8Align.CENTER,
                                          sysactions.translate_message(model,
                                                                       "WIFI_ACCESS_CODE",
                                                                       "%s" % whopper_wifi_code),
                                          AposA8CommandType.PRINT_TEXT))

        tax_text = "%-36s %7.2f" % ("Valor aproximado dos tributos deste cupom", (float(total_taxes['nacionalfederal']['value']) + float(total_taxes['estadual']['value'])))
        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      tax_text,
                                      AposA8CommandType.PRINT_TEXT))
        tax_value = "%7.2f" % (float(total_taxes['nacionalfederal']['value']) + float(total_taxes['estadual']['value']))
        report.append(AposA8PrintLine(AposA8Align.RIGHT,
                                      tax_value,
                                      AposA8CommandType.PRINT_TEXT))
        federal_tax = "Fed = R$%7.2f (%.2f%%), Est = R$%7.2f (%.2f%%)" % (
        total_taxes['nacionalfederal']['value'], total_taxes['nacionalfederal']['percent'],
        total_taxes['estadual']['value'], total_taxes['estadual']['percent'])
        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      federal_tax,
                                      AposA8CommandType.PRINT_TEXT))
        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      "(Conforme Lei Fed. 12.741/2012)",
                                      AposA8CommandType.PRINT_TEXT))

        report.append(AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))

        # Campo de texto customizado exibido na área de informações adicionais
        if self.customer_text_field != "":
            for customer_text in self.customer_text_field.split('\\n'):
                report.append(AposA8PrintLine(AposA8Align.CENTER,
                                              customer_text.replace("\\n", ""),
                                              AposA8CommandType.PRINT_TEXT))
            report.append(
                AposA8PrintLine(AposA8Align.CENTER, AposA8Constants.SEPARATOR_DASH, AposA8CommandType.PRINT_TEXT))

        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      "SAT No. %s" % sat_fiscal_response.find("satno").text.strip(),
                                      AposA8CommandType.PRINT_TEXT))

        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      sat_fiscal_response.find("datetime").text.strip(),
                                      AposA8CommandType.PRINT_TEXT))

        satk = insert_space(sat_fiscal_response.find("satkey").text.strip(), 4)
        report.append(AposA8PrintLine(AposA8Align.CENTER,
                                      str(satk),
                                      AposA8CommandType.PRINT_TEXT))

        return report
