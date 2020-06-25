# -*- coding: utf-8 -*-
import json
from ast import literal_eval
import base64
import datetime
from unicodedata import normalize
from xml.etree import ElementTree as eTree

import constants
import printer_wrapper
import sysactions
from dateutil import tz
from old_helper import F, get_sale_line_priced_items, remove_xml_namespace
from clichehelper import ClicheHelper
from msgbus import FM_PARAM, TK_SYS_ACK, TK_SYS_NAK, TK_STORECFG_GET, TK_PRN_PRINT, MBException, MBEasyContext
from persistence import Driver as DBDriver
from sysactions import get_storewide_config
from bustoken import create_token
from comp_exceptions import VoidOrderException

TK_DECRYPT_GARENA_COUPON = create_token("F", "99", "2")


class FiscalPrinter(object):
    def __init__(self, mbcontext, print_customer_name, cliche_helper):
        # type: (MBEasyContext, bool, ClicheHelper) -> None
        self.mbcontext = mbcontext
        self.print_customer_name = print_customer_name
        self.print_merchant_receipt = None
        self.cliche_helper = cliche_helper
        sysactions.mbcontext = mbcontext

    def print_fiscal(self, posid, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        raise NotImplementedError()

    def print_cancel(self, posid, data):
        raise NotImplementedError()

    @staticmethod
    def _center(s, cols=constants.COLS):
        if not s:
            return s

        s = SatFiscalPrinter._cut(s)
        miss = cols - len(s)

        if miss == 0:
            return s

        left = miss / 2

        return (" " * left) + s

    @staticmethod
    def _cut(s):
        if len(s) > constants.COLS:
            # If there is a line-feed at the end, keep it
            return s[:constants.COLS] if (s[-1] != "\n") else (s[:(constants.COLS - 1)] + "\n")

        return s

    @staticmethod
    def get_payment_description(mbcontext, tender):
        # TODO: colocar cache
        conn_prod = DBDriver().open(mbcontext)
        tender_type = [str(element.get_entry(0)) for element in conn_prod.select("""SELECT TenderDescr FROM TenderType WHERE TenderId = %s """ % tender.type)][0]
        conn_prod.close()
        return tender_type

    def tef_receipts(self, tenders):
        totem_print = True
        report = unicode('', 'utf-8')
        if tenders:
            for tender in tenders:
                if tender.receipt_customer:
                    report += constants.TXT_ALIGN_CT
                    report += constants.SEPARATOR_DASH + "\n"

                    result = ""
                    for item in tender.receipt_customer.split('\n'):
                        result += "{}\n".format(item.split())

                    for item in ["[", "]", "'", "'"]:
                        result = result.replace(item, "")

                    report += result

                if self.get_print_merchant_receipt_flag() and tender.receipt_merchant:
                    report += constants.TXT_ALIGN_CT
                    report += "\n" + constants.SEPARATOR_DASH + "\n"

                    result = ""
                    for item in tender.receipt_merchant.split('\n'):
                        result += "{}\n".format(item.split())

                    for item in ["[", "]", "'", "'"]:
                        result = result.replace(item, "")

                    report += result

        return str(report)

    def get_print_merchant_receipt_flag(self):
        if self.print_merchant_receipt is None:
            self.print_merchant_receipt = get_storewide_config("Store.PrintMerchantReceipt", defval="False").lower() == "true"
        return self.print_merchant_receipt


class SatFiscalPrinter(FiscalPrinter):
    def __init__(self, mbcontext, print_customer_name, cliche_helper, customer_text_field, garena_configs):
        # type: (MBEasyContext, bool, ClicheHelper, str, dict) -> None
        super(SatFiscalPrinter, self).__init__(mbcontext, print_customer_name, cliche_helper)
        self.customer_text_field = customer_text_field
        self.satisfaction_survey_text = None
        self.garena_configs = garena_configs

    def print_fiscal(self, posid, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        # type: (str, eTree.Element, list, eTree.Element, eTree.Element, dict, str, str) -> None
        xml = base64.b64decode(fiscal_request.text.strip())
        parsed_xml = eTree.XML(xml)
        n_c_fe = parsed_xml.find("infCFe/ide/nCFe").text
        model = sysactions.get_model(posid)

        totem_print = sysactions.get_podtype(sysactions.get_model(posid)) == "TT"

        report = self._fiscal_report(order, tenders, fiscal_response, total_taxes, n_c_fe, customer_name, totem_print, model)

        barcode1, barcode2 = printer_wrapper.barcode(fiscal_response.find("satkey").text.strip())
        qr_code = printer_wrapper.qr(fiscal_response.find("QRCode").text.strip())

        report = report.encode("utf-8") + barcode1
        report += barcode2
        report += "\n"
        report += constants.TXT_ALIGN_CT
        report += qr_code
        report += constants.TXT_ALIGN_LT
        report += self.tef_receipts(tenders)
        return report

    def print_cancel(self, posid, data):
        # type: (str, str) -> None
        fiscal_response = eTree.XML(data)
        xml = base64.b64decode(fiscal_response.find("XmlRequest").text.strip())
        parsed_xml = eTree.XML(xml)
        n_c_fe = parsed_xml.find("infCFe/ide/nCFe").text
        total = parsed_xml.find("infCFe/total/vCFe").text
        report = self._cancel_report(fiscal_response.find("FiscalData"), n_c_fe, total)

        barcode1, barcode2 = printer_wrapper.barcode(fiscal_response.find("FiscalData/satkey").text.strip())
        qr_code = printer_wrapper.qr(fiscal_response.find("FiscalData/QRCode").text.strip())

        report = report.encode("utf-8") + barcode1
        report += barcode2
        report += "\n"
        report += qr_code
        report += constants.TXT_ALIGN_LT

        # 10 Seconds Timeout
        msg = self.mbcontext.MB_EasySendMessage("printer%s" % posid, TK_PRN_PRINT, format=FM_PARAM, data=report, timeout=10000000)  # type: MBMessage
        if msg.token != TK_SYS_ACK:
            raise MBException("Erro imprimindo: %d", msg.token)

        # Imprime duas vias
        msg = self.mbcontext.MB_EasySendMessage("printer%s" % posid, TK_PRN_PRINT, format=FM_PARAM, data=report, timeout=10000000)  # type: MBMessage
        if msg.token != TK_SYS_ACK:
            raise MBException("Erro imprimindo: %d", msg.token)

    def _cancel_report(self, sat_fiscal_response, nCFe, total):
        # type: () -> unicode
        from printer_wrapper import insert_space

        report = unicode("", "utf-8")
        report += constants.LINESPACING_FUNCS[1]
        report += constants.TXT_FONT_B
        report += constants.TXT_ALIGN_CT  # CENTER

        for line in self.cliche_helper.get_cliche():
            report += line + "\n"
        report += constants.SEPARATOR_DASH
        report += "\n"
        report += constants.TXT_BOLD_ON + "EXTRATO No. %s" % nCFe
        report += "\n"
        report += "CUPOM FISCAL ELETRONICO - SAT"
        report += "\nCANCELAMENTO"
        report += "\n" + constants.TXT_ALIGN_LT + constants.SEPARATOR_DASH

        report += "\nDADOS DO CUPOM FISCAL ELETRONICO CANCELADO"
        cpf_cnpj = sat_fiscal_response.find("CustomerCPF").text
        report += "\nCPF/CNPJ do Consumidor: %s" % ("Nao informado" if not cpf_cnpj else cpf_cnpj)
        report += "\nTOTAL R$ %s" % total

        report += "\n" + constants.SEPARATOR_DASH + "\n" + constants.TXT_ALIGN_CT
        report += constants.TXT_BOLD_ON + "SAT No. %s" % sat_fiscal_response.find("satno").text.strip() + constants.TXT_BOLD_OFF
        report += "\n"
        report += sat_fiscal_response.find("datetime").text.strip()
        report += "\n"
        report += constants.TXT_ALIGN_CT
        satk = insert_space(sat_fiscal_response.find("satkey").text.strip(), 4)
        report += self._center(str(satk))

        report += "\n"

        return report

    def _fiscal_report(self, order, tenders, sat_fiscal_response, total_taxes, nCFe, customer_name, totem_print=False, model=None):
        # type: (eTree.Element, list, eTree.Element, dict, str, str, list) -> unicode
        from printer_wrapper import insert_space

        whopper_wifi_property = order.find("CustomOrderProperties/OrderProperty[@key='WHOPPER_WIFI_CODE']")
        if whopper_wifi_property is not None:
            whopper_wifi_code = whopper_wifi_property.get("value")[0:4] + " " + whopper_wifi_property.get("value")[4:8]
        else:
            whopper_wifi_code = None

        satisfaction_survey_property = order.find("CustomOrderProperties/OrderProperty[@key='SATISFACTION_SURVEY_CODE']")
        if satisfaction_survey_property is not None:
            satisfaction_survey_code = satisfaction_survey_property.get("value")
            if self.satisfaction_survey_text is None:
                self.satisfaction_survey_text = get_storewide_config("Store.GuestSatisfactionSurvey.Text")
        else:
            satisfaction_survey_code = None

        report = unicode("", "utf-8")
        space = ''

        if totem_print:
            space = '\n'
            report += b'\x1b\x33\x14'
            report += constants.TXT_FONT_A
        else:
            report += constants.LINESPACING_FUNCS[1]
            report += constants.TXT_FONT_B

        report += constants.TXT_FONT_B
        report += constants.TXT_ALIGN_CT  # CENTER

        for line in self.cliche_helper.get_cliche():
            report += line + "\n"
        report += constants.SEPARATOR_DASH
        report += "\n"
        report += constants.TXT_BOLD_ON + "EXTRATO No. %s" % nCFe
        report += "\n"
        report += "CUPOM FISCAL ELETRONICO - SAT" + constants.TXT_BOLD_OFF
        report += "\n" + constants.SEPARATOR_DASH
        cpf_cnpj = sat_fiscal_response.find("CustomerCPF").text
        report += "\nCPF/CNPJ do Consumidor: %s" % ("Nao informado" if not cpf_cnpj else cpf_cnpj)
        report += "\n" + (constants.TXT_ALIGN_CT if totem_print else constants.TXT_ALIGN_LT) + constants.SEPARATOR_DASH

        report += space
        # report += "\n#   COD    DESCR    QTD    UN   VL UNIT  R$   VL ITEM R$"
        report += "\nCOD     DESCR              QTD UN    VL UNIT       TOTAL"
        report += "\n"  # + SEPARATOR_DASH + "\n"

        order_voided = order.get("state") == "VOIDED"
        items_amount = 0

        sale_lines = order.findall("SaleLine")
        sale_lines = get_sale_line_priced_items(sale_lines)

        for line in sale_lines:
            item_price, unit_price, item_qty, name, part_code = map(line.get, ("correctItemPrice", "correctUnitPrice", "correctQty", "productName", "partCode"))
            un = "un"
            items_amount += 1
            line = "%-7.7s %-18.18s%6.3f%2.2s%9.02f" % (part_code, name, F(item_qty), un, F(unit_price))  # ("" * level) + onlylabel + label + name
            string = ("%-46.46s %9.02f\n" % (line, F(item_price)))
            report += string

        factor = -1 if order_voided else 1

        report += constants.SEPARATOR_DASH
        report += "\n"
        report += space
        report += "%-44s         %3d\n" % ("QTD. TOTAL DE ITENS", items_amount)
        report += "%-44s   R$%7.2f\n" % ("VALOR TOTAL", float(order.get("totalAmount"))+float(order.get("taxTotal")))
        report += "%-44s   R$%7.2f\n" % ("DESCONTO", float(order.get("discountAmount")))
        report += "%-44s   R$%7.2f\n" % ("VALOR A PAGAR", float(order.get("totalAmount")) + float(order.get("taxTotal")) - float(order.get("discountAmount")))

        report += "\n%-44s  %s\n" % ("FORMA DE PAGAMENTO", "Valor Pago")
        for tender in tenders:
            tender_descr = self.get_payment_description(self.mbcontext, tender)
            tender_amount = tender.amount + tender.change
            report += "%-44s   R$%7.2f\n" % (tender_descr, tender_amount)

        change = tenders[len(tenders) - 1].change  # Get "Change" (sixth value of tender tuple) from last tender in tenders

        if change > 0:
            report += "%-44s   R$%7.2f\n" % ("Troco", change * factor)

        report += constants.SEPARATOR_DASH + "\n"
        if self.print_customer_name:
            char_amount = 21

            content = (customer_name or '')[:(char_amount - 2)] or order.get('orderId')[-3:]
            report += constants.TXT_ALIGN_CT
            report += space
            report += constants.TXT_BOLD_ON + "PAINEL DE RETIRADA - VOCE SERA CHAMADO POR:" + constants.TXT_BOLD_OFF
            report += "\n"
            report += constants.TXT_FONT_A + constants.TXT_INVERT_ON + constants.TXT_ALIGN_CT
            report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[2] + constants.TXT_HEIGHT[2])

            # adiciona espaço em volta do texto impresso
            total_whitespace = char_amount - len(content)
            half_whitespace = total_whitespace // 2
            odd_division = total_whitespace % 2 != 0
            report += " " * half_whitespace
            report += "%s" % content.upper()
            report += " " * (half_whitespace + (1 if odd_division else 0))

            report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[1] + constants.TXT_HEIGHT[1])
            report += constants.TXT_FONT_B + constants.TXT_INVERT_OFF
            report += "\n" + constants.SEPARATOR_DASH + "\n"

        if whopper_wifi_code is not None and model is not None:
            report += constants.TXT_ALIGN_CT
            report += constants.TXT_NORMAL + constants.TXT_BOLD_ON
            report += space
            report += sysactions.translate_message(model, "WIFI_PRINTER_MESSAGE")
            report += "\n" + sysactions.translate_message(model, "WIFI_ACCESS_CODE", "%s" % whopper_wifi_code) + "\n"
            report += constants.TXT_FONT_B + constants.TXT_BOLD_OFF
            report += constants.SEPARATOR_DASH + "\n"

        if satisfaction_survey_code is not None and model is not None:
            report += constants.TXT_ALIGN_CT
            report += constants.TXT_NORMAL
            ssc = satisfaction_survey_code
            satisfaction_survey_code = ssc[:3] + '-' + ssc[3:6] + '-' + ssc[6:9] + '-' + ssc[9:12] + '-' + ssc[12:15] + '-' + ssc[-1]
            report += self.satisfaction_survey_text + satisfaction_survey_code + "\n"
            report += constants.TXT_FONT_B
            report += constants.SEPARATOR_DASH + "\n"

        report = _print_garena_coupons(self.mbcontext, order, report)

        report += constants.TXT_ALIGN_CT
        report += "\n%-44s   R$%7.2f\n" % ("Valor aproximado dos tributos deste cupom", (float(total_taxes['nacionalfederal']['value']) + float(total_taxes['estadual']['value'])))
        report += "Fed = R$%7.2f (%.2f%%), Est = R$%7.2f (%.2f%%)" % (total_taxes['nacionalfederal']['value'], total_taxes['nacionalfederal']['percent'],
                                                                      total_taxes['estadual']['value'], total_taxes['estadual']['percent'])
        report += "\n(Conforme Lei Fed. 12.741/2012)\n"
        report += constants.SEPARATOR_DASH + "\n"

        # Campo de texto customizado exibido na área de informações adicionais
        if self.customer_text_field != "":
            report += "\n" + constants.TXT_ALIGN_CT
            report += "\n" + "%s" % self.customer_text_field.replace("\\n", "\n")
            report += "\n" + constants.SEPARATOR_DASH + "\n"

        report += constants.TXT_BOLD_ON + "SAT No. %s" % sat_fiscal_response.find("satno").text.strip() + constants.TXT_BOLD_OFF
        report += "\n"
        report += sat_fiscal_response.find("datetime").text.strip()
        report += "\n"
        satk = insert_space(sat_fiscal_response.find("satkey").text.strip(), 4)
        report += self._center(str(satk))

        report += "\n"

        return report


class NfceFiscalPrinter(FiscalPrinter):

    def __init__(self, mbcontext, print_customer_name, cliche_helper, qrcode_check_url, versao_ws, customer_text_field, garena_configs):
        # type: (MBEasyContext, bool, ClicheHelper, str, int, str, dict) -> None
        super(NfceFiscalPrinter, self).__init__(mbcontext, print_customer_name, cliche_helper)
        self.qrcode_check_url = qrcode_check_url
        self.versao_ws = versao_ws
        self.customer_text_field = customer_text_field
        self.satisfaction_survey_text = None
        self.garena_configs = garena_configs

    def print_fiscal(self, posid, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        # type: (str, eTree.ElementTree, list, eTree.ElementTree, eTree.ElementTree, dict, str, str) -> str

        model = sysactions.get_model(posid)
        fiscal_xml = remove_xml_namespace(eTree.tostring(fiscal_request))

        tp_emiss = fiscal_xml.find(".//tpEmis").text
        totem_print = sysactions.get_podtype(model) == "TT"

        if tp_emiss == "9":
            report = self._fiscal_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "Via Estabelecimento", customer_name, self.qrcode_check_url, totem_print, model)
            report += "\n\n\n\n\n\n\n\n"
            report += constants.PAPER_PART_CUT
            report += self._fiscal_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "Via Consumidor", customer_name, self.qrcode_check_url, totem_print, model)
            report += self.tef_receipts(tenders)
        else:
            report = self._fiscal_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "", customer_name, self.qrcode_check_url, totem_print, model)
            report += self.tef_receipts(tenders)

        return report

    def print_cancel(self, posid, data):
        return ""

    def read_swconfig(self, key, mbcontext):
        """gets a store wide configuration"""

        rmsg = mbcontext.MB_EasySendMessage("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=key)
        if rmsg.token == TK_SYS_NAK:
            raise Exception("Nao foi possivel obter configuracao %s" % key)

        return str(rmsg.data)

    def _fiscal_report(self, order, tenders, fiscal_request, fiscal_response, total_taxes, via, customer_name, url_sefaz, totem_print=False, model=None):
        # type: (eTree.Element, list, eTree.Element, eTree.Element, dict, str, str, str) -> str

        fiscal_xml = remove_xml_namespace(eTree.tostring(fiscal_request))

        whopper_wifi_property = order.find("CustomOrderProperties/OrderProperty[@key='WHOPPER_WIFI_CODE']")
        if whopper_wifi_property is not None:
            whopper_wifi_code = whopper_wifi_property.get("value")[0:4] + " " + whopper_wifi_property.get("value")[4:8]
        else:
            whopper_wifi_code = None

        satisfaction_survey_property = order.find("CustomOrderProperties/OrderProperty[@key='SATISFACTION_SURVEY_CODE']")
        if satisfaction_survey_property is not None:
            satisfaction_survey_code = satisfaction_survey_property.get("value")
            if self.satisfaction_survey_text is None:
                self.satisfaction_survey_text = get_storewide_config("Store.GuestSatisfactionSurvey.Text")
        else:
            satisfaction_survey_code = None

        report = unicode("", "utf-8")
        space = ''

        if totem_print:
            space = '\n'
            report += b'\x1b\x33\x14'
            report += constants.TXT_FONT_A
        else:
            report += constants.LINESPACING_FUNCS[1]

        report += constants.TXT_FONT_B

        report += constants.TXT_ALIGN_CT  # CENTER

        for line in self.cliche_helper.get_cliche():
            report += line + "\n"
        report += constants.SEPARATOR_DASH
        report += space
        report += "Documento Auxiliar da Nota Fiscal\n"
        report += "de Consumidor Eletronica\n"
        report += constants.SEPARATOR_DASH
        report += space

        tp_emiss = fiscal_xml.find(".//tpEmis").text

        if tp_emiss == "9":
            report += constants.TXT_BOLD_ON
            report += "\nEMITIDA EM CONTINGENCIA\n"
            report += constants.TXT_BOLD_OFF
            report += "Pendente de autorizacao\n"
            report += constants.SEPARATOR_DASH
        report += space
        report += constants.TXT_BOLD_ON
        report += "COD     DESCR              QTD UN    VL UNIT       TOTAL\n"
        report += constants.TXT_BOLD_OFF

        items_amount = 0

        sale_lines = order.findall("SaleLine")
        sale_lines = get_sale_line_priced_items(sale_lines)

        for line in sale_lines:
            item_price, unit_price, item_qty, name, part_code = map(line.get, ("correctItemPrice", "correctUnitPrice", "correctQty", "productName", "partCode"))
            un = "un"
            items_amount += 1
            line = "%-7.7s %-18.18s%6.3f%2.2s%9.02f" % (part_code, name, F(item_qty), un, F(unit_price))  # ("" * level) + onlylabel + label + name
            string = ("%-46.46s %9.02f\n" % (line, F(item_price)))
            report += string

        # Totalizador + Pagamentos + Troco
        report += constants.SEPARATOR_DASH
        report += "\n"
        report += space
        report += "%-44s         %3d\n" % ("QTD. TOTAL DE ITENS", items_amount)
        report += "%-44s   R$%7.2f\n" % ("VALOR TOTAL R$", float(order.get("totalAmount")) + float(order.get("taxTotal")))
        report += "%-44s   R$%7.2f\n" % ("DESCONTO", float(order.get("discountAmount")))
        report += "%-44s   R$%7.2f\n" % ("VALOR A PAGAR", float(order.get("totalAmount")) + float(order.get("taxTotal")) - float(order.get("discountAmount")))

        report += "\n%-44s  %s\n" % ("FORMA DE PAGAMENTO", "Valor Pago")
        for tender in tenders:
            tender_descr = self.get_payment_description(self.mbcontext, tender)
            tender_amount = tender.amount + tender.change
            report += "%-44s   R$%7.2f\n" % (tender_descr, tender_amount)

        change = tenders[len(tenders) - 1].change  # Get "Change" (sixth value of tender tuple) from last tender in tenders

        if change > 0:
            report += "%-44s   R$%7.2f\n" % ("Troco", change)

        report += constants.SEPARATOR_DASH + "\n"
        if self.print_customer_name:
            char_amount = 21

            content = (customer_name or '')[:(char_amount - 2)] or order.get('orderId')[-3:]
            report += constants.TXT_ALIGN_CT
            report += space
            report += constants.TXT_BOLD_ON + "PAINEL DE RETIRADA - VOCE SERA CHAMADO POR:" + constants.TXT_BOLD_OFF
            report += space
            report += "\n"
            report += constants.TXT_FONT_A + constants.TXT_INVERT_ON + constants.TXT_ALIGN_CT
            report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[2] + constants.TXT_HEIGHT[2])

            # adiciona espaço em volta do texto impresso
            total_whitespace = char_amount - len(content)
            half_whitespace = total_whitespace // 2
            odd_division = total_whitespace % 2 != 0
            report += " " * half_whitespace
            report += "%s" % content.upper()
            report += " " * (half_whitespace + (1 if odd_division else 0))

            report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[1] + constants.TXT_HEIGHT[1])
            report += constants.TXT_FONT_B + constants.TXT_INVERT_OFF
            report += "\n" + constants.SEPARATOR_DASH + "\n"
            report += space

        if whopper_wifi_code is not None and model is not None:
            report += constants.TXT_ALIGN_CT
            report += constants.TXT_NORMAL + constants.TXT_BOLD_ON
            report += sysactions.translate_message(model, "WIFI_PRINTER_MESSAGE")
            report += "\n" + sysactions.translate_message(model, "WIFI_ACCESS_CODE", "%s" % whopper_wifi_code) + "\n"
            report += constants.TXT_FONT_B + constants.TXT_BOLD_OFF
            report += constants.SEPARATOR_DASH + "\n"

        if satisfaction_survey_code is not None and model is not None:
            report += constants.TXT_ALIGN_CT
            report += constants.TXT_NORMAL
            ssc = satisfaction_survey_code
            satisfaction_survey_code = ssc[:3] + '-' + ssc[3:6] + '-' + ssc[6:9] + '-' + ssc[9:12] + '-' + ssc[12:15] + '-' + ssc[-1]
            report += self.satisfaction_survey_text + satisfaction_survey_code + "\n"
            report += constants.TXT_FONT_B
            report += constants.SEPARATOR_DASH + "\n"

        report = _print_garena_coupons(self.mbcontext, order, report)

        report += constants.TXT_ALIGN_CT + constants.TXT_BOLD_ON
        report += "Consulte pela Chave de Acesso em\n"
        report += constants.TXT_BOLD_OFF
        report += url_sefaz + "\n"

        chave = fiscal_xml.find(".//infNFe").attrib['Id'][3:]

        for i in range(0, 44, 4):
            report += chave[i:i + 4] + " "
        report += "\n"

        cpf_cnpj = ""
        cpf = fiscal_xml.find(".//dest/CPF")
        if cpf is not None:
            cpf_cnpj = cpf.text
        else:
            cnpj = fiscal_xml.find(".//dest/CNPJ")
            if cnpj is not None:
                cpf_cnpj = cnpj.text

        # Consumidor
        report += constants.TXT_BOLD_ON
        report += "CONSUMIDOR %s" % ("NAO INFORMADO" if not cpf_cnpj else ("- CPF " + cpf_cnpj))

        numero = fiscal_xml.find(".//nNF").text
        serie = fiscal_xml.find(".//serie").text
        data_emissao_xml = fiscal_xml.find(".//dhEmi").text
        tp_amb = fiscal_xml.find(".//tpAmb").text

        data_emissao_str = self._formata_data(data_emissao_xml)
        report += "\nNFC-e Numero %09d  Serie %03d  %s\n" % (int(numero), int(serie), data_emissao_str)

        if tp_emiss == "9":
            report += via + "\n"

        response_xml = None
        if fiscal_response is not None:
            response_xml = remove_xml_namespace(eTree.tostring(fiscal_response))

        if response_xml is not None:
            protocolo_element = response_xml.find(".//nProt").text
            if protocolo_element is not None:
                report += constants.TXT_BOLD_ON
                report += "Protocolo de autorizacao: "
                report += constants.TXT_BOLD_OFF
                report += protocolo_element + "\n"

                data_protocolo = response_xml.find(".//dhRecbto").text
                report += constants.TXT_BOLD_ON
                report += "Data de autorizacao: "
                report += constants.TXT_BOLD_OFF
                report += self._formata_data(data_protocolo)

        url = fiscal_xml.find(".//qrCode").text

        if tp_amb == "2":
            report += constants.TXT_BOLD_ON
            report += "EMITIDA EM HOMOLOGACAO - SEM VALOR FISCAL\n"
            report += constants.TXT_BOLD_OFF
        if tp_emiss == "9":
            report += constants.TXT_BOLD_ON
            report += "EMITIDA EM CONTINGENCIA\n"
            report += constants.TXT_BOLD_OFF
            report += "Pendente de autorizacao\n"

        report = report.encode("utf-8") + "\n"
        report += constants.TXT_ALIGN_CT
        report += printer_wrapper.qr(url)

        if response_xml is not None:
            message_code_tag = response_xml.find(".//infProt/cMsg")
            message_code = message_code_tag.text if message_code_tag is not None else None
            message_text_tag = response_xml.find(".//infProt/xMsg")
            message_text = message_text_tag.text if message_text_tag is not None else None
            if message_code == '200' and message_text not in [None, '', ' ']:
                report += '\n' + message_text.replace('|', '\n').strip()

        # Valor aproximado dos tributos
        report += constants.TXT_BOLD_OFF
        report += "\n%-44s   R$%7.2f\n" % ("Valor aproximado dos tributos deste cupom", (float(total_taxes['nacionalfederal']['value'] + float(total_taxes['estadual']['value']))))
        report += "Fed = R$%7.2f (%.2f%%), Est = R$%7.2f (%.2f%%)" % (total_taxes['nacionalfederal']['value'], total_taxes['nacionalfederal']['percent'], total_taxes['estadual']['value'], total_taxes['estadual']['percent'])
        report += "\n(Conforme Lei Fed. 12.741/2012)\n"
        report += constants.TXT_ALIGN_LT

        # Campo de texto customizado exibido na �rea de informa��es adicionais
        if self.customer_text_field != "":
            report += constants.TXT_ALIGN_CT
            report += "\n" + str(self.customer_text_field.replace("\\n", "\n"))
            report += "\n" + constants.TXT_ALIGN_LT

        return report

    def _formata_data(self, data, mascara="%d/%m/%Y %H:%M:%S"):
        data_emissao_date_utc = data[:19]
        data_emissao_date_utc = datetime.datetime.strptime(data_emissao_date_utc, "%Y-%m-%dT%H:%M:%S")
        data_emissao_offset = int(data[20:22]) * 60 + int(data[23:])
        if data[19] == "+":
            data_emissao_offset *= -1
        data_emissao_date_utc = data_emissao_date_utc + datetime.timedelta(minutes=data_emissao_offset)
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()

        data_emissao_date = data_emissao_date_utc.replace(tzinfo=from_zone)
        # Convert time zone
        data_emissao_date = data_emissao_date.astimezone(to_zone)
        data_emissao_str = data_emissao_date.strftime(mascara)
        return data_emissao_str


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode('utf8'))).encode('ascii', 'ignore')


def _print_garena_coupons(mb_context, order, report):
    garena_custom_property = order.find("CustomOrderProperties/OrderProperty[@key='GARENA_COUPONS']")
    garena_coupons = None
    if garena_custom_property is not None:
        garena_coupons = garena_custom_property.get("value").split("|")
    if garena_coupons:
        request_data = []
        for coupon in garena_coupons:

            coupon_obj = literal_eval(coupon)
            coupon_id = coupon_obj['couponId']
            request_data.append(coupon_id)

        try:
            ret = mb_context.MB_EasySendMessage("Garena", TK_DECRYPT_GARENA_COUPON, data="|".join(request_data), timeout=5000000)
            if ret.token == TK_SYS_NAK or not ret.data:
                raise VoidOrderException("Error decrypting garena coupon")
        except:
            return report

        garena_coupon_data = {}
        decrypted_coupons = json.loads(ret.data)
        for coupon in decrypted_coupons:
            coupon_data = json.loads(coupon['coupon_data'])
            garena_coupon_data.setdefault(coupon_data['promo']['description'], []).append(coupon['decrypted_data'])

        for promo in garena_coupon_data:
            report += constants.TXT_ALIGN_CT
            report += constants.TXT_NORMAL + constants.TXT_BOLD_ON
            report += _remove_accents(promo) + "\n"

            for decrypted_coupon in garena_coupon_data[promo]:
                report += decrypted_coupon + "\n"

            report += constants.TXT_FONT_B + constants.TXT_BOLD_OFF
            report += constants.SEPARATOR_DASH + "\n"

    return report
