# -*- coding: utf-8 -*-
import unittest
from nfceutil import XmlEnveloper

class XmlEnveloperTest(unittest.TestCase):
    def test_xmlIsCorrectlyEnveloped(self):
        input_xml = "<a>a</a>"
        web_service_namespace = "http://namescape.web.service.com/Path/Namespace"
        c_uf = 43

        xml_enveloper = XmlEnveloper(c_uf)

        xml_envoloped = xml_enveloper.envelop(input_xml, web_service_namespace)

        expected_output = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/"><Header><nfeCabecMsg xmlns="http://namescape.web.service.com/Path/Namespace"><cUF>43</cUF><versaoDados>3.10</versaoDados></nfeCabecMsg></Header><Body><nfeDadosMsg xmlns="http://namescape.web.service.com/Path/Namespace"><a>a</a></nfeDadosMsg></Body></Envelope>"""

        self.assertEqual(expected_output, xml_envoloped)
