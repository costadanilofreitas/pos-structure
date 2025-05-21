# encoding: utf-8

import unittest
import mock

from nfce import NfceAutorizador, NfceRequestBuilder, LoteStatus, LoteException, LoteConsultaStatus
from requests import ConnectionError
from commonmock import NfceRequestMaker
from xml.etree import cElementTree as eTree


class AutorizaNotasTestCase(unittest.TestCase):
    def test_InvalidWsVersion_requestReturned(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 5, 0, 0)

        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.RecebidoComSucesso, "<xml></xml>"))
        nfce_autorizador._busca_recibo = mock.Mock(return_value="12345")
        nfce_autorizador._busca_resposta_do_lote = mock.Mock(return_value=("response_nfce", 0))

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except Exception as ex:
            self.assertEqual(ex.message, "Versão WS Inválida. Parâmetros válidos: 1 e 3")

    def test_EnviaLoteComTentativasException_ExceptionIsThrown(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        raised_exception = Exception("exception_message")
        nfce_autorizador._envia_lote = mock.Mock(side_effect=raised_exception)

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_EnviaLoteReturningServicoParalisadoTemporariamente_ConnectionErrorIsThrown(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        raised_exception = Exception("exception_message")
        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.ServicoParalisadoTemporariamente, "<anyxml></anyxml>"))

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except ConnectionError as ex:
            self.assertEqual(ex.message, "SEFAZ Indisponivel - Status " + LoteStatus.ServicoParalisadoTemporariamente)

    def test_EnviaLoteReturningServicoParalisadoSemPrevisao_ConnectionErrorIsThrown(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        raised_exception = Exception("exception_message")
        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.ServicoParalisadoSemPrevisao, "<anyxml></anyxml>"))

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except ConnectionError as ex:
            self.assertEqual(ex.message, "SEFAZ Indisponivel - Status " + LoteStatus.ServicoParalisadoSemPrevisao)

    def test_EnviaLoteReturningErroInterno_ConnectionErrorIsThrown(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        raised_exception = Exception("exception_message")
        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.ErroInterno, "<anyxml></anyxml>"))

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except ConnectionError as ex:
            self.assertEqual(ex.message, "SEFAZ Indisponivel - Status " + LoteStatus.ErroInterno)

    def test_EnviaLoteReturningAnyOtherError_ConnectionErrorIsThrown(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        raised_exception = Exception("exception_message")
        nfce_autorizador._envia_lote = mock.Mock(return_value=("123", "<anyxml></anyxml>"))

        request = "<nfceRequest></nfceRequest>"

        try:
            nfce_autorizador.autoriza_notas(request, 1)
        except LoteException as ex:
            self.assertEqual(ex.message, "Erro ao enviar lote de NFCe. Codigo: 123")

    def test_ExceptionOnBuscaRecibo_SameExceptionIsRaised(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.RecebidoComSucesso, "<anyxml></anyxml>"))
        raised_exception = Exception("exception_message")
        nfce_autorizador._busca_recibo = mock.Mock(side_effect=raised_exception)

        try:
            request = "<nfceRequest></nfceRequest>"
            nfce_autorizador.autoriza_notas(request, 1)
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_BuscaRespostaDoLoteException_ExceptionIsRaised(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.RecebidoComSucesso, "<anyxml></anyxml>"))
        nfce_autorizador._busca_recibo = mock.Mock(return_value="1234")
        raised_exception = Exception("exception_message")
        nfce_autorizador._busca_resposta_do_lote = mock.Mock(side_effect=raised_exception)

        try:
            request = "<nfceRequest></nfceRequest>"
            nfce_autorizador.autoriza_notas(request, 1)
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_BuscaRespostaDoLoteCorreta_CorrectResponseReturned(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        nfce_autorizador._envia_lote = mock.Mock(return_value=(LoteStatus.RecebidoComSucesso, "<anyxml></anyxml>"))
        nfce_autorizador._busca_recibo = mock.Mock(return_value="1234")
        returned_nfce_response = "<response_nfce></response_nfce>"
        nfce_autorizador._busca_resposta_do_lote = mock.Mock(return_value=(returned_nfce_response, 0))

        request = "<nfceRequest></nfceRequest>"
        returned_request, response, tentativas = nfce_autorizador.autoriza_notas(request, 1)

        self.assertEqual(returned_request, request)
        self.assertEqual(response, returned_nfce_response)
        self.assertEqual(tentativas, 0)


class EnviaLoteComRetentativaTestCase(unittest.TestCase):
    def test_EnviaNfceException_TentadoMaxTentativas999NoneReturned(self):
        raised_exception = Exception("Erro")
        nfce_request = NfceRequestMaker().with_exception(raised_exception).make()
        nfce_autorizador = NfceAutorizador(None, nfce_request, "url_autorizacao", None, 1, 3, 0)

        status_lote, response_str = nfce_autorizador._envia_lote("request")
        self.assertEqual(status_lote, "999")
        self.assertIsNone(response_str)
        nfce_request.envia_nfce.assert_has_calls([mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao")])

    def test_EnviaNfceInvalidResponse_TentadoMaxTentativas999NoneReturned(self):
        invalid_xml = "asdf"

        nfce_request = NfceRequestMaker().with_content(invalid_xml).make()
        nfce_autorizador = NfceAutorizador(None, nfce_request, "url_autorizacao", None, 1, 3, 0)

        status_lote, response_str = nfce_autorizador._envia_lote("request")
        self.assertEqual(status_lote, "999")
        self.assertIsNone(response_str)
        nfce_request.envia_nfce.assert_has_calls([mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao")])

    def test_EnviaNfceTwoErrorsThirdOk_CorrectResponseReturned(self):
        invalid_xml = "asdf"
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao">
                            <retEnviNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <cStat>456</cStat>
                            </retEnviNFe>
                        </nfeAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_request = NfceRequestMaker().with_content_list([invalid_xml, invalid_xml, valid_xml]).make()
        nfce_autorizador = NfceAutorizador(None, nfce_request, "url_autorizacao", None, 1, 3, 0)

        status_lote, response_xml = nfce_autorizador._envia_lote("request")
        self.assertEqual(status_lote, "456")
        self.assertEqual(eTree.tostring(response_xml), eTree.tostring(eTree.XML(valid_xml)))
        nfce_request.envia_nfce.assert_has_calls([mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao"), mock.call("request", "url_autorizacao")])


class BuscaReciboTestCase(unittest.TestCase):
    def test_InvalidXml_ExceptionRaised(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 3, 0)
        invalid_xml = "<xml></xml>"
        try:
            nfce_autorizador._busca_recibo(eTree.XML(invalid_xml))
        except Exception as ex:
            self.assertEqual(ex.message, "Erro ao obter o recibo da NFCe")

    def test_ValidXml_ReciboReturned(self):
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 3, 0)
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                            <Body>
                                <nfeAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao">
                                    <retEnviNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                        <infRec>
                                            <nRec>1234</nRec>
                                        </infRec>
                                    </retEnviNFe>
                                </nfeAutorizacaoLoteResult>
                            </Body>
                        </Envelope>"""

        recibo = nfce_autorizador._busca_recibo(eTree.XML(valid_xml))
        self.assertEqual(recibo, "1234")


class BuscaRespostaDoLoteTestCase(unittest.TestCase):
    def test_MethodCalled_BuildConsultaCalledWithRecibo(self):
        nfce_request_builder = NfceRequestBuilderMaker().build()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, None, None, None, 1, 3, 0)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 5, False)
            self.fail()
        except Exception as ex:
            nfce_request_builder.build_consulta.assert_called_with("1234")

    def test_BuildConsultaException_ExceptionIsRaised(self):
        raised_exception = Exception("exception")
        nfce_request_builder = NfceRequestBuilderMaker().with_exception(raised_exception).build()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, None, None, None, 1, 3, 0)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 5, False)
            self.fail()
        except Exception as ex:
            self.assertEqual(raised_exception, ex)

    def test_EnviaNfceException_MaxRetriesTriedConnectionErrorRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        raised_exception = Exception("exception")
        nfce_request = NfceRequestMaker().with_exception(raised_exception).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except ConnectionError as ce:
            nfce_request.envia_nfce.assert_has_calls([
                mock.call(returnted_xml, "url_ret_autorizacao"),
                mock.call(returnted_xml, "url_ret_autorizacao"),
                mock.call(returnted_xml, "url_ret_autorizacao"),
                mock.call(returnted_xml, "url_ret_autorizacao")])

    def test_InvalidXmlFromSefaz_MaxRetriesTriedConnectionErrorRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "invalid_xml"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except Exception as ex:
            nfce_request.envia_nfce.assert_has_calls([mock.call(returnted_xml, "url_ret_autorizacao"),
                                                      mock.call(returnted_xml, "url_ret_autorizacao"),
                                                      mock.call(returnted_xml, "url_ret_autorizacao"),
                                                      mock.call(returnted_xml, "url_ret_autorizacao")])

    def test_BuscaStatusConsultaException_MaxRetriesTriedConnectionErrorRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        raised_exception = Exception("exception")
        nfce_autorizador._busca_status_consulta = mock.Mock(side_effect=raised_exception)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except ConnectionError as ce:
            call_args_list = nfce_autorizador._busca_status_consulta.call_args_list
            self.assertEqual(len(call_args_list), 4)
            self.assertEqual(eTree.tostring(call_args_list[0][0][0]), eTree.tostring(eTree.XML(resposta_status_lote)))
            self.assertEqual(eTree.tostring(call_args_list[1][0][0]), eTree.tostring(eTree.XML(resposta_status_lote)))
            self.assertEqual(eTree.tostring(call_args_list[2][0][0]), eTree.tostring(eTree.XML(resposta_status_lote)))
            self.assertEqual(eTree.tostring(call_args_list[3][0][0]), eTree.tostring(eTree.XML(resposta_status_lote)))

    def test_BuscaStatusInvalidStatus_LoteExceptionRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        invalid_status_consulta = "456"
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=invalid_status_consulta)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except LoteException as le:
            nfce_autorizador._busca_status_consulta.assert_any_call(mock.ANY)
            eTree.tostring(nfce_autorizador._busca_status_consulta.call_args[0][0]) == "<xml/>"
            self.assertEqual(le.message, "Erro ao consultar status do lote NFCe. Codigo: 456")

    def test_BuscaStatusErrorSchema_LoteExceptionRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        invalid_status_consulta = "225"
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=invalid_status_consulta)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except LoteException as le:
            pass

    def test_BuscaStatusLoteProcessingForever_ConnectionErrorRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=LoteConsultaStatus.LoteEmProcessamento)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except ConnectionError as ce:
            pass

    def test_BuscaStatusLoteProcessadoEnvioLoteTrue_XmlAndTentativasReturned(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=LoteConsultaStatus.LoteProcessado)

        response_xml, tentativas = nfce_autorizador._busca_resposta_do_lote("1234", 4, True)
        self.assertEqual(response_xml, resposta_status_lote)
        self.assertEqual(tentativas, 0)

    def test_BuscaStatusLoteProcessadoEnvioLoteFalseStatusProcessamentoException_ExceptionRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<resposta><status><lote></lote></status></resposta>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=LoteConsultaStatus.LoteProcessado)

        raised_exception = Exception("exception")
        nfce_autorizador._verifica_status_processamento_nfce = mock.Mock(side_effect=raised_exception)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except Exception as ex:
            self.assertEqual(ex, raised_exception)

    def test_BuscaStatusLoteProcessadoEnvioLoteFalseStatusProcessamentoOK_ResponseReturned(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<resposta><status><lote></lote></status></resposta>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)

        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=LoteConsultaStatus.LoteProcessado)
        nfce_autorizador._verifica_status_processamento_nfce = mock.Mock()

        nfce_response_xml, tentativas = nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
        self.assertEqual(nfce_response_xml, "<resposta><status><lote /></status></resposta>")
        self.assertEqual(tentativas, 0)

    def test_BuscaStatusLoteConsumoIndevido_ConnectionErrorRaised(self):
        returnted_xml = "<consulta><lote><xml></xml></lote></consulta>"
        nfce_request_builder = NfceRequestBuilderMaker().with_build_consulta_response_xml(returnted_xml).build()
        resposta_status_lote = "<xml></xml>"
        nfce_request = NfceRequestMaker().with_content(resposta_status_lote).make()

        nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, None, "url_ret_autorizacao", 1, 3, 0)
        nfce_autorizador._busca_status_consulta = mock.Mock(return_value=LoteConsultaStatus.ConsumoIndevido)

        try:
            nfce_autorizador._busca_resposta_do_lote("1234", 4, False)
            self.fail()
        except ConnectionError as ce:
            pass


class BuscaStatusConsultaTestCase(unittest.TestCase):
    def test_InvalidXml_ExceptionRaised(self):
        invalid_xml = "<invalido></invalido>"
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._busca_status_consulta(eTree.XML(invalid_xml))
            self.fail()
        except:
            pass

    def test_InvalidVersaoWsAndResponse_ExceptionRaised(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
            <Body>
                <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao3">
                    <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                        <cStat>1234</cStat>
                    </retConsReciNFe>
                </nfeRetAutorizacaoLoteResult
            </Body>
        </Envelope>"""
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._busca_status_consulta(eTree.XML(valid_xml))
            self.fail()
        except:
            pass

    def test_ValidVersion1XML_cStatReturned(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
            <Body>
                <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                    <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                        <cStat>1234</cStat>
                    </retConsReciNFe>
                </nfeRetAutorizacaoLoteResult>
            </Body>
        </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        status_consulta = nfce_autorizador._busca_status_consulta(eTree.XML(valid_xml))
        self.assertEqual(status_consulta, "1234")

    def test_ValidVersion3XML_cStatReturned(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
            <Body>
                <nfeRetAutorizacaoResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao3">
                    <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                        <cStat>1234</cStat>
                    </retConsReciNFe>
                </nfeRetAutorizacaoResult>
            </Body>
        </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 3, 0, 0)
        status_consulta = nfce_autorizador._busca_status_consulta(eTree.XML(valid_xml))
        self.assertEqual(status_consulta, "1234")


class VerificaStatusProcessamentoNfce(unittest.TestCase):
    def test_InvalidXml_ExceptionRaised(self):
        invalid_xml = "<invalido></invalido>"
        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(invalid_xml))
            self.fail()
        except:
            pass

    def test_NfceAutorizadaVersaoWs1_MethodReturn(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>100</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(valid_xml))

    def test_NfceAutorizadaVersaoWs3_MethodReturn(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao3">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>100</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 3, 0, 0)
        nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(valid_xml))

    def test_ServicoParalisadoTemporariamento_MethodReturn(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>108</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(valid_xml))
            self.fail()
        except ConnectionError as ce:
            self.assertEqual(ce.message, "SEFAZ Indisponivel - Entrando em Contingencia - Status: 108")

    def test_ServicoParalisadoSemPrevisao_MethodReturn(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>109</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(valid_xml))
            self.fail()
        except ConnectionError as ce:
            self.assertEqual(ce.message, "SEFAZ Indisponivel - Entrando em Contingencia - Status: 109")

    def test_ErroInterno_ConnectionErrorRaised(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>999</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            nfce_autorizador._verifica_status_processamento_nfce(eTree.XML(valid_xml))
            self.fail()
        except ConnectionError as ce:
            self.assertEqual(ce.message, "SEFAZ Indisponivel - Entrando em Contingencia - Status: 999")

    def test_DuplicidadeNfce_DuplicidadeNfceExceptionRaised(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>204</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)

        input_xml = eTree.XML(valid_xml)
        nfce_autorizador._verifica_status_processamento_nfce(input_xml)

    def test_OutrosErros_ExceptionRaised(self):
        valid_xml = """<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
                    <Body>
                        <nfeRetAutorizacaoLoteResult xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
                            <retConsReciNFe xmlns="http://www.portalfiscal.inf.br/nfe">
                                <protNFe>
                                    <infProt>
                                        <cStat>555</cStat>
                                    </infProt>
                                </protNFe>
                            </retConsReciNFe>
                        </nfeRetAutorizacaoLoteResult>
                    </Body>
                </Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        try:
            input_xml = eTree.XML(valid_xml)
            nfce_autorizador._verifica_status_processamento_nfce(input_xml)
            self.fail()
        except Exception as ex:
            self.assertEqual(ex.message, "NFCe Nao Autorizada. Status: 555")


class VerificaMesmaNotaTestCase(unittest.TestCase):
    def test_sameNotaEnviadaVersion1_TrueReturned(self):
        valid_xml = """<ns0:Envelope xmlns="http://www.portalfiscal.inf.br/nfe" xmlns:ns0="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
    	<ns0:Body>
    		<ns1:nfeRetAutorizacaoLoteResult>
    			<retConsReciNFe versao="3.10">
    				<tpAmb>1</tpAmb>
    				<verAplic>AM3.10</verAplic>
    				<nRec>130003365890573</nRec>
    				<cStat>104</cStat>
    				<xMotivo>Lote processado</xMotivo>
    				<cUF>13</cUF>
    				<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    				<protNFe versao="3.10">
    					<infProt>
    						<tpAmb>1</tpAmb>
    						<verAplic>AM3.10</verAplic>
    						<chNFe>13170526277931000397650010000002961496751015</chNFe>
    						<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    						<cStat>539</cStat>
    						<xMotivo>Rejeicao: Duplicidade de NF-e, com diferenca na chave de acesso [chNFe: 13170526277931000397650010000002961496751015][nRec: 130003267863753]</xMotivo>
    					</infProt>
    				</protNFe>
    			</retConsReciNFe>
    		</ns1:nfeRetAutorizacaoLoteResult>
    	</ns0:Body>
    </ns0:Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        ret = nfce_autorizador._verifica_mesma_nota(eTree.XML(valid_xml))

        self.assertTrue(ret)

    def test_sameNotaEnviadaVersion3_TrueReturned(self):
        valid_xml = """<ns0:Envelope xmlns="http://www.portalfiscal.inf.br/nfe" xmlns:ns0="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao3">
    	<ns0:Body>
    		<ns1:nfeRetAutorizacaoLoteResult>
    			<retConsReciNFe versao="3.10">
    				<tpAmb>1</tpAmb>
    				<verAplic>AM3.10</verAplic>
    				<nRec>130003365890573</nRec>
    				<cStat>104</cStat>
    				<xMotivo>Lote processado</xMotivo>
    				<cUF>13</cUF>
    				<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    				<protNFe versao="3.10">
    					<infProt>
    						<tpAmb>1</tpAmb>
    						<verAplic>AM3.10</verAplic>
    						<chNFe>13170526277931000397650010000002961496751015</chNFe>
    						<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    						<cStat>539</cStat>
    						<xMotivo>Rejeicao: Duplicidade de NF-e, com diferenca na chave de acesso [chNFe: 13170526277931000397650010000002961496751015][nRec: 130003267863753]</xMotivo>
    					</infProt>
    				</protNFe>
    			</retConsReciNFe>
    		</ns1:nfeRetAutorizacaoLoteResult>
    	</ns0:Body>
    </ns0:Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 3, 0, 0)
        ret = nfce_autorizador._verifica_mesma_nota(eTree.XML(valid_xml))

        self.assertTrue(ret)
        
    def test_differentNotaEnviadaVersion1_TrueReturned(self):
        valid_xml = """<ns0:Envelope xmlns="http://www.portalfiscal.inf.br/nfe" xmlns:ns0="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">
    	<ns0:Body>
    		<ns1:nfeRetAutorizacaoLoteResult>
    			<retConsReciNFe versao="3.10">
    				<tpAmb>1</tpAmb>
    				<verAplic>AM3.10</verAplic>
    				<nRec>130003365890573</nRec>
    				<cStat>104</cStat>
    				<xMotivo>Lote processado</xMotivo>
    				<cUF>13</cUF>
    				<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    				<protNFe versao="3.10">
    					<infProt>
    						<tpAmb>1</tpAmb>
    						<verAplic>AM3.10</verAplic>
    						<chNFe>13170526277931000397650010000002961496751015</chNFe>
    						<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    						<cStat>539</cStat>
    						<xMotivo>Rejeicao: Duplicidade de NF-e, com diferenca na chave de acesso [chNFe: 13170526277931000397650010000002961496751014][nRec: 130003267863753]</xMotivo>
    					</infProt>
    				</protNFe>
    			</retConsReciNFe>
    		</ns1:nfeRetAutorizacaoLoteResult>
    	</ns0:Body>
    </ns0:Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        ret = nfce_autorizador._verifica_mesma_nota(eTree.XML(valid_xml))

        self.assertFalse(ret)

    def test_differentNotaEnviadaVersion3_TrueReturned(self):
        valid_xml = """<ns0:Envelope xmlns="http://www.portalfiscal.inf.br/nfe" xmlns:ns0="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao3">
    	<ns0:Body>
    		<ns1:nfeRetAutorizacaoLoteResult>
    			<retConsReciNFe versao="3.10">
    				<tpAmb>1</tpAmb>
    				<verAplic>AM3.10</verAplic>
    				<nRec>130003365890573</nRec>
    				<cStat>104</cStat>
    				<xMotivo>Lote processado</xMotivo>
    				<cUF>13</cUF>
    				<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    				<protNFe versao="3.10">
    					<infProt>
    						<tpAmb>1</tpAmb>
    						<verAplic>AM3.10</verAplic>
    						<chNFe>13170526277931000397650010000002961496751015</chNFe>
    						<dhRecbto>2017-05-31T20:24:17-04:00</dhRecbto>
    						<cStat>539</cStat>
    						<xMotivo>Rejeicao: Duplicidade de NF-e, com diferenca na chave de acesso [chNFe: 13170526277931000397650010000002961496751014][nRec: 130003267863753]</xMotivo>
    					</infProt>
    				</protNFe>
    			</retConsReciNFe>
    		</ns1:nfeRetAutorizacaoLoteResult>
    	</ns0:Body>
    </ns0:Envelope>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 3, 0, 0)
        ret = nfce_autorizador._verifica_mesma_nota(eTree.XML(valid_xml))

        self.assertFalse(ret)

    def test_InvalidXml_FalseReturned(self):
        invalid_xml = """<invalid></invalid>"""

        nfce_autorizador = NfceAutorizador(None, None, None, None, 1, 0, 0)
        ret = nfce_autorizador._verifica_mesma_nota(eTree.XML(invalid_xml))

        self.assertFalse(ret)


class NfceRequestBuilderMaker(object):
    def __init__(self):
        self.build_consulta_response_xml = None
        self.exception = None

    def with_build_consulta_response_xml(self, build_consulta_response_xml):
        # type: (str) -> NfceRequestBuilderMaker
        self.build_consulta_response_xml = build_consulta_response_xml
        return self

    def with_exception(self, exception):
        self.exception = exception
        return self

    def build(self):
        # type: () -> NfceRequestBuilder
        nfce_request_builder = mock.NonCallableMagicMock(spec=NfceRequestBuilder)

        if self.exception is not None:
            nfce_request_builder.build_consulta = mock.Mock(side_effect=self.exception)
        else:
            nfce_request_builder.build_consulta = mock.Mock(return_value=self.build_consulta_response_xml)

        return nfce_request_builder
