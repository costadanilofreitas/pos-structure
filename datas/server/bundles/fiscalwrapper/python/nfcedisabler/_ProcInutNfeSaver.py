# -*- coding: utf-8 -*-

import os
from xml.etree import cElementTree as eTree

import iso8601


class ProcInutNfeSaver(object):
    def __init__(self, xmls_base_path):
        self.xmls_base_path = xmls_base_path

    def save_proc_inut_nfe_xml(self, xml, order):
        # type: (str, eTree.ElementTree) -> None
        canceled_date_str = order.find("StateHistory/State[@state='VOIDED']").get("timestamp")
        canceled_date = iso8601.parse_date(canceled_date_str)
        order_id = order.get("orderId").zfill(9)

        proc_inut_nfe_xml = eTree.XML(xml)
        serie = proc_inut_nfe_xml.find("{{{0}}}inutNFe/{{{0}}}infInut/{{{0}}}serie".format("http://www.portalfiscal.inf.br/nfe")).text.zfill(3)
        fiscal_number = proc_inut_nfe_xml.find("{{{0}}}inutNFe/{{{0}}}infInut/{{{0}}}nNFIni".format("http://www.portalfiscal.inf.br/nfe")).text.zfill(9)
        file_name = "{0}_{1}_{2}_procInutNfe.xml".format(serie, fiscal_number, order_id)

        save_dir = os.path.join(self.xmls_base_path, "Enviados", canceled_date.strftime("%Y"), canceled_date.strftime("%m"), canceled_date.strftime("%d"))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(save_dir, file_name)

        with open(save_path, mode="w") as proc_inut_nfe_file:
            proc_inut_nfe_file.write(xml)

    def save_proc_inut_nfe_xml_error(self, xml, order):
        # type: (str, eTree.ElementTree) -> None
        canceled_date_str = order.find("StateHistory/State[@state='VOIDED']").get("timestamp")
        canceled_date = iso8601.parse_date(canceled_date_str)
        order_id = order.get("orderId").zfill(9)

        proc_inut_nfe_xml = eTree.XML(xml)
        serie = proc_inut_nfe_xml.find("{{{0}}}inutNFe/{{{0}}}infInut/{{{0}}}serie".format("http://www.portalfiscal.inf.br/nfe")).text.zfill(3)
        fiscal_number = proc_inut_nfe_xml.find("{{{0}}}inutNFe/{{{0}}}infInut/{{{0}}}nNFIni".format("http://www.portalfiscal.inf.br/nfe")).text.zfill(9)
        file_name = "{0}_{1}_{2}_procInutNfe.xml".format(serie, fiscal_number, order_id)

        save_dir = os.path.join(self.xmls_base_path, "Erros")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_path = os.path.join(save_dir, file_name)

        with open(save_path, mode="w") as proc_inut_nfe_file:
            proc_inut_nfe_file.write(xml)
