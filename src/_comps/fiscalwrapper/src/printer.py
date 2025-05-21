# -*- coding: utf-8 -*-

import base64
import json
import time
from ast import literal_eval
from datetime import datetime, timedelta
from unicodedata import normalize
from xml.etree import cElementTree as eTree
from xml.etree.cElementTree import Element

import constants
import printer_wrapper
import sysactions
from bustoken import create_token
from clichehelper import ClicheHelper
from comp_exceptions import VoidOrderException
from dateutil import tz
from msgbus import FM_PARAM, TK_SYS_ACK, TK_PRN_PRINT, MBException, MBEasyContext, TK_SYS_NAK
from old_helper import F, get_sale_line_priced_items, regex_search
from persistence import Driver as DBDriver, AprDbdException
from typing import Optional, Dict

SATISFACTION_SURVEY_TEXT = None  # type: Optional[str]
PAYMENTS_DESCRIPTION = {}
TK_DECRYPT_GARENA_COUPON = create_token("F", "99", "2")


class FiscalPrinter(object):
    def __init__(self, mb_context, print_customer_name, cliche_helper):
        # type: (MBEasyContext, bool, ClicheHelper) -> None
        self.mb_context = mb_context
        self.print_customer_name = print_customer_name
        self.print_merchant_receipt = None
        self.cliche_helper = cliche_helper
        sysactions.mbcontext = mb_context

    def print_fiscal(self, pos_id, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        raise NotImplementedError()

    def print_cancel(self, pos_id, data):
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


class DonationCouponPrinter(object):
    def __init__(self, cliche, nf_type):
        # type: (ClicheHelper, str) -> None
        self.nf_type = nf_type
        self.cliche = cliche

    def print_coupon(self, pos_id, order_id, customer_name, donation_value, donation_institution, donation_cnpj, donation_site):
        model = sysactions.get_model(pos_id)
        report = ""
        if self.nf_type != "PAF":
            report += constants.LINESPACING_FUNCS[1]
            report += constants.TXT_FONT_B
            report += constants.TXT_ALIGN_CT
            for row in self.cliche.get_cliche():
                report += row + "\n"
            report += constants.SEPARATOR_DASH + "\n"
            report += constants.TXT_ALIGN_LT
            report += "%-44s   %s" % (datetime.now().strftime("%d/%m/%y"), datetime.now().strftime("%H:%M:%S")) + "\n"
            report += "NAO E DOCUMENTO FISCAL\n"
            report += constants.TXT_ALIGN_CT + constants.TXT_BOLD_ON + "COMPROVANTE NAO FISCAL" + constants.TXT_BOLD_OFF + "\n"
            report += constants.TXT_ALIGN_LT
            client_name = constants.TXT_BOLD_ON \
                          + (customer_name[:30] or _translate(model, "UNINFORMED")).upper() \
                          + "\n" \
                          + constants.TXT_BOLD_OFF
            report += "%-12s   %46s" % (_translate(model, "ORDER_NUMBER", "%s" % order_id),
                                        _translate(model, "CLIENT_NAME", "%s" % _remove_accents(client_name))) + "\n"
            report += "%-44s   %s %s" % (_remove_accents(_translate(model, "DONATION_VALUE")),
                                         _translate(model, "L10N_CURRENCY_SYMBOL"),
                                         donation_value)
            report += "\n" + constants.SEPARATOR_DASH + "\n"
            report += constants.TXT_ALIGN_CT
            report += _translate(model, "DONATION_INSTITUTION", "%s" % donation_institution) + "\n"
            report += _translate(model, "DONATION_CNPJ", "%s" % donation_cnpj) + "\n"
            report += "%s" % donation_site
        else:
            report += datetime.now().strftime("%d/%m/%y %H:%M:%S") + "\n"
            report += _translate(model, "ORDER_NUMBER", "%s" % order_id) + "\n"
            report += _translate(model, "CLIENT_NAME", "%s" % (customer_name or _translate(model, "UNINFORMED")).upper())
            report += "\n\n" + "%-37s   %s %s" % (_translate(model, "DONATION_VALUE"),
                                                  _translate(model, "L10N_CURRENCY_SYMBOL"),
                                                  donation_value)
            report += "\n------------------------------------------------\n"
            report += _translate(model, "DONATION_INSTITUTION", "%s" % _remove_accents(donation_institution)) + "\n"
            report += _translate(model, "DONATION_CNPJ", "%s" % donation_cnpj) + "\n"
            report += "%s" % donation_site

        return report


class SatFiscalPrinter(FiscalPrinter):
    def __init__(self, mb_context, print_customer_name, cliche_helper, customer_text_field, garena_configs, tip_config, print_order_identifier):
        # type: (MBEasyContext, bool, ClicheHelper, str, Dict, Dict, bool) -> None
        super(SatFiscalPrinter, self).__init__(mb_context, print_customer_name, cliche_helper)
        self.customer_text_field = customer_text_field
        self.tip_config = tip_config
        self.print_order_identifier = print_order_identifier
        self.garena_configs = garena_configs

    def print_fiscal(self, pos_id, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        # type: (str, Element, list, Element, Element, dict, str, Optional[str]) -> None
        xml = base64.b64decode(fiscal_request.text.strip())
        parsed_xml = eTree.XML(xml)
        n_c_fe = parsed_xml.find("infCFe/ide/nCFe").text
        model = sysactions.get_model(pos_id)

        totem_print = sysactions.get_podtype(sysactions.get_model(pos_id)) == "TT"

        report = self._build_report(order, tenders, fiscal_response, total_taxes, n_c_fe, customer_name, totem_print, model)

        barcode1, barcode2 = printer_wrapper.barcode(fiscal_response.find("satkey").text.strip())
        qr_code = printer_wrapper.qr(fiscal_response.find("QRCode").text.strip())

        report = report.encode("utf-8") + barcode1
        report += barcode2
        report += "\n"
        report += constants.TXT_ALIGN_CT
        report += qr_code
        report += constants.TXT_ALIGN_LT
        report += constants.PAPER_EMPTY_SPACE + constants.PAPER_PART_CUT
        return report

    def print_cancel(self, pos_id, data):
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

        for _ in range(0, 2):
            self._print_with_retry(pos_id, report)

    def _print_with_retry(self, pos_id, report):
        msg = None
        printer = "printer%s" % pos_id
        try:
            msg = self.mb_context.MB_EasySendMessage(printer, TK_PRN_PRINT, FM_PARAM, report, 10000000)
        except MBException:
            time.sleep(0.5)
            msg = self.mb_context.MB_EasySendMessage(printer, TK_PRN_PRINT, FM_PARAM, report, 10000000)
        finally:
            if msg and msg.token != TK_SYS_ACK:
                raise MBException("Erro imprimindo: %d", msg.token)

    def _cancel_report(self, sat_fiscal_response, ncfe_number, total):
        report = unicode("", "utf-8")
        report += constants.LINESPACING_FUNCS[1]
        report += constants.TXT_FONT_B
        report += constants.TXT_ALIGN_CT

        for line in self.cliche_helper.get_cliche():
            report += line + "\n"
        report += constants.SEPARATOR_DASH
        report += "\n"
        report += constants.TXT_BOLD_ON + "EXTRATO No. %s" % ncfe_number
        report += "\n"
        report += "CUPOM FISCAL ELETRONICO - SAT"
        report += "\nCANCELAMENTO"
        report += "\n" + constants.TXT_ALIGN_CT + constants.SEPARATOR_DASH

        report += "\nDADOS DO CUPOM FISCAL ELETRONICO CANCELADO"
        cpf_cnpj = sat_fiscal_response.find("CustomerCPF").text
        report += "\nCPF/CNPJ do Consumidor: %s" % ("Nao informado" if not cpf_cnpj else cpf_cnpj)
        report += "\nTOTAL R$ %s" % total
        report = self._build_footer(report, sat_fiscal_response)

        return report

    def _build_report(self, order, tenders, fiscal_request, total_taxes, ncfe_number, customer_name, totem_print=False, model=None):
        # type: (Element, list, Element, dict, str, str, Optional[list], Optional[Element]) -> unicode
        report = _build_start_configs(self.cliche_helper, totem_print)
        report = self._build_header(ncfe_number, report, fiscal_request, totem_print)
        report = _common_fiscal_coupon(self.mb_context, customer_name, model, order, report, tenders, totem_print, self.tip_config, self.print_customer_name, self.print_order_identifier, self.customer_text_field)
        report = _build_coupon_tax(report, total_taxes)
        report = self._build_footer(report, fiscal_request)
        report += constants.TXT_FONT_A

        return report

    def _build_footer(self, report, sat_fiscal_response):
        report += "\n" + constants.SEPARATOR_DASH + "\n" + constants.TXT_ALIGN_CT
        report += constants.TXT_BOLD_ON + "SAT No. %s" % sat_fiscal_response.find("satno").text.strip() + constants.TXT_BOLD_OFF
        report += "\n"
        report += sat_fiscal_response.find("datetime").text.strip()
        report += "\n"
        report += constants.TXT_ALIGN_CT
        from printer_wrapper import insert_space
        sat_key = insert_space(sat_fiscal_response.find("satkey").text.strip(), 4)
        report += self._center(str(sat_key))
        report += "\n"
        return report

    @staticmethod
    def _build_header(ncfe_number, report, fiscal_response, totem_print):
        report += constants.TXT_ALIGN_CT + constants.SEPARATOR_DASH
        report += "\n"
        report += constants.TXT_BOLD_ON + "EXTRATO No. %s" % ncfe_number
        report += "\n"
        report += "CUPOM FISCAL ELETRONICO - SAT" + constants.TXT_BOLD_OFF
        report += "\n" + constants.SEPARATOR_DASH
        cpf_cnpj = fiscal_response.find("CustomerCPF").text
        report += "\nCPF/CNPJ do Consumidor: %s" % ("Nao informado" if not cpf_cnpj else cpf_cnpj)
        report += "\n" + (constants.TXT_ALIGN_CT if totem_print else constants.TXT_ALIGN_LT) + constants.SEPARATOR_DASH
        report += "\n" if totem_print else ""
        report += "\nCOD     DESCR              QTD UN    VL UNIT       TOTAL"
        report += "\n"
        return report


class NfceFiscalPrinter(FiscalPrinter):
    def __init__(self, mb_context, print_customer_name, cliche_helper, qrcode_check_url, versao_ws, customer_text_field, garena_configs, tip_config, print_order_identifier):
        # type: (MBEasyContext, bool, ClicheHelper, str, int, str, Dict, Dict, bool) -> None
        super(NfceFiscalPrinter, self).__init__(mb_context, print_customer_name, cliche_helper)
        self.qrcode_check_url = qrcode_check_url
        self.versao_ws = versao_ws
        self.customer_text_field = customer_text_field
        self.tip_config = tip_config
        self.print_order_identifier = print_order_identifier
        self.garena_configs = garena_configs

    def print_fiscal(self, pos_id, order, tenders, fiscal_request, fiscal_response, total_taxes, customer_name, url_sefaz=""):
        # type: (str, Element, list, Element, Element, dict, str, str) -> unicode

        model = sysactions.get_model(pos_id)

        re_search = r"<[A-z0-9]*?:?{0}>(.*?)</([A-z0-9]*?):?{0}>"
        tp_emiss = regex_search(re_search, eTree.tostring(fiscal_request), key="tpEmis")

        totem_print = sysactions.get_podtype(model) == "TT"

        if tp_emiss == "9":
            report = self._build_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "Via Estabelecimento", customer_name, self.qrcode_check_url, totem_print, model)
            report += "\n\n\n\n\n\n\n\n"
            report += constants.PAPER_PART_CUT
            report += self._build_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "Via Consumidor", customer_name, self.qrcode_check_url, totem_print, model)
        else:
            report = self._build_report(order, tenders, fiscal_request, fiscal_response, total_taxes, "", customer_name, self.qrcode_check_url, totem_print, model)

        return report

    def print_cancel(self, pos_id, data):
        return ""

    @staticmethod
    def _build_footer(fiscal_request, fiscal_response, re_search, report, tp_emiss, url_sefaz, via):
        report += constants.TXT_ALIGN_CT + constants.TXT_BOLD_ON
        report += "\nConsulte pela Chave de Acesso em\n"
        report += constants.TXT_BOLD_OFF
        report += url_sefaz + "\n"

        re_search_attribute_id = r"<[A-z0-9]*?:?infNFe.*?Id=\"(.*?)\""
        chave = regex_search(re_search_attribute_id, eTree.tostring(fiscal_request), key="infNFe")[3:]
        for i in range(0, 44, 4):
            report += chave[i:i + 4] + " "
        report += "\n"
        customer_properties_search = r"<dest>[\s\S]*?<{0}>(.*?)</{0}>[\s\S]*?</dest>"
        cpf_cnpj = ""
        cpf = regex_search(customer_properties_search, eTree.tostring(fiscal_request), key="CPF")
        if cpf is not None:
            cpf_cnpj = cpf
        else:
            cnpj = regex_search(customer_properties_search, eTree.tostring(fiscal_request), key="CNPJ")
            if cnpj is not None:
                cpf_cnpj = cnpj

        # Consumidor
        report += constants.TXT_BOLD_ON
        report += "\nCONSUMIDOR %s" % ("NAO INFORMADO" if not cpf_cnpj else ("- CPF " + cpf_cnpj))
        numero = regex_search(re_search, eTree.tostring(fiscal_request), key="nNF")
        serie = regex_search(re_search, eTree.tostring(fiscal_request), key="serie")
        data_emissao_xml = regex_search(re_search, eTree.tostring(fiscal_request), key="dhEmi")
        data_emissao_str = _format_date(data_emissao_xml)
        report += "\n\nNFC-e Numero %09d  Serie %03d  %s\n" % (int(numero), int(serie), data_emissao_str)
        tp_amb = regex_search(re_search, eTree.tostring(fiscal_request), key="tpAmb")

        if tp_emiss == "9":
            report += "\n" + via + "\n"
        if fiscal_response is not None:
            protocolo_element = regex_search(re_search, eTree.tostring(fiscal_response), key="nProt")
            if protocolo_element is not None:
                report += constants.TXT_BOLD_ON
                report += "\nProtocolo de autorizacao: "
                report += constants.TXT_BOLD_OFF
                report += protocolo_element + "\n"

                data_protocolo = regex_search(re_search, eTree.tostring(fiscal_response), key="dhRecbto")
                report += constants.TXT_BOLD_ON
                report += "\nData de autorizacao: "
                report += constants.TXT_BOLD_OFF
                report += _format_date(data_protocolo) + "\n"

        if tp_amb == "2":
            report += constants.TXT_BOLD_ON
            report += "\nEMITIDA EM HOMOLOGACAO - SEM VALOR FISCAL\n"
            report += constants.TXT_BOLD_OFF
        if tp_emiss == "9":
            report += constants.TXT_BOLD_ON
            report += "\nEMITIDA EM CONTINGENCIA\n"
            report += constants.TXT_BOLD_OFF
            report += "Pendente de autorizacao\n"

        report = report.encode("utf-8") + "\n"
        report += constants.TXT_ALIGN_CT
        url = regex_search(re_search, eTree.tostring(fiscal_request), key="qrCode")
        report += printer_wrapper.qr(url)

        return report

    def _build_report(self, order, tenders, fiscal_request, fiscal_response, total_taxes, via, customer_name, url_sefaz, totem_print=False, model=None):
        # type: (Element, list, Element, Element, dict, str, str, str, Optional[bool], Optional[Element]) -> str
        report = _build_start_configs(self.cliche_helper, totem_print)
        re_search, report, tp_emiss = self._build_header(fiscal_request, report)
        report = _common_fiscal_coupon(self.mb_context, customer_name, model, order, report, tenders, totem_print, self.tip_config, self.print_customer_name, self.print_order_identifier, self.customer_text_field)
        report = self._build_footer(fiscal_request, fiscal_response, re_search, report, tp_emiss, url_sefaz, via)
        report = _build_coupon_tax(report, total_taxes)
        report += constants.TXT_FONT_A

        return report

    @staticmethod
    def _build_header(fiscal_request, report):
        report += constants.SEPARATOR_DASH
        report += "\n"
        report += "Documento Auxiliar da Nota Fiscal\n"
        report += "de Consumidor Eletronica\n"
        report += constants.SEPARATOR_DASH
        report += "\n"
        re_search = r"<[A-z0-9]*?:?{0}>(.*?)</([A-z0-9]*?):?{0}>"
        tp_emiss = regex_search(re_search, eTree.tostring(fiscal_request), key="tpEmis")
        if tp_emiss == "9":
            report += constants.TXT_BOLD_ON
            report += "\nEMITIDA EM CONTINGENCIA\n"
            report += constants.TXT_BOLD_OFF
            report += "Pendente de autorizacao\n"
            report += constants.SEPARATOR_DASH
        report += constants.TXT_BOLD_ON
        report += "COD     DESCR              QTD UN    VL UNIT       TOTAL\n"
        report += constants.TXT_BOLD_OFF
        return re_search, report, tp_emiss


def _common_fiscal_coupon(mb_context, customer_name, model, order, report, tenders, totem_print, tip_config, print_customer_name, print_order_identifier, customer_text_field):
    sale_lines = get_sale_line_priced_items(order.findall("SaleLine"))
    items_amount, order_tip, report = _build_sale_lines(tip_config, model, order, report, sale_lines)
    report = _build_order_totals(mb_context, items_amount, order, order_tip, report, tenders, totem_print)
    report = _build_customer_name(print_customer_name, customer_name, order, report, totem_print)
    report = _build_whopper_wifi_code(model, report, order, totem_print)
    report = _build_satisfaction_survey_code(model, report, order)
    report = _build_garena_code(mb_context, order, report)
    report = _build_order_identifier(report, print_order_identifier, order)
    report = _build_custom_text_field(customer_text_field, report)
    return report


def _build_sale_lines(tip_config, model, order, report, sale_lines):
    items_amount = 0
    for line in sale_lines:
        line_params = map(line.get, ("correctItemPrice", "correctUnitPrice", "correctQty", "productName", "partCode"))
        item_price, unit_price, item_qty, name, part_code = line_params
        measure_unit = line.get("measureUnit") if "measureUnit" in line.attrib else "un"
        items_amount += 1
        line = "%-7.7s %-18.18s%6.3f%2.2s%9.02f" % (part_code, name, F(item_qty), measure_unit, F(unit_price))
        string = ("%-46.46s %9.02f\n" % (line, F(item_price)))
        report += _remove_accents(string.encode('utf-8'))
    order_tip = 0.0
    if order.get("tip") and float(order.get("tip")) > 0:
        order_tip = F(order.get("tip"))
        tip_line = "%-7.7s %-18.18s%6.3f%2.2s%9.02f" % (
        tip_config['TipCode'], sysactions.translate_message(model, "TIP_GIVEN").upper(), F(1), "un", order_tip)
        report += ("%-46.46s %9.02f\n" % (tip_line, order_tip))
        items_amount += 1
    return items_amount, order_tip, report


def _build_whopper_wifi_code(model, report, order, totem_print):
    whopper_wifi_code = _get_whopper_wifi_code(order)
    if whopper_wifi_code is not None and model is not None:
        report += constants.TXT_ALIGN_CT
        report += constants.TXT_NORMAL + constants.TXT_BOLD_ON
        report += "\n" if totem_print else ""
        report += sysactions.translate_message(model, "WIFI_PRINTER_MESSAGE")
        report += "\n" + sysactions.translate_message(model, "WIFI_ACCESS_CODE", "%s" % whopper_wifi_code) + "\n"
        report += constants.TXT_FONT_B + constants.TXT_BOLD_OFF
        report += constants.SEPARATOR_DASH + "\n"
    return report


def _build_satisfaction_survey_code(model, report, order):
    satisfaction_survey_code = _get_satisfaction_survey_code(order)
    if satisfaction_survey_code is not None and model is not None:
        report += constants.TXT_ALIGN_CT
        report += constants.TXT_NORMAL
        ssc = satisfaction_survey_code
        satisfaction_survey_code = ssc[:3] + '-' + ssc[3:6] + '-' + ssc[6:9] + '-' + ssc[9:12] + '-' + ssc[12:15] + '-' + ssc[-1]
        report += SATISFACTION_SURVEY_TEXT + satisfaction_survey_code + "\n"
        report += constants.TXT_FONT_B
        report += constants.SEPARATOR_DASH + "\n"
    return report


def _build_customer_name(print_customer_name, customer_name, order, report, totem_print):
    if print_customer_name and order.find(".//OrderProperty[@key='TABLE_ID']") is None:
        char_amount = 21
        content = (customer_name or '')[:(char_amount - 2)] or order.get('orderId')[-3:]
        report += constants.TXT_ALIGN_CT
        report += "\n" if totem_print else ""
        report += constants.TXT_BOLD_ON + "PAINEL DE RETIRADA - VOCE SERA CHAMADO POR:" + constants.TXT_BOLD_OFF
        report += "\n"
        report += constants.TXT_FONT_A + constants.TXT_INVERT_ON + constants.TXT_ALIGN_CT
        report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[2] + constants.TXT_HEIGHT[2])

        total_whitespace = char_amount - len(content)
        half_whitespace = total_whitespace // 2
        odd_division = total_whitespace % 2 != 0
        report += " " * half_whitespace
        report += "%s" % content.upper()
        report += " " * (half_whitespace + (1 if odd_division else 0))

        report += constants.TXT_SIZE + chr(constants.TXT_WIDTH[1] + constants.TXT_HEIGHT[1])
        report += constants.TXT_FONT_B + constants.TXT_INVERT_OFF
        report += "\n" + constants.SEPARATOR_DASH + "\n"

    return report


def _build_start_configs(cliche_helper, totem_print):
    report = unicode("", "utf-8")
    if totem_print:
        report += b'\x1b\x33\x14'
        report += constants.TXT_FONT_A
    else:
        report += constants.LINESPACING_FUNCS[1]
        report += constants.TXT_FONT_B

    report += constants.TXT_ALIGN_CT  # CENTER
    for line in cliche_helper.get_cliche():
        report += _remove_accents(line) + "\n"
    return report


def _build_custom_text_field(customer_text_field, report):
    if customer_text_field != "":
        report += constants.TXT_ALIGN_CT
        report += "\n" + "%s" % customer_text_field.replace("\\n", "\n")
        report += "\n" + constants.SEPARATOR_DASH + "\n"
    return report


def _build_order_identifier(report, print_order_identifier, order):
    if print_order_identifier:
        order_id = order.get("orderId")
        user_id = order.get("sessionId").split("user=")[1].split(",")[0]
        operator_name = eTree.XML(sysactions.get_user_information(user_id)).find(".//user").get("LongName")[:15]
        table_property = order.find("CustomOrderProperties/OrderProperty[@key='TABLE_ID']")
        table_id = table_property.get("value") if table_property is not None else None
        if table_id:
            order_label = "Pedido/Mesa: {}/{}".format(order_id[-4:], table_id)
        else:
            order_label = "Pedido: {}".format(order_id[-4:])

        report += "Operador: {}  {}".format(operator_name, order_label)
        report += "\n" + constants.SEPARATOR_DASH + "\n"
    return report


def _build_coupon_tax(report, total_taxes):
    report += constants.TXT_ALIGN_CT
    total_tax_amount = float(total_taxes['nacionalfederal']['value']) + float(total_taxes['estadual']['value'])
    report += "%-44s   R$%7.2f\n" % ("Valor aproximado dos tributos deste cupom", total_tax_amount)
    report += "Fed = R$%7.2f (%.2f%%), Est = R$%7.2f (%.2f%%)" % (total_taxes['nacionalfederal']['value'],
                                                                  total_taxes['nacionalfederal']['percent'],
                                                                  total_taxes['estadual']['value'],
                                                                  total_taxes['estadual']['percent'])
    report += "\n(Conforme Lei Fed. 12.741/2012)"
    return report


def _build_order_totals(mb_context, items_amount, order, order_tip, report, tenders, totem_print):
    discount_amount = float(order.get("discountAmount") or 0)
    total_amount = float(order.get("totalAmount"))
    tax_total = float(order.get("taxTotal"))
    order_voided = order.get("state") == "VOIDED"
    factor = -1 if order_voided else 1

    report += constants.SEPARATOR_DASH + "\n"
    report += "\n" if totem_print else ""
    report += "%-44s         %3d\n" % ("QTD. TOTAL DE ITENS", items_amount)
    report += "%-44s   R$%7.2f\n" % ("VALOR TOTAL", total_amount + tax_total + order_tip)

    if discount_amount:
        bonus_type = "DESCONTO" if discount_amount > 0 else "ACRESCIMO"
        report += "%-44s   R$%7.2f\n" % (bonus_type, abs(discount_amount))

    total_amount = total_amount + tax_total - discount_amount + order_tip
    report += "%-44s   R$%7.2f\n" % ("VALOR A PAGAR", total_amount)
    report += "\n%-44s  %s\n" % ("FORMA DE PAGAMENTO", "Valor Pago")

    for tender in tenders:
        tender_descr = _remove_accents(get_payment_description(mb_context, tender))
        tender_amount = tender.amount
        report += "%-44s   R$%7.2f\n" % (tender_descr, tender_amount)

    change = tenders[len(tenders) - 1].change  # Get "Change" (sixth value of tender tuple) from last tender in tenders
    if change > 0:
        report += "%-44s   R$%7.2f\n" % ("Troco", change * factor)

    report += constants.SEPARATOR_DASH + "\n"
    return report


def _get_whopper_wifi_code(order):
    prop_path = "CustomOrderProperties/OrderProperty[@key='WHOPPER_WIFI_CODE']"
    whopper_wifi_code = order.find(prop_path).get("value") if order.find(prop_path) is not None else None
    if whopper_wifi_code is not None:
        whopper_wifi_code = whopper_wifi_code[0:4] + " " + whopper_wifi_code[4:8]
    return whopper_wifi_code


def _get_satisfaction_survey_code(order):
    global SATISFACTION_SURVEY_TEXT

    satisfaction_survey_property = order.find("CustomOrderProperties/OrderProperty[@key='SATISFACTION_SURVEY_CODE']")
    if satisfaction_survey_property is not None:
        satisfaction_survey_code = satisfaction_survey_property.get("value")
        if SATISFACTION_SURVEY_TEXT is None:
            SATISFACTION_SURVEY_TEXT = sysactions.get_storewide_config("Store.GuestSatisfactionSurvey.Text")
    else:
        satisfaction_survey_code = None
    return satisfaction_survey_code


def get_payment_description(mb_context, tender):
    if not PAYMENTS_DESCRIPTION:
        _build_payments_description_cache(mb_context)
        
    tender_id = str(tender.type)
    tender_descr = PAYMENTS_DESCRIPTION[tender_id].get("tender_description")
    parent_tender_id = PAYMENTS_DESCRIPTION[tender_id].get("parent_tender_id")
    if parent_tender_id:
        parent_tender_descr = PAYMENTS_DESCRIPTION[parent_tender_id].get("tender_description")
        tender_descr = "{} {}".format(parent_tender_descr, tender_descr)
    
    return tender_descr


def _build_payments_description_cache(mb_context):
    global PAYMENTS_DESCRIPTION
    
    conn = DBDriver().open(mb_context)
    has_parent_tender_id_on_db = True
    try:
        result = conn.select("SELECT TenderId, TenderDescr, ParentTenderId FROM TenderType")
    except AprDbdException:
        has_parent_tender_id_on_db = False
        result = conn.select("SELECT TenderId, TenderDescr FROM TenderType")
    for row in result:
        tender_id = row.get_entry("TenderId")
        tender_descr = row.get_entry("TenderDescr")
        parent_tender_id = row.get_entry("ParentTenderId") if has_parent_tender_id_on_db else None
        PAYMENTS_DESCRIPTION[tender_id] = {"tender_description": tender_descr, "parent_tender_id": parent_tender_id}


def _build_garena_code(mb_context, order, report):
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


def _format_date(data, mascara="%d/%m/%Y %H:%M:%S"):
    data_emissao_date_utc = data[:19]
    data_emissao_date_utc = datetime.strptime(data_emissao_date_utc, "%Y-%m-%dT%H:%M:%S")
    data_emissao_offset = int(data[20:22]) * 60 + int(data[23:])
    if data[19] == "+":
        data_emissao_offset *= -1
    data_emissao_date_utc = data_emissao_date_utc + timedelta(minutes=data_emissao_offset)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    data_emissao_date = data_emissao_date_utc.replace(tzinfo=from_zone)
    data_emissao_date = data_emissao_date.astimezone(to_zone)
    data_emissao_str = data_emissao_date.strftime(mascara)
    return data_emissao_str


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode('utf8'))).encode('ASCII', 'ignore')


def _translate(model, text, *param):
    return _remove_accents(sysactions.translate_message(model, text, *param))
