# -*- coding: utf-8 -*-
import unittest
import os

from nfceutil import NfceSigner
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NfceSignerTest(unittest.TestCase):
    def test_xmlCorrectlySigned(self):
        input_xml = """<inutNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="3.10"><infInut Id='ID43171357459404430465001000003950000003950'><tpAmb>2</tpAmb><xServ>INUTILIZAR</xServ><cUF>43</cUF><ano>17</ano><CNPJ>13574594044304</CNPJ><mod>65</mod><serie>1</serie><nNFIni>3950</nNFIni><nNFFin>3950</nNFFin><xJust>Pedido cancelado</xJust></infInut></inutNFe>"""

        current_directory = os.path.dirname(os.path.realpath(__file__))

        nfce_signer = NfceSigner(current_directory + "\\cert.key", current_directory +  "\\cert.pem")

        signed_xml = nfce_signer.sign_xml(input_xml, "infInut", "Id")

        self._assertXmlIsSignedAndValid(signed_xml)

    def _assertXmlIsSignedAndValid(self, signed_xml):
        chrome = webdriver.Chrome()
        try:
            chrome.get("https://www.sefaz.rs.gov.br/nfe/nfe-val.aspx")

            txtxml = chrome.find_element_by_id("txtxml")
            txtxml.send_keys(signed_xml)

            btnvalidar = chrome.find_element_by_id("btnvalidar")
            btnvalidar.click()

            WebDriverWait(chrome, 120).until(EC.presence_of_element_located((By.ID, "resultado")))

            try:
                error_span = chrome.find_element_by_css_selector("span.erroSchema2")
                self.fail(error_span.text)
            except NoSuchElementException:
                pass
        finally:
            chrome.close()




