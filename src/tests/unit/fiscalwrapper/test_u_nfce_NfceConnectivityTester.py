import unittest
from commonmock import NfceRequestMaker
from nfce import NfceConnectivityTester


class TestConnectivityTestCase(unittest.TestCase):
    def test_NoErrors_CorrectXmlSentToEnviaNfce(self):
        nfce_request = NfceRequestMaker().make()

        nfce_connectivity_tester = NfceConnectivityTester(nfce_request, "url_status_servico", "RJ")

        nfce_connectivity_tester.test_connectivity()

        expected_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">""" \
                           "<Header>" \
                             """<nfeCabecMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeStatusServico2">""" \
                                    "<cUF>RJ</cUF>" \
                                    "<versaoDados>3.10</versaoDados>" \
                                "</nfeCabecMsg>" \
                            "</Header>" \
                            "<Body>" \
                                """<nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeStatusServico2">""" \
                                    """<enviNFe versao="3.10" xmlns="http://www.portalfiscal.inf.br/nfe"></enviNFe>""" \
                                "</nfeDadosMsg>" \
                            "</Body>" \
                       "</Envelope>"


        nfce_request.envia_nfce.assert_called_with(expected_xml, "url_status_servico")

    def test_NoErrors_TrueReturned(self):
        nfce_request = NfceRequestMaker().make()

        nfce_connectivity_tester = NfceConnectivityTester(nfce_request, "url_status_servico", "RJ")

        ret = nfce_connectivity_tester.test_connectivity()
        self.assertTrue(ret)

    def test_InvalidResponseCodeFromSefaz_FalseReturned(self):
        nfce_request = NfceRequestMaker().with_status_code(500).make()

        nfce_connectivity_tester = NfceConnectivityTester(nfce_request, "url_status_servico", "RJ")

        ret = nfce_connectivity_tester.test_connectivity()
        self.assertFalse(ret)

    def test_ExceptionFromSefaz_FalseReturned(self):
        raised_exception = Exception("exception")
        nfce_request = NfceRequestMaker().with_exception(raised_exception).make()

        nfce_connectivity_tester = NfceConnectivityTester(nfce_request, "url_status_servico", "RJ")

        ret = nfce_connectivity_tester.test_connectivity()
        self.assertFalse(ret)
