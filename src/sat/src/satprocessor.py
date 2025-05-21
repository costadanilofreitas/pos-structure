# -*- coding: utf-8 -*-
import threading
import time
import ctypes
import pyscripts
import persistence
import os
import random
import base64
import re
import ast
import platform
import logging

from msgbus import MBMessage, FM_STRING
from datetime import datetime
from shutil import move, copyfile
from threading import Thread, Condition
from xml.etree import cElementTree as eTree
from typing import Optional

MAX_RETRIES_ERROR_TRY_AGAIN = "ERROR - Max retries reached - %d - Coping again"
ERROR_CODE_NOT_FOUND = "ERROR - Response code not found"

logger = logging.getLogger("SatProcessor")


class SatProcessor(object):
    def __init__(self):
        return

    def is_active(self):
        raise NotImplementedError()

    def process_sat(self, msg):
        raise NotImplementedError()

    def status_operacional(self, msg):
        raise NotImplementedError()

    def process_payment(self, msg):
        raise NotImplementedError()

    def payment_status(self, msg):
        raise NotImplementedError()

    def process_cancel(self, msg):
        raise NotImplementedError()

    def cancel_sale(self, msg):
        raise NotImplementedError()


class FakeSatProcessor(SatProcessor):
    def __init__(self, active_delay, process_delay, is_mfe):
        super(FakeSatProcessor, self).__init__()
        self.active_delay = active_delay
        self.process_delay = process_delay
        self.is_mfe = is_mfe

    def is_active(self):
        # type: () -> str
        time.sleep(self.active_delay)
        return "OK"

    def process_payment(self, msg):
        # type: (MBMessage) -> str
        time.sleep(self.active_delay)
        return "123"

    def payment_status(self, msg):
        # type: (MBMessage) -> str
        time.sleep(self.active_delay)
        return "OK - 123"

    def process_cancel(self, msg):
        # type: (MBMessage) -> str
        time.sleep(self.active_delay)
        return "OK - 456"

    def status_operacional(self, msg):
        # type: (MBMessage) -> str
        time.sleep(self.active_delay)
        return "000123|10000|Resposta com Sucesso.|||900009331|IPFIX|010.200.024.104|02:01:00:00:93:31|255.255.255.000|010.200.024.254|008.008.008.008|008.008.004.004|CONECTADO|ALTO|1 Gbyte|0 Mbytes|20170202120414|01.03.00|00.07|35170261099008000141599000093310000779904668|35161261099008000141599000093310000759260693|35170261099008000141599000093310000779904668|20161213164209|20161214084712|20160817|20210816|0"

    def process_sat(self, msg):
        # type: (MBMessage) -> str
        time.sleep(self.process_delay)
        pos_id, order_id, data = msg.data.split('\0')
        now = datetime.now()
        xml_request = """
        <CFe><infCFe Id="CFe35161061099008000141599000042070004696565921" versao="0.06" versaoDadosEnt="0.06" versaoSB="010100"><ide><cUF>35</cUF><cNF>656592</cNF><mod>59</mod><nserieSAT>900004207</nserieSAT><nCFe>%s</nCFe><dEmi>%s</dEmi><hEmi>%s</hEmi><cDV>1</cDV><tpAmb>2</tpAmb><CNPJ>16716114000172</CNPJ><signAC>SGR-SAT SISTEMA DE GESTAO E RETAGUARDA DO SAT</signAC><assinaturaQRCODE>Q4sUXX+Mu8tc+hryAaOVEtoSQUO3k/naoypf5lbZfWhFeQPC8sjSW5cZSvKZH1woU0qk2f2reYLEaYjF+Qa9MurqjlxZbleXZ04LhX8XB3WxlUP0ouL2MNNyIMirCsuKedvEQ87w8LzVx4s+Co6b2aLCc3slnrYDbEkz45TKJo6qwqIow+X7Nggk26aqnAPi1CGuW2ism8Utyf3fN8gPyI5N2Pam62hu7gucMczOKAv5Wawd+F8pE3lOOdnxWbuzxplES+HqQjrczqTrvRUmNqOVjscvXKPCBkngYyEGxmuxP9pUpWAGv893S2ucmH5cOx2TTLczK0/oKRlrgTgsGg==</assinaturaQRCODE><numeroCaixa>001</numeroCaixa></ide><emit><CNPJ>61099008000141</CNPJ><xNome>DIMAS DE MELO PIMENTA SISTEMAS DE PONTO E ACESSO LTDA</xNome><xFant>DIMEP</xFant><enderEmit><xLgr>AVENIDA MOFARREJ</xLgr><nro>840</nro><xCpl>908</xCpl><xBairro>VL. LEOPOLDINA</xBairro><xMun>SAO PAULO</xMun><CEP>05311000</CEP></enderEmit><IE>111111111111</IE><cRegTrib>3</cRegTrib><cRegTribISSQN>1</cRegTribISSQN><indRatISSQN>N</indRatISSQN></emit><dest></dest><det nItem="1"><prod><cProd>1050</cProd><xProd>Whopper/Q</xProd><CFOP>5000</CFOP><uCom>un</uCom><qCom>1.0000</qCom><vUnCom>9.000</vUnCom><vProd>9.00</vProd><indRegra>A</indRegra><vItem>9.00</vItem><obsFiscoDet xCampoDet="Cod.NCM"><xTextoDet>19022000</xTextoDet></obsFiscoDet></prod><imposto><ICMS><ICMS00><Orig>0</Orig><CST>00</CST><pICMS>3.20</pICMS><vICMS>0.29</vICMS></ICMS00></ICMS><PIS><PISAliq><CST>01</CST><vBC>9.00</vBC><pPIS>1.6500</pPIS><vPIS>14.85</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vBC>9.00</vBC><pCOFINS>7.6000</pCOFINS><vCOFINS>68.40</vCOFINS></COFINSAliq></COFINS></imposto></det><det nItem="2"><prod><cProd>6012</cProd><xProd>MD Batata</xProd><CFOP>5000</CFOP><uCom>un</uCom><qCom>1.0000</qCom><vUnCom>3.000</vUnCom><vProd>3.00</vProd><indRegra>A</indRegra><vItem>3.00</vItem><obsFiscoDet xCampoDet="Cod.NCM"><xTextoDet>20052000</xTextoDet></obsFiscoDet></prod><imposto><ICMS><ICMS00><Orig>0</Orig><CST>00</CST><pICMS>3.20</pICMS><vICMS>0.10</vICMS></ICMS00></ICMS><PIS><PISAliq><CST>01</CST><vBC>3.00</vBC><pPIS>1.6500</pPIS><vPIS>4.95</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vBC>3.00</vBC><pCOFINS>7.6000</pCOFINS><vCOFINS>22.80</vCOFINS></COFINSAliq></COFINS></imposto></det><det nItem="3"><prod><cProd>9008</cProd><xProd>Free Refill</xProd><CFOP>5000</CFOP><uCom>un</uCom><qCom>1.0000</qCom><vUnCom>10.900</vUnCom><vProd>10.90</vProd><indRegra>A</indRegra><vItem>10.90</vItem><obsFiscoDet xCampoDet="Cod.NCM"><xTextoDet>21069010</xTextoDet></obsFiscoDet><obsFiscoDet xCampoDet="Cod.CEST"><xTextoDet>300300</xTextoDet></obsFiscoDet></prod><imposto><ICMS><ICMS00><Orig>0</Orig><CST>00</CST><pICMS>0.00</pICMS><vICMS>0.00</vICMS></ICMS00></ICMS><PIS><PISAliq><CST>01</CST><vBC>10.90</vBC><pPIS>1.6500</pPIS><vPIS>17.98</vPIS></PISAliq></PIS><COFINS><COFINSAliq><CST>01</CST><vBC>10.90</vBC><pCOFINS>7.6000</pCOFINS><vCOFINS>82.84</vCOFINS></COFINSAliq></COFINS></imposto></det><total><ICMSTot><vICMS>0.39</vICMS><vProd>22.90</vProd><vDesc>0.00</vDesc><vPIS>37.78</vPIS><vCOFINS>174.04</vCOFINS><vPISST>0.00</vPISST><vCOFINSST>0.00</vCOFINSST><vOutro>0.00</vOutro></ICMSTot><vCFe>22.90</vCFe></total><pgto><MP><cMP>01</cMP><vMP>22.90</vMP></MP><vTroco>0.00</vTroco></pgto></infCFe><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></SignatureMethod><Reference URI="#CFe35161061099008000141599000042070004696565921"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></Transform><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></DigestMethod><DigestValue>dGPF79k+cvGp6EPgKc0Tt+9NhiVIY+CQWDvyAtDm4F8=</DigestValue></Reference></SignedInfo><SignatureValue>Wb3HtTGTK0GiXFio+Vi1x3H1gx29hL9/A/Yc7Wsd6NW4Z7tyPE/j0CB8TvZPl/b5uNuoq/NhjkYROLpcEP4+J7EkoEzGKsW03sCg/4/SHjJuJaAxnepYkMjirZNo8TdrWlOxU88WO6qsFVD1RKe9RzOD7pama6u6geWOK2l5o6LDiWcEwhexmjf5nbe3WkQG0KgKORvVIhhIOkzIb8yQrzKv8l55FYTfx1OHDzgDNyS6jFusWlW2Jh622l417nksocfA0x37/Q7sE7cpyN2ObEKWdyG6kMdDlP+meS5ANhlGh5zf4Y3L4oWcZmwrz0CSJqbpC8knmyaqyUpn4Xx/9g==</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIGyTCCBLGgAwIBAgIJARzkDhhHufRyMA0GCSqGSIb3DQEBCwUAMGcxCzAJBgNVBAYTAkJSMTUwMwYDVQQKEyxTZWNyZXRhcmlhIGRhIEZhemVuZGEgZG8gRXN0YWRvIGRlIFNhbyBQYXVsbzEhMB8GA1UEAxMYQUMgU0FUIGRlIFRlc3RlIFNFRkFaIFNQMB4XDTE1MDcwODIwMDI1MVoXDTIwMDcwODIwMDI1MVowgc4xEjAQBgNVBAUTCTkwMDAwNDIwNzELMAkGA1UEBhMCQlIxEjAQBgNVBAgTCVNhbyBQYXVsbzERMA8GA1UEChMIU0VGQVotU1AxDzANBgNVBAsTBkFDLVNBVDEoMCYGA1UECxMfQXV0ZW50aWNhZG8gcG9yIEFSIFNFRkFaIFNQIFNBVDFJMEcGA1UEAxNARElNQVMgREUgTUVMTyBQSU1FTlRBIFNJU1RFTUFTIERFIFBPTlRPIEUgQUNFU1NPIDo2MTA5OTAwODAwMDE0MTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAIuYfJYn/Pv38cdb10F996Yw3fCIOmjEr9ExvPxIdEY1lFcpbOfDNOnfYboL0Ts//PsrxeIPJlDsvQ0L46wpHDNpFfBDqxydBV4rF+VIOlvu6bvz+DPGv9nqTTG2WMyXKv5aueLcYyVdu24npM7Wedd0Nh6ABI86/jjvZGRQKtKbst+4ZWtVIFtQOiTtHhWNpL1un+Z+v0H8tjOFHn+sz19LpVhWSHnBHTpeEAquwgvkaWw3esPjyLPZe/fvriCl7SZOMDPYpWNzyW98r/5NbmO5tsBgxFfGpCbbsjNPNxnUmfwVWX30K1ZLYFgsgzgByfyxR2lcAfgeg6Fd5iu0E2ECAwEAAaOCAg4wggIKMA4GA1UdDwEB/wQEAwIF4DB7BgNVHSAEdDByMHAGCSsGAQQBgewtAzBjMGEGCCsGAQUFBwIBFlVodHRwOi8vYWNzYXQuaW1wcmVuc2FvZmljaWFsLmNvbS5ici9yZXBvc2l0b3Jpby9kcGMvYWNzYXRzZWZhenNwL2RwY19hY3NhdHNlZmF6c3AucGRmMGsGA1UdHwRkMGIwYKBeoFyGWmh0dHA6Ly9hY3NhdC10ZXN0ZS5pbXByZW5zYW9maWNpYWwuY29tLmJyL3JlcG9zaXRvcmlvL2xjci9hY3NhdHNlZmF6c3AvYWNzYXRzZWZhenNwY3JsLmNybDCBpgYIKwYBBQUHAQEEgZkwgZYwNAYIKwYBBQUHMAGGKGh0dHA6Ly9vY3NwLXBpbG90LmltcHJlbnNhb2ZpY2lhbC5jb20uYnIwXgYIKwYBBQUHMAKGUmh0dHA6Ly9hY3NhdC10ZXN0ZS5pbXByZW5zYW9maWNpYWwuY29tLmJyL3JlcG9zaXRvcmlvL2NlcnRpZmljYWRvcy9hY3NhdC10ZXN0ZS5wN2MwEwYDVR0lBAwwCgYIKwYBBQUHAwIwCQYDVR0TBAIwADAkBgNVHREEHTAboBkGBWBMAQMDoBAEDjYxMDk5MDA4MDAwMTQxMB8GA1UdIwQYMBaAFI45QQBc8rgF2qhtmLkBRm1uY98CMA0GCSqGSIb3DQEBCwUAA4ICAQCVZ9RW9moj0r+61w+uv23vhoJ/EmUnynuz9qRYODxdPiYFq+9DFNa1weplzSfz2nPFlIe253VgjUvUNmOUvd+WH0GVDTM4uiBWY/rlhdqRe/mA6RQyTlcFeqa/3Kw8F6Zsa1Ztv2GDnOJSKvEWq+W8kGIyc1wHMKK4DeAjnYGa+CIZvR702/IARcJJex3PCnelPGz3TrIReMd4SSEcb95zHaYxVocA8CpbZSHkxc5wJICVSoRDvwe9zzwffOQNrwWo4Ow6gdA5wMpCHGvQ7O3UggZIrrU3JJXYJOaSnWYOjZwk3fNY7Oa9EpEbzOjp5CSDqwjNwTqzj3upL9ujXDzK2VIphEcqq8fpF7b2c2WDKYlk7vWYnjwHfkT+N3NJPv0/pupfs5Pxj9tlQjmo3IpdD5myd074htVk++tJ/T3gq4UAnPCs17VN+5yXq54ak9KFfHlVffJKNycdUqKBHvq5T3gYFtU24IgMD9pIo6kDHd2/k+AYKGm/rStsDWbf6xwkTkC4rRTZU9bA4MhAUcj3E2sxqHnjF2y7yjPwBYiSQkOddZbIhCkjBGH8SW4DBN9k/Wc028/r4ZmfoAsc+hMHYznXH9xGwZDC6IitqbY/aEbvZlJbRoptZ+NjJaKhqaq6Tkb80Cq8wsF6e5SzqndT9xqID529IziVUsmOZslrGw==</X509Certificate></X509Data></KeyInfo></Signature></CFe>
        """ % (order_id, now.strftime('%Y%m%d'), now.strftime('%H%M%S'))
        return """
                <SatResponse>
                    <FiscalData>
                        <datetime>13/02/2016 15:00</datetime>
                        <satno>000.000.000</satno>
                        <satkey>11111111111111111111111111111111111111111111</satkey>
                        <CustomerCPF></CustomerCPF>
                        <QRCode>FakeSATQRCode</QRCode>
                    </FiscalData>
                    <XmlRequest>%s</XmlRequest>
                </SatResponse>""" % base64.b64encode(xml_request)

    def cancel_sale(self, msg):
            message = "Venda cancelada com sucesso."
            return """
                            <SatCancelResponse>
                                <Message>%s</Message>
                                <XmlResponse></XmlResponse>
                            </SatCancelResponse>""" % (message)


class SatSynchProcessor(SatProcessor):
    def __init__(self, sat_act_key, module_directory, is_mfe, integrador_inputdir=None, integrador_outputdir=None, temp_dir=None,
                 error_dir=None, chave_acesso_validador=None, chave_requisicao=None, estabelecimento=None, cnpj=None, icms_base=None,
                 max_retries=30):
        # type: (str, str) -> None
        super(SatSynchProcessor, self).__init__()

        self.sat_act_key = str(sat_act_key)
        self.sat_no = None
        self.lock = threading.Lock()
        self.module_directory = module_directory
        self.active = False
        self.cancelar_ultima_venda = None

        self.is_mfe = is_mfe
        self.integrador_inputdir = integrador_inputdir
        self.integrador_outputdir = integrador_outputdir
        self.temp_dir = temp_dir
        self.error_dir = error_dir
        self.chave_acesso_validador = chave_acesso_validador
        self.chave_requisicao = chave_requisicao
        self.estabelecimento = estabelecimento
        self.cnpj = cnpj
        self.max_retries = int(max_retries)
        self.icms_base = icms_base
        self.payment_map = {}
        self.last_cfe_map = {}

        self.consultar_sat = None
        self.consultar_status_operacional = None
        self.enviar_dados_venda = None

        self.init_thread = None  # type: Thread
        self.init_thread_condition = Condition()
        self.init_thread_running = False

        self.sat_dll = None

        if self.is_mfe:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            if not os.path.exists(self.error_dir):
                os.makedirs(self.error_dir)
        else:
            sat_dll = "{BUNDLEDIR}/dll/"
            for var in re.findall("{[a-zA-Z0-9]*}+", sat_dll):
                sat_dll = sat_dll.replace(var, os.environ.get(var.replace('{', '').replace('}', ''), ""))

            self.manufacturers = [name for name in os.listdir(sat_dll) if os.path.isdir(os.path.join(sat_dll, name))]
            self.start_init_thread()

    def is_active(self):
        # type: () -> str
        with self.lock:
            if self.is_mfe:
                out = self._consultar_mfe(random.randint(1, 999999))
            else:
                out = self.consultar_sat(random.randint(1, 999999))

            if out.startswith("ERROR"):
                return "ERROR"

            splitted = out.split('|')
            if len(splitted) > 1:
                if "08000" in splitted[1]:
                    return "OK"
                elif "08098" in splitted[1]:
                    return "Em Processamento"

            return "ERROR"

    def process_payment(self, msg):
        # type: (MBMessage) -> str
        logger.debug("ENTRANDO process_payment")
        if not self.is_mfe:
            return "OK"

        with self.lock:
            logger.debug("LOCK OBTIDO process_payment")
            # Obtem parametros do pagamento
            posid, orderid, tender_seq_id, payment_amt, order_amt = msg.data.split("\0")
            # posid, orderid, tender_seq_id, payment_amt, order_amt = '1', '2', '0', '1', '5'
            # Cria XML
            payment_data = self._create_payment_xml(posid, tender_seq_id, payment_amt, order_amt)
            # Salva no diretorio
            today = datetime.now().strftime("%Y%m%d")
            now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
            temp_path = os.path.join(self.temp_dir, today, "payment_request_%s.xml" % now)
            temp_path2 = os.path.join(self.temp_dir, today, "payment_request2_%s.xml" % now)
            self.send_file_to_process(payment_data, temp_path, temp_path2, today)

            payment_id = None
            # Loop para verificar se pagamento enviado
            for i in xrange(1, self.max_retries, 1):
                files = os.listdir(self.integrador_outputdir)
                if not len(files):
                    if not i % 5:
                        logger.debug(MAX_RETRIES_ERROR_TRY_AGAIN % i)
                        self._clear_input_dir()
                        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                        temp_path2 = os.path.join(self.temp_dir, "payment_request2_%s.xml" % now)
                        copyfile(temp_path, temp_path2)
                        move(temp_path2, self.integrador_inputdir)
                    time.sleep(1)
                else:
                    output_file = None
                    try:
                        output_file = os.path.join(self.integrador_outputdir, files[0])
                        with file(output_file) as f:
                            response_file = f.read()
                            response_xml = eTree.XML(response_file)
                            for erro in response_xml.findall("Erro"):
                                error_text = "Erro. Codigo: %s Valor: %s" % (erro.find("Codigo").text, erro.find("Valor").text)
                                logger.error(error_text)
                            response_code = response_xml.find("IntegradorResposta/Codigo")
                            if response_code is None:
                                return ERROR_CODE_NOT_FOUND
                            if not response_code.text == 'AP':
                                # Retorno diferente de AP, tratar possiveis retornos
                                return "ERROR - Response code diferente de AP"
                            id_pagamento = response_xml.find("Resposta/IdPagamento")
                            if id_pagamento is None:
                                return "ERROR - Id pagamento nao encontrado"
                            # Obtem status do pagamento
                            response_status = response_xml.find("Resposta/StatusPagamento")
                            if response_status is None:
                                return "ERROR - Erro obtendo status do pagamento"
                            if not response_status.text == 'EnviadoAoValidador':
                                return "ERROR - Status do pagamento = %s" % response_status.text
                            payment_id = id_pagamento.text
                            break
                    except Exception:
                        logger.exception("Erro processando pagamento")
                        return "ERROR - Erro processando pagamento"
                    finally:
                        if not os.path.exists(os.path.join(self.error_dir, today)):
                            os.makedirs(os.path.join(self.error_dir, today))
                        if output_file:
                            response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                            if not payment_id:
                                copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                                copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                            move(output_file, os.path.join(self.temp_dir, today, response_file))
            if not payment_id:
                if not os.path.exists(os.path.join(self.error_dir, today)):
                    os.makedirs(os.path.join(self.error_dir, today))
                copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                logger.error("Response enviar pagamento nao encontrado")
                return "ERROR - Excedido numero de tentativas para enviar Pagamento"
            logger.debug("Process_Payment - ID obtida: %s" % payment_id)
            logger.debug("SAINDO process_payment")
            return payment_id

    def payment_status(self, msg):
        # type: (MBMessage) -> str
        logger.debug("ENTRANDO payment_status")
        if not self.is_mfe:
            return "OK"

        with self.lock:
            logger.debug("LOCK OBTIDO payment_status")
            # Obtem parametros do pagamento
            posid, order_id, tender_seq_id, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits = msg.data.split("\0")
            # posid, orderid, tender_seq_id, payment_amt, order_amt = '1', '2', '0', '1', '5'
            # Cria XML
            payment_data = self._create_payment_status_xml(order_id, tender_seq_id, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits)
            # Salva no diretorio
            today = datetime.now().strftime("%Y%m%d")
            now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
            temp_path = os.path.join(self.temp_dir, today, "payment_status_%s.xml" % now)
            temp_path2 = os.path.join(self.temp_dir, today, "payment_status2_%s.xml" % now)
            self.send_file_to_process(payment_data, temp_path, temp_path2, today)

            payment_id = None
            # Loop para verificar se status do pagamento enviado
            for i in xrange(1, self.max_retries, 1):
                files = os.listdir(self.integrador_outputdir)
                if not len(files):
                    if not i % 5:
                        logger.debug(MAX_RETRIES_ERROR_TRY_AGAIN % i)
                        self._clear_input_dir()
                        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                        temp_path2 = os.path.join(self.temp_dir, "payment_status2_%s.xml" % now)
                        copyfile(temp_path, temp_path2)
                        move(temp_path2, self.integrador_inputdir)
                    time.sleep(1)
                else:
                    output_file = None
                    try:
                        output_file = os.path.join(self.integrador_outputdir, files[0])
                        with file(output_file) as f:
                            response_file = f.read()
                            response_xml = eTree.XML(response_file)
                            for erro in response_xml.findall("Erro"):
                                error_text = "Erro. Codigo: %s Valor: %s" % (erro.find("Codigo").text, erro.find("Valor").text)
                                logger.error(error_text)
                            response_code = response_xml.find("IntegradorResposta/Codigo")
                            if response_code is None:
                                return "ERROR - Response code nao encontrado"
                            if not response_code.text == 'AP':
                                # Retorno diferente de AP, tratar possiveis retornos
                                return "ERROR - Response code diferente de AP"
                            id_pagamento = response_xml.find("Resposta/retorno")
                            if id_pagamento is None:
                                return "ERROR - Id pagamento nao encontrado"
                            if not id_pagamento.text == id_fila:
                                return "ERROR - Id pagamento nao confere"
                            payment_id = id_pagamento.text
                            break
                    except Exception:
                        logger.exception("Erro processando pagamento")
                        return "ERROR - Erro processando pagamento"
                    finally:
                        if not os.path.exists(os.path.join(self.error_dir, today)):
                            os.makedirs(os.path.join(self.error_dir, today))
                        if output_file:
                            response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                            if not payment_id:
                                copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                                copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                            move(output_file, os.path.join(self.temp_dir, today, response_file))
            if not payment_id:
                if not os.path.exists(os.path.join(self.error_dir, today)):
                    os.makedirs(os.path.join(self.error_dir, today))
                copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                logger.error("Response status do pagamento nao encontrado")
                return "ERROR - Excedido numero de tentativas para enviar status do Pagamento"

            logger.debug("Payment_Status - ID obtida: %s" % payment_id)

            #  Adicionamos o pagamento ao payment_map
            if order_id not in self.payment_map:
                self.payment_map[order_id] = []
            self.payment_map[order_id].append([tender_seq_id, id_fila, nsu, authcode, media, adq])
            logger.debug("SAINDO payment_status")
            return payment_id

    def cancel_order(self, pos_id, customer_doc, cnpj_sw, sign_ac, last_cfe):
        # type: (MBMessage) -> any
        if not self.is_mfe:
            return None

        # Cria XML
        data = self._create_cancel_sat_xml(pos_id, customer_doc, cnpj_sw, sign_ac, last_cfe)
        cancel_data = self._create_cancel_data_xml(random.randint(1, 999999), self.sat_act_key, last_cfe, data)
        # Salva no diretorio
        today = datetime.now().strftime("%Y%m%d")
        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        temp_path = os.path.join(self.temp_dir, today, "cancel_order_%s.xml" % now)
        temp_path2 = os.path.join(self.temp_dir, today, "cancel_order2_%s.xml" % now)
        self.send_file_to_process(cancel_data, temp_path, temp_path2, today)

        out = None
        # Loop para verificar se status do pagamento enviado
        for i in range(1, self.max_retries, 1):
            files = os.listdir(self.integrador_outputdir)
            if not len(files):
                if not i % 5:
                    logger.debug(MAX_RETRIES_ERROR_TRY_AGAIN % i)
                    self._clear_input_dir()
                    now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                    temp_path2 = os.path.join(self.temp_dir, "cancel_order2_%s.xml" % now)
                    copyfile(temp_path, temp_path2)
                    move(temp_path2, self.integrador_inputdir)
                time.sleep(1)
            else:
                output_file = None
                try:
                    output_file = os.path.join(self.integrador_outputdir, files[0])
                    with file(output_file) as f:
                        response_file = f.read()
                        response_xml = eTree.XML(response_file)
                        for erro in response_xml.findall("Erro"):
                            error_text = "Erro. Codigo: %s Valor: %s" % (erro.find("Codigo").text, erro.find("Valor").text)
                            logger.error(error_text)
                        response_code = response_xml.find("IntegradorResposta/Codigo")
                        if response_code is None:
                            return "ERROR - Response code nao encontrado"
                        if not response_code.text == 'AP':
                            # Retorno diferente de AP, tratar possiveis retornos
                            return "ERROR - Response code diferente de AP"
                        mfe_retorno = response_xml.find("Resposta/retorno")
                        if mfe_retorno is None:
                            return "ERROR - Id pagamento nao encontrado"
                        out = mfe_retorno.text
                        break
                except Exception:
                    logger.exception("Erro processando pagamento")
                    return "ERROR - Erro processando pagamento"
                finally:
                    if not os.path.exists(os.path.join(self.error_dir, today)):
                        os.makedirs(os.path.join(self.error_dir, today))
                    if output_file:
                        response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                        if not out:
                            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                            copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                        move(output_file, os.path.join(self.temp_dir, today, response_file))
        if not out:
            if not os.path.exists(os.path.join(self.error_dir, today)):
                os.makedirs(os.path.join(self.error_dir, today))
            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
            logger.error("Response cancelamento de pedido nao encontrado")
            return "ERROR - Excedido numero de tentativas para cancelar pedido"

        return out

    def send_file_to_process(self, cancel_data, temp_path, temp_path2, today):
        if not os.path.exists(os.path.join(self.temp_dir, today)):
            os.makedirs(os.path.join(self.temp_dir, today))
        request_file = open(temp_path, "w+")
        request_file.write(cancel_data)
        request_file.close()

        # Clean output directory
        self._clear_output_dir()
        self._clear_input_dir()
        copyfile(temp_path, temp_path2)
        move(temp_path2, self.integrador_inputdir)

    def status_operacional(self, msg):
        # type: (MBMessage) -> str
        with self.lock:
            out = self.consultar_status_operacional(random.randint(1, 999999), self.sat_act_key)
            if "Erro" in out:
                return "ERROR - Falha SAT"
            else:
                return out

    def process_sat(self, msg):
        # type: (MBMessage) -> str
        logger.debug("ENTRANDO process_sat")
        if msg.format != FM_STRING:
            raise Exception("Invalid parameter format")

        with self.lock:
            pos_id, order_id, data = msg.data.split('\0')
            if self.is_mfe:
                out = self._enviar_dados_mfe(random.randint(1, 999999), self.sat_act_key, data)
            else:
                out = self.enviar_dados_venda(random.randint(1, 999999), self.sat_act_key, data)

        logger.debug("Process_SAT - OUT: %s" % out)
        splitted = out.split('|')
        if out.startswith("ERROR") or len(splitted) < 2:
            raise Exception(out)
        if "06000" not in splitted[1]:
            raise Exception("Nota fiscal rejeitada pelo SAT. Erro: %s" % splitted[3] if len(splitted) > 3 else splitted[2])

        # XML Request que devera ser enviado ao BKOffice
        padded = splitted[6] + "=" * ((4 - len(splitted[6]) % 4) % 4)

        if self.sat_no is None:
            request = base64.b64decode(splitted[6])
            self.sat_no = re.search("<nserieSAT>(.*)<\/nserieSAT>", request).group(1)

        dt_emissao = datetime.strptime(splitted[7], "%Y%m%d%H%M%S").strftime("%d/%m/%y %H:%M:%S")
        sat_key = splitted[8][3:]
        qr_code = sat_key + "|" + splitted[7] + "|" + splitted[9] + "|" + splitted[10] + "|" + splitted[11]

        if self.is_mfe:
            #  Finaliza pagamentos no MFE
            if order_id in self.payment_map:
                logger.debug("ENTRANDO resposta_fiscal")
                with self.lock:
                    logger.debug("LOCK OBTIDO resposta_fiscal")
                    for payment in self.payment_map[order_id]:
                        tender_seq_id, id_fila, nsu, authcode, media, adq = payment
                        response_fiscal_id = self._resposta_fiscal(order_id, tender_seq_id, id_fila, sat_key, nsu, authcode, media, adq, '')
                        if not response_fiscal_id:
                            logger.error(pos_id, "Erro ao finalizar pagamento no Integrador Sefaz")
                            break
                        elif "ERROR" in id_fila:
                            logger.error(pos_id, "Erro ao finalizar pagamento no Integrador Sefaz: %s" % id_fila)
                            break

                        drv = persistence.Driver()
                        conn = None
                        try:
                            conn = drv.open(pyscripts.mbcontext, service_name="FiscalPersistence")
                            query = """
                                UPDATE fiscal.PaymentData SET PaymentId = '%s', ResponseFiscalId = '%s' 
                                WHERE OrderId = '%s' 
                                AND TenderSeqId = '%s'""" % (id_fila, response_fiscal_id, order_id, tender_seq_id)
                            conn.query(query)
                        finally:
                            if conn:
                                conn.close()

                    del self.payment_map[order_id]
                logger.debug("SAINDO resposta_fiscal")
            self.last_cfe_map[pos_id] = order_id, sat_key

        return """
        <SatResponse>
            <FiscalData>
                <datetime>%s</datetime>
                <satno>%s</satno>
                <satkey>%s</satkey>
                <CustomerCPF>%s</CustomerCPF>
                <QRCode>%s</QRCode>
            </FiscalData>
            <XmlRequest>%s</XmlRequest>
        </SatResponse>""" % (dt_emissao, self.sat_no, sat_key, splitted[10], qr_code, padded)

    def cancel_sale(self, msg):
        cancel_data = ast.literal_eval(msg.data)
        xml_de_cancelamento = cancel_data[0]
        chave = cancel_data[1]

        logger.debug("Cancel XML: {}".format(xml_de_cancelamento))
        with self.lock:
            out = self.cancelar_ultima_venda(random.randint(1, 999999), self.sat_act_key, chave, xml_de_cancelamento)
            if "07000" in out:
                message = "Venda cancelada com sucesso."
                splitted = out.split('|')
                padded = splitted[6] + "=" * ((4 - len(splitted[6]) % 4) % 4)
            elif "1218" in out:
                message = "Venda já cancelada anteriormente."
                padded = ''
            elif "1412" in out:
                logger.debug("Cancel Error XML: {}".format(xml_de_cancelamento))
                raise Exception("Não é mais possível cancelar esta venda: %s" % str(out))
            else:
                logger.debug("Cancel Error XML: {}".format(xml_de_cancelamento))
                raise Exception("Erro cancelando venda: %s" % str(out))
            return """
                    <SatCancelResponse>
                        <Message>%s</Message>
                        <XmlResponse>%s</XmlResponse>
                    </SatCancelResponse>""" % (message, padded)

    def process_cancel(self, msg):
        # type: (MBMessage) -> Optional[str]

        logger.debug("ENTRANDO process_cancel")
        with self.lock:
            logger.debug("LOCK OBTIDO process_cancel")
            # Obtem parametros do orderid e verifica se foi esse MFE que processou o pedido
            pos_id, order_id, customer_doc, cnpj_sw, sign_ac = msg.data.split('\0')
            if pos_id not in self.last_cfe_map:
                return None
            last_cfe = self.last_cfe_map[pos_id]
            if last_cfe[0] != order_id:
                return None
            last_cfe = last_cfe[1]  # Obtem o ultimo codigo CFE, para ser enviado ao SAT

            if self.is_mfe:
                out = self.cancel_order(pos_id, customer_doc, cnpj_sw, sign_ac, last_cfe)
            else:
                return None

        logger.debug("SAINDO process_cancel")
        logger.debug("Process_Cancel - OUT: %s" % out)
        if out.startswith("ERROR"):
            raise Exception(out)

        splitted = out.split('|')
        if "07000" not in splitted[1] and "07007" not in splitted[1]:
            raise Exception("Nota fiscal rejeitada pelo SAT. Erro: %s" % splitted[3])

        # XML Request que devera ser enviado ao BKOffice
        padded = splitted[6] + "=" * ((4 - len(splitted[6]) % 4) % 4)

        if self.sat_no is None:
            request = base64.b64decode(splitted[6])
            self.sat_no = re.search("<nserieSAT>(.*)<\/nserieSAT>", request).group(1)

        dt_emissao = datetime.strptime(splitted[7], "%Y%m%d%H%M%S").strftime("%d/%m/%y %H:%M:%S")
        sat_key = splitted[8][3:]
        qr_code = sat_key + "|" + splitted[7] + "|" + splitted[9] + "|" + splitted[10] + "|" + splitted[11]

        return """
        <SatResponse>
            <FiscalData>
                <datetime>%s</datetime>
                <satno>%s</satno>
                <satkey>%s</satkey>
                <CustomerCPF>%s</CustomerCPF>
                <QRCode>%s</QRCode>
            </FiscalData>
            <XmlRequest>%s</XmlRequest>
        </SatResponse>""" % (dt_emissao, self.sat_no, sat_key, splitted[10], qr_code, padded)

    def start_init_thread(self):
        self.init_thread_running = True
        self.init_thread = Thread(target=self._init_thread_loop)
        self.init_thread.daemon = True
        self.init_thread.start()

    def stop_init_thread(self):
        if self.init_thread_running:
            self.init_thread_condition.acquire()
            self.init_thread_running = False
            self.init_thread_condition.notifyAll()

    def _init_thread_sleep(self, sleep_time):
        self.init_thread_condition.acquire()
        self.init_thread_condition.wait(sleep_time)
        self.init_thread_condition.release()

    def _enviar_dados_mfe(self, sessao, act_key, data):
        # Cria XML
        enviar_dados_data = self._create_enviar_dados_xml(sessao, act_key, data)
        # Salva no diretorio
        today = datetime.now().strftime("%Y%m%d")
        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        temp_path = os.path.join(self.temp_dir, today, "enviar_dados_request_%s.xml" % now)
        temp_path2 = os.path.join(self.temp_dir, today, "enviar_dados_request2_%s.xml" % now)
        self.send_file_to_process(enviar_dados_data, temp_path, temp_path2, today)

        out = None
        # Loop para verificar se status do pagamento enviado
        for i in range(1, self.max_retries, 1):
            files = os.listdir(self.integrador_outputdir)
            if not len(files):
                if not i % 5:
                    logger.debug(MAX_RETRIES_ERROR_TRY_AGAIN % i)
                    self._clear_input_dir()
                    now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                    temp_path2 = os.path.join(self.temp_dir, "enviar_dados_request2_%s.xml" % now)
                    copyfile(temp_path, temp_path2)
                    move(temp_path2, self.integrador_inputdir)
                time.sleep(1)
            else:
                output_file = None
                try:
                    output_file = os.path.join(self.integrador_outputdir, files[0])
                    with file(output_file) as f:
                        response_file = f.read()
                        response_xml = eTree.XML(response_file)
                        for erro in response_xml.findall("Erro"):
                            error_text = "Erro. Codigo: %s Valor: %s" % (
                                erro.find("Codigo").text, erro.find("Valor").text)
                            logger.error(error_text)
                        response_code = response_xml.find("IntegradorResposta/Codigo")
                        if response_code is None:
                            return "ERROR - Response code nao encontrado"
                        if not response_code.text == 'AP':
                            # Retorno diferente de AP, tratar possiveis retornos
                            return "ERROR - Response code diferente de AP"
                        mfe_retorno = response_xml.find("Resposta/retorno")
                        if mfe_retorno is None:
                            return "ERROR - Retorno MFE nao encontrado"
                        out = mfe_retorno.text
                        break
                except Exception:
                    logger.exception("Erro enviando dados da venda")
                    return "ERROR - Erro enviando dados da venda"
                finally:
                    if not os.path.exists(os.path.join(self.error_dir, today)):
                        os.makedirs(os.path.join(self.error_dir, today))
                    if output_file:
                        response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                        if not out or "06000" not in out:
                            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                            copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                        move(output_file, os.path.join(self.temp_dir, today, response_file))
        if not out:
            if not os.path.exists(os.path.join(self.error_dir, today)):
                os.makedirs(os.path.join(self.error_dir, today))
            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
            logger.error("Response enviar dados da venda nao encontrado")
            return "ERROR - Excedido numero de tentativas para enviar dados da Venda"

        return out

    def _resposta_fiscal(self, order_id, tender_seq_id, id_fila, chave_nfe, nsu, authcode, media, adq, impressao_fiscal):
        # Cria XML
        resposta_fiscal_data = self._create_resposta_fiscal_xml(order_id, tender_seq_id, id_fila, chave_nfe, nsu, authcode, media, adq, impressao_fiscal)
        # Salva no diretorio
        today = datetime.now().strftime("%Y%m%d")
        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        temp_path = os.path.join(self.temp_dir, today, "resposta_fiscal_%s.xml" % now)
        temp_path2 = os.path.join(self.temp_dir, today, "resposta_fiscal2_%s.xml" % now)
        self.send_file_to_process(resposta_fiscal_data, temp_path, temp_path2, today)

        out = None
        # Loop para verificar se status do pagamento enviado
        for i in range(1, self.max_retries, 1):
            files = os.listdir(self.integrador_outputdir)
            if not len(files):
                if not i % 5:
                    logger.debug(MAX_RETRIES_ERROR_TRY_AGAIN % i)
                    self._clear_input_dir()
                    now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                    temp_path2 = os.path.join(self.temp_dir, "resposta_fiscal2_%s.xml" % now)
                    copyfile(temp_path, temp_path2)
                    move(temp_path2, self.integrador_inputdir)
                time.sleep(1)
            else:
                output_file = None
                try:
                    output_file = os.path.join(self.integrador_outputdir, files[0])
                    with file(output_file) as f:
                        response_file = f.read()
                        response_xml = eTree.XML(response_file)
                        for erro in response_xml.findall("Erro"):
                            error_text = "Erro. Codigo: %s Valor: %s" % (
                                erro.find("Codigo").text, erro.find("Valor").text)
                            logger.error(error_text)
                        response_code = response_xml.find("IntegradorResposta/Codigo")
                        if response_code is None:
                            return "ERROR - Response code nao encontrado"
                        if not response_code.text == 'AP':
                            # Retorno diferente de AP, tratar possiveis retornos
                            return "ERROR - Response code diferente de AP"
                        mfe_retorno = response_xml.find("Resposta/retorno")
                        if mfe_retorno is None:
                            return "ERROR - Retorno MFE nao encontrado"
                        out = mfe_retorno.text
                        break
                except Exception:
                    logger.exception("Erro enviando resposta fiscal")
                    return "ERROR - Erro enviando resposta fiscal"
                finally:
                    if not os.path.exists(os.path.join(self.error_dir, today)):
                        os.makedirs(os.path.join(self.error_dir, today))
                    if output_file:
                        response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                        if not out:
                            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                            copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                        move(output_file, os.path.join(self.temp_dir, today, response_file))
        if not out:
            if not os.path.exists(os.path.join(self.error_dir, today)):
                os.makedirs(os.path.join(self.error_dir, today))
            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
            logger.exception("Response resposta fiscal nao encontrado")
            return "ERROR - Excedido numero de tentativas para enviar resposta fiscal"
        logger.debug("Resposta_Fiscal - OUT: %s" % out)

        return out

    def _consultar_mfe(self, sessao):
        # Cria XML
        consultar_mfe_data = self._create_consultar_mfe_xml(sessao)
        # Salva no diretorio
        today = datetime.now().strftime("%Y%m%d")
        now = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        temp_path = os.path.join(self.temp_dir, today, "consultar_mfe_%s.xml" % now)
        temp_path2 = os.path.join(self.temp_dir, today, "consultar_mfe2_%s.xml" % now)
        if not os.path.exists(os.path.join(self.temp_dir, today)):
            os.makedirs(os.path.join(self.temp_dir, today))
        request_file = open(temp_path, "w+")
        request_file.write(consultar_mfe_data)
        request_file.close()
        # Limpa diretorio de saida antes de enviar o de request
        self._clear_output_dir()
        self._clear_input_dir()
        copyfile(temp_path, temp_path2)
        move(temp_path2, self.integrador_inputdir)
        out = None

        # Loop para verificar se status do pagamento enviado
        for _ in range(1, self.max_retries, 1):
            files = os.listdir(self.integrador_outputdir)
            if not len(files):
                time.sleep(0.2)
            else:
                output_file = None
                try:
                    output_file = os.path.join(self.integrador_outputdir, files[0])
                    with file(output_file) as f:
                        response_file = f.read()
                        response_xml = eTree.XML(response_file)
                        for erro in response_xml.findall("Erro"):
                            error_text = "Erro. Codigo: %s Valor: %s" % (
                                erro.find("Codigo").text, erro.find("Valor").text)
                            logger.error(error_text)
                        response_code = response_xml.find("IntegradorResposta/Codigo")
                        if response_code is None:
                            return "ERROR - Response code nao encontrado"
                        if not response_code.text == 'AP':
                            # Retorno diferente de AP, tratar possiveis retornos
                            return "ERROR - Response code diferente de AP"
                        mfe_retorno = response_xml.find("Resposta/retorno")
                        if mfe_retorno is None:
                            return "ERROR - Retorno MFE nao encontrado"
                        out = mfe_retorno.text
                        break
                except Exception:
                    logger.exception("Erro consultando mfe")
                    return "ERROR - Erro consultando mfe"
                finally:
                    if not os.path.exists(os.path.join(self.error_dir, today)):
                        os.makedirs(os.path.join(self.error_dir, today))
                    if output_file:
                        response_file = os.path.basename(temp_path).replace('.xml', '_response.xml')
                        if not out or "SAT em opera" not in out:
                            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
                            copyfile(output_file, os.path.join(self.error_dir, today, response_file))
                        move(output_file, os.path.join(self.temp_dir, today, response_file))
        if not out:
            if not os.path.exists(os.path.join(self.error_dir, today)):
                os.makedirs(os.path.join(self.error_dir, today))
            copyfile(temp_path, os.path.join(self.error_dir, today, os.path.basename(temp_path)))
            logger.error("Response consulta MFE nao encontrado")
            return "ERROR - Excedido numero de tentativas para consultar MFE"

        return out

    def _clear_output_dir(self):
        filelist = os.listdir(self.integrador_outputdir)
        for f in filelist:
            os.remove(os.path.join(self.integrador_outputdir, f))

    def _clear_input_dir(self):
        filelist = os.listdir(self.integrador_inputdir)
        for f in filelist:
            os.remove(os.path.join(self.integrador_inputdir, f))

    # noinspection PyMethodMayBeStatic
    def _create_payment_xml(self, orderid, tender_seq_id, payment_amt, order_amt):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%s_%s</Valor>
              </Identificador>
              <Componente Nome="VFP-e">
                <Metodo Nome="EnviarPagamento">
                  <Construtor>
                    <Parametros>
                      <Parametro>
                        <Nome>chaveAcessoValidador</Nome>
                        <!--String-->
                        <Valor>%s</Valor>
                      </Parametro>
                    </Parametros>
                  </Construtor>
                  <Parametros>
                    <Parametro>
                      <Nome>ChaveRequisicao</Nome>
                      <!--Guid-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Estabelecimento</Nome>
                      <!--int-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                        <Nome>SerialPos</Nome>
                        <Valor>TEF</Valor>
                    </Parametro>
                    <Parametro>
                        <Nome>CNPJ</Nome>
                        <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                        <Nome>ValorOperacaoSujeitaICMS</Nome>
                        <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                        <Nome>ValorTotalVenda</Nome>
                        <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>IcmsBase</Nome>
                      <!--decimal-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>HabilitarMultiplosPagamentos</Nome>
                      <!--bool-->
                      <Valor>True</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>HabilitarControleAntiFraude</Nome>
                      <!--bool-->
                      <Valor>False</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>CodigoMoeda</Nome>
                      <!--string-->
                      <Valor>BRL</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>OrigemPagamento</Nome>
                      <!--string-->
                      <Valor>Order%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>EmitirCupomNFCE</Nome>
                      <!--bool-->
                      <Valor>False</Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (orderid, tender_seq_id, self.chave_acesso_validador, self.chave_requisicao, self.estabelecimento, self.cnpj, payment_amt, order_amt, self.icms_base, orderid)
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_payment_status_xml(self, order_id, tender_seq_id, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%s_%s</Valor>
              </Identificador>
              <Componente Nome="VFP-e">
                <Metodo Nome="EnviarStatusPagamento">
                  <Construtor>
                    <Parametros>
                      <Parametro>
                        <Nome>chaveAcessoValidador</Nome>
                        <!--String-->
                        <Valor>%s</Valor>
                      </Parametro>
                    </Parametros>
                  </Construtor>
                  <Parametros>
                    <Parametro>
                      <Nome>CodigoAutorizacao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Bin</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>DonoCartao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>DataExpiracao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>InstituicaoFinanceira</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Parcelas</Nome>
                      <!--string-->
                      <Valor>1</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>CodigoPagamento</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>ValorPagamento</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>IdFila</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Tipo</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>UltimosQuatroDigitos</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (order_id, tender_seq_id, self.chave_acesso_validador, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits)
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_enviar_dados_xml(self, sessao, act_key, data):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%d</Valor>
              </Identificador>
              <Componente Nome="MF-e">
                <Metodo Nome="EnviarDadosVenda">
                  <Parametros>
                    <Parametro>
                      <Nome>numeroSessao</Nome>
                      <!--int-->
                      <Valor>%d</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>codigoDeAtivacao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>dadosVenda</Nome>
                      <!--string-->
                      <Valor><![CDATA[%s]]></Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>nrDocumento</Nome>
                      <!--string-->
                      <Valor>%d</Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (int(sessao), int(sessao), act_key, data, int(sessao))
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_consultar_mfe_xml(self, sessao):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%s</Valor>
              </Identificador>
              <Componente Nome="MF-e">
                <Metodo Nome="ConsultarMFe">
                  <Parametros>
                    <Parametro>
                      <Nome>numeroSessao</Nome>
                      <!--int-->
                      <Valor>%s</Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (int(sessao), int(sessao))
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_resposta_fiscal_xml(self, order_id, tender_seq_id, id_fila, chave_nfe, nsu, auth_code, media, adq, impressao_fiscal):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%s_%s</Valor>
              </Identificador>
              <Componente Nome="VFP-e">
                <Metodo Nome="RespostaFiscal">
                  <Construtor>
                    <Parametros>
                      <Parametro>
                        <Nome>chaveAcessoValidador</Nome>
                        <!--String-->
                        <Valor>%s</Valor>
                      </Parametro>
                    </Parametros>
                  </Construtor>
                  <Parametros>
                    <Parametro>
                      <Nome>idFila</Nome>
                      <!--int-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>ChaveAcesso</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Nsu</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>NumerodeAprovacao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Bandeira</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Adquirente</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>Cnpj</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>ImpressaoFiscal</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>NumeroDocumento</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (order_id, tender_seq_id, self.chave_acesso_validador, id_fila, chave_nfe, nsu, auth_code, media, adq, self.cnpj, impressao_fiscal, nsu)
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_cancel_data_xml(self, sessao, act_key, last_cfe, xml_cancel):
        xml = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <Integrador>
              <Identificador>
                <Valor>%s</Valor>
              </Identificador>
              <Componente Nome="MF-e">
                <Metodo Nome="CancelarUltimaVenda">
                  <Parametros>
                    <Parametro>
                      <Nome>numeroSessao</Nome>
                      <!--int-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>codigoDeAtivacao</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>chave</Nome>
                      <!--string-->
                      <Valor>%s</Valor>
                    </Parametro>
                    <Parametro>
                      <Nome>dadosCancelamento</Nome>
                      <!--string-->
                      <Valor><![CDATA[%s]]></Valor>
                    </Parametro>
                  </Parametros>
                </Metodo>
              </Componente>
            </Integrador>""" % (sessao, sessao, act_key, last_cfe, xml_cancel)
        return xml

    # noinspection PyMethodMayBeStatic
    def _create_cancel_sat_xml(self, pos_id, customer_doc, cnpj_sw, sign_ac, last_cfe):
        if not customer_doc:
            dest = "<dest></dest>"
        elif len(customer_doc) == 11:
            dest = "<dest><CPF>%s</CPF></dest>" % customer_doc
        else:
            dest = "<dest><CNPJ>%s</CNPJ></dest>" % customer_doc

        xml = """<?xml version="1.0" encoding="UTF-8"?>
            <CFeCanc>
                <infCFe chCanc="CFe%s">
                    <ide>
                        <CNPJ>%s</CNPJ>
                        <signAC>%s</signAC>
                        <numeroCaixa>%03d</numeroCaixa>
                    </ide>
                    <emit></emit>
                    %s
                    <total></total>
                </infCFe>
            </CFeCanc>""" % (last_cfe, cnpj_sw, sign_ac, int(pos_id), dest)
        return xml

    def _get_dll(self, manufacturer):
        sat_lib = os.path.join("{BUNDLEDIR}/dll", manufacturer)
        for var in re.findall("{[a-zA-Z0-9]*}+", sat_lib):
            sat_lib = sat_lib.replace(var, os.environ.get(var.replace('{', '').replace('}', ''), ""))

        os.chdir(sat_lib)
        if platform.system() == "Windows":
            self.sat_dll = ctypes.WinDLL(os.path.join(os.getcwd(), "dllsat.dll"))
        else:
            self.sat_dll = ctypes.CDLL(os.path.join(os.getcwd(), "dllsat.so"))

        self.consultar_sat = self.sat_dll["ConsultarSAT"]
        self.consultar_sat.restype = ctypes.c_char_p
        self.consultar_status_operacional = self.sat_dll["ConsultarStatusOperacional"]
        self.consultar_status_operacional.restype = ctypes.c_char_p
        self.enviar_dados_venda = self.sat_dll["EnviarDadosVenda"]
        self.enviar_dados_venda.restype = ctypes.c_char_p
        self.enviar_dados_venda.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self.cancelar_ultima_venda = self.sat_dll["CancelarUltimaVenda"]
        self.cancelar_ultima_venda.restype = ctypes.c_char_p

    def _init_thread_loop(self):
        while self.init_thread_running:
            bin_path = os.getcwd()

            try:
                if self.is_active() == "OK":
                    self._init_thread_sleep(300)
                    continue
            except Exception:
                pass

            for manufacturer in self.manufacturers:
                try:
                    logger.info("Testando DLL Manufacturer - {0}".format(manufacturer))
                    self._init_thread_sleep(1)

                    self._get_dll(manufacturer)
                    if self.is_active() == "OK":
                        logger.info("Manufacturer OK - {0}".format(manufacturer))
                        break
                    raise Exception()

                except Exception:
                    os.chdir(bin_path)
                    logger.info("Manufacturer FAIL - {0}".format(manufacturer))
            else:
                # Wait for another Loop
                self._init_thread_sleep(60)
