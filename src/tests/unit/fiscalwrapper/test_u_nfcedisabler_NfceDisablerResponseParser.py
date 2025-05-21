import unittest
import os
from nfcedisabler import NfceDisablerResponseParser, NfceDisablerResponseParserException


class NfceDisablerResponseParser_ParseResponse(unittest.TestCase):
    def test_invalidXml_NfceDisablerResponseParserException(self):
        input_xml = "asdfasdf"

        nfce_disabler_response_parser = NfceDisablerResponseParser()

        try:
            nfce_disabler_response_parser.parse_response(input_xml)
            self.fail("An exception should have been trhown")
        except NfceDisablerResponseParserException as ex:
            pass

    def test_validXml_correctNfceDisablerResponseReturned(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        input_xml_file_path = current_directory + "\\data\\NfceDisablerResponseParser\\valid.xml"

        with open(input_xml_file_path, "rb") as input_xml_file:
            input_xml = input_xml_file.read()

        nfce_disabler_response_parser = NfceDisablerResponseParser()
        nfce_disabler_response = nfce_disabler_response_parser.parse_response(input_xml)
        self.assertEqual(nfce_disabler_response.c_stat, "102")
        self.assertEqual(nfce_disabler_response.x_motivo, "Inutilizacao de numero homologado")
        self.assertEqual(nfce_disabler_response.n_prot, "143170000343346")


