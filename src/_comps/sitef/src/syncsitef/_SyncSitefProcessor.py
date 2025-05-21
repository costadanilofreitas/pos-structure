# -*- coding: utf-8 -*-

import base64
import logging
import os
import re
import time
from ctypes import WinDLL, c_long, addressof, create_string_buffer
from threading import Lock
from xml.etree import cElementTree as eTree

import sysactions
from sitef import SitefProcessor
from systools import sys_log_exception

logger = logging.getLogger("Sitef")


class SynchSitefProcessor(SitefProcessor):
    def __init__(self, mbcontext, callback):
        super(SynchSitefProcessor, self).__init__()
        self.sitef_service_finder = None

        self.mbcontext = mbcontext
        sysactions.mbcontext = mbcontext
        self.callback = callback
        self.id_loja = None
        self.ip_sitef = None
        self.timeout = None
        self.current_processing = None, None

        self.cancela = False
        self.anulado = False

        self.lock = Lock()

        clisitef_lib = "{BUNDLEDIR}/lib/clisitef32i.dll"
        for var in re.findall("{[a-zA-Z0-9]*}+", clisitef_lib):
            clisitef_lib = clisitef_lib.replace(var, os.environ.get(var.replace('{', '').replace('}', ''), ""))

        self.sitefDll = WinDLL(clisitef_lib)

        self.configuraIntSiTefInterativo = self.sitefDll["ConfiguraIntSiTefInterativo"]
        self.iniciaFuncaoSiTefInterativo = self.sitefDll["IniciaFuncaoSiTefInterativo"]
        self.continuaFuncaoSiTefInterativo = self.sitefDll["ContinuaFuncaoSiTefInterativo"]
        self.finalizaFuncaoSiTefInterativo = self.sitefDll["FinalizaFuncaoSiTefInterativo"]

    def process(self, bus_msg, pos_id, order_id, operador, tender_type, amount, data_fiscal, hora_fiscal, tender_seq_id, display_via_api, ip_sitef=None):
        self.anulado = False
        tender_type = int(tender_type)
        id_terminal = "SW%06d" % int(pos_id)
        receipt_merchant = ""
        receipt_customer = ""
        authorizer_cnpj = ""
        transaction_processor = ""
        nome_instituicao = None
        bin_cartao = None
        auth_code = None
        bandeira = None
        rede_autorizadora = None
        data_vencimento = None
        nsu = None
        data_transacao = ''
        id_mercado_pago = ''
        response = None
        display_via_api = True if display_via_api == 'True' else False
        last_digits = "0000"

        logger.debug("SynchSitefProcessor - STARTED")
        self.callback(pos_id, "Conectando PinPad", display_via_api)
        time_limit = (time.time() + 5.0)
        while (time.time() < time_limit) and (not self.sitefDll["VerificaPresencaPinPad"]()):
            time.sleep(0.2)

        self.ip_sitef = self.sitef_service_finder.find_sitef_service() if ip_sitef is None else ip_sitef
        if self.current_processing[0] == order_id:
            self.ip_sitef = self.current_processing[1]
        else:
            self._check_finalized_last_order(pos_id)

        if self.ip_sitef is None:
            self.sitef_service_finder.wakeup_search()

            response = "<EftXml Result=\"Sem Conexao SiTEF\"/>"
            logger.debug("SynchSitefProcessor - ENDED Response: {0}".format(response))
            return True, response

        logger.debug("SynchSitefProcessor - ip_sitef: {0}, id_loja: {1}, id_terminal: {2}".format(self.ip_sitef, self.id_loja, id_terminal))

        ret = self.configuraIntSiTefInterativo(self.ip_sitef, self.id_loja, id_terminal, 0)
        if ret != 0:
            self.sitef_service_finder.sitef_unavailable(self.ip_sitef)
            response = "<EftXml Result=\"Servidor SiTEF Inoperante\"/>"
            logger.debug("SynchSitefProcessor - ENDED Response: {0}".format(response))
            return True, response

        if ret == 0:
            self.cancela = False
            # Send EVENT to notify SITEF started PROCESSING...
            self.mbcontext.MB_EasyEvtSend('SITEF', 'PROCESS_STARTED', xml=str(tender_type), sourceid=int(pos_id), synchronous=True)

            # 2 = debito, 3 = credito
            # valor separado por virgula. Deve ter sempre 2 casas apos a virgula
            # numero do cupom fiscal
            # data YYYYMMDD
            # hora HHMMSS
            # operador 123
            codigo_tipo = None
            if tender_type == 1:  # Credito
                codigo_tipo = 3
            elif tender_type == 2:  # Debito
                codigo_tipo = 2
            elif tender_type == 3:  # Teste conexão SiTef
                codigo_tipo = 111
            elif tender_type == 122:  # Mercado Pago
                codigo_tipo = 122

            ret = self.iniciaFuncaoSiTefInterativo(codigo_tipo, amount, pos_id + order_id, data_fiscal, hora_fiscal, operador, "")
            if ret == 10000:
                comando = c_long(0)
                tipo_campo = c_long(0)
                tam_minimo = c_long(0)
                tam_maximo = c_long(0)
                tam_buffer = 32768
                output_buffer = create_string_buffer('\000' * tam_buffer)

                last_time = -1
                last_message = ""
                self.current_processing = order_id, self.ip_sitef
                while ret == 10000:
                    with self.lock:
                        if self.cancela:
                            continua = -1 if tender_type == 122 else 2
                        else:
                            continua = 0
                    ret = self.continuaFuncaoSiTefInterativo(addressof(comando), addressof(tipo_campo), addressof(tam_minimo), addressof(tam_maximo), output_buffer, tam_buffer, continua)

                    # logger.debug("Iteração => ret: {0}, comando: {1}, tipo_campo: {2}, output_buffer: {3}, last_message: {4}".format(ret, comando.value, tipo_campo.value, output_buffer.value, last_message))

                    if ret != 10000:
                        break

                    # Qualquer acao diferente de esperando, zeramos o timer
                    if comando.value != 23:
                        last_time = -1
                    try:
                        if not comando.value == 0:
                            if comando.value == 1:
                                # Mostra buffer no visor do operador
                                last_message = output_buffer.value
                                self.callback(pos_id, output_buffer.value, display_via_api)
                            elif comando.value == 2:
                                # Mostra mensagem no visor do cliente
                                pass
                            elif comando.value == 3:
                                # Mostra mensagem nos dois visores
                                last_message = output_buffer.value
                                self.callback(pos_id, output_buffer.value, display_via_api)
                            elif comando.value == 11:
                                # Apaga mensagem do visor do operador
                                last_message = ""
                                self.callback(pos_id, "", display_via_api)
                                # write_ldisplay(model, "")
                            elif comando.value == 12:
                                # Apaga mensagem do visor do cliente
                                self.callback(pos_id, "", display_via_api)
                                # write_ldisplay(model, "")
                            elif comando.value == 13:
                                # Apaga mensagem do visor do operador e do cliente
                                last_message = ""
                                self.callback(pos_id, "", display_via_api)
                                # write_ldisplay(model, "")
                            elif comando.value == 22:
                                # Apresenta buffer e aguarda uma tecla do operador (para que ele fique ciente da mensagem)
                                self.callback(pos_id, output_buffer.value, display_via_api)
                            elif comando.value == 4:
                                # Apresenta buffer e aguarda proximo comando (21), que ira apresentar as opcoes pro operador
                                pass
                            elif comando.value == 21:
                                # Apresenta buffer como opcoes (separado por ;) e obtem escolha do operador
                                pass
                            elif comando.value == 14:
                                # Apaga o titulo apresentado pelo comando 4
                                pass
                            elif comando.value == 23:
                                # Esperando acao do usuario... DEVERA HAVER UM BOTAO PARA O OPERADOR PODER CANCELAR
                                if last_time == -1:
                                    last_time = time.time()
                                else:
                                    current_time = time.time()
                                    if current_time - last_time > self.timeout:
                                        with self.lock:
                                            self.cancela = True

                                        logger.debug("SynchSitefProcessor - Cancel Requested - OrderId: {0} - IP SiTef: {1}".format(order_id, self.ip_sitef))
                                        output_buffer.value = "0" * tam_maximo.value
                                    else:
                                        self.callback(pos_id, last_message + " " + str(self.timeout - int(current_time - last_time)), display_via_api)
                                # self.callback(self, oBuffer.value)
                            elif comando.value == 20:
                                # Pressionada tecla ANULA. Cancela operacao
                                if codigo_tipo != 111:
                                    self.anulado = True
                                output_buffer.value = "0"
                                time.sleep(1.5)
                            elif comando.value == 30:
                                # Inserir Codigo de Seguranca
                                pin = self.callback(pos_id, "THREAD_ASK_PIN|{}".format(output_buffer.value), display_via_api)
                                if pin == "CANCELA":
                                    with self.lock:
                                        self.cancela = True

                                    logger.debug("SynchSitefProcessor - PIN Cancel Requested - OrderId: {0} - IP SiTef: {1}".format(order_id, self.ip_sitef))
                                    output_buffer.value = "0" * tam_maximo.value
                                else:
                                    output_buffer.value = pin
                            else:
                                self.callback(pos_id, "Mensagem %s %s" % (str(comando.value), output_buffer.value), display_via_api)
                                time.sleep(0.5)

                        if not tipo_campo.value == -1:
                            if tipo_campo.value == 136:
                                # BIN do cartao
                                bin_cartao = output_buffer.value
                            elif tipo_campo.value == 131:
                                # indice que indica qual a instituicao que ira processar a transacao
                                transaction_processor = output_buffer.value
                            elif tipo_campo.value == 132:
                                # Captura Tipo do cartao que ira processar
                                # 00001 = VISA
                                # 00002 = MASTERCARD
                                # 00004 = AMEX
                                bandeira = output_buffer.value
                            elif tipo_campo.value == 952:
                                # Numero de autorizacao NFCe (##################################Usar este ou 135?????)
                                auth_code = output_buffer.value
                            elif tipo_campo.value == 101:
                                # Modalidade de pagamento (apenas para exibicao)
                                pass
                            elif tipo_campo.value == 102:
                                # Modalidade de pagamento a ser impressa na NF
                                pass
                            elif tipo_campo.value == 121:
                                # Primeira via do comprovante de pagamento a ser impresso (via do cliente)
                                receipt_customer = output_buffer.value
                            elif tipo_campo.value == 122:
                                # Segunda via do comprovante de pagamento a ser impresso (via do caixa)
                                receipt_merchant = output_buffer.value
                            elif tipo_campo.value == 133:
                                nsu = output_buffer.value
                            elif tipo_campo.value == 134:
                                # NSU Host
                                pass
                            elif tipo_campo.value == 135:
                                # Codigo de autorizacao de credito (#####################################Usar este ou 952????)
                                pass
                            elif tipo_campo.value == 105:
                                # Data e hora da transacao YYYYMMDDHHMMSS
                                data_transacao = output_buffer.value
                                pass
                            elif tipo_campo.value == 158:
                                # Codigo da rede autorizadora (05 #################################Usar este ou 131????)
                                rede_autorizadora = output_buffer.value
                            elif tipo_campo.value == 156:
                                # Nome da instituicao: MASTERCARD
                                nome_instituicao = output_buffer.value.strip()
                            elif tipo_campo.value == 157:
                                # Codigo de estabelecimento (00000001)
                                pass
                            elif tipo_campo.value == 513:
                                data_vencimento = output_buffer.value
                            elif tipo_campo.value == 950:
                                # Codigo do CNPJ da autorizadora
                                authorizer_cnpj = output_buffer.value.strip()
                            elif tipo_campo.value == 4077:
                                # Codigo de identificação do pagamento para Mercado Pago (limitado a 9 caracteres)
                                id_mercado_pago = output_buffer.value[-9:]
                            elif tipo_campo.value == 1190:
                                # Embosso (4 últimos dígitos) do Cartão
                                last_digits = output_buffer.value
                    except Exception as ex:
                        sys_log_exception("Exception Trapped on SiTef Processor %" + str(ex))
                if ret == 0:
                    if codigo_tipo != 111:
                        receipt_merchant = receipt_merchant if receipt_merchant not in ("", None) else receipt_customer
                        b64_receipt_merchant = base64.b64encode(receipt_merchant)
                        b64_receipt_customer = base64.b64encode(receipt_customer)
                        if tender_type == 122:
                            auth_code = "{}{}".format(data_transacao, id_mercado_pago)
                        response = SitefProcessor.RESPONSE_XML % (nome_instituicao, ret, bin_cartao, auth_code, amount, rede_autorizadora, authorizer_cnpj, bandeira, b64_receipt_merchant, b64_receipt_customer, data_vencimento, nsu, transaction_processor, last_digits)

                        logger.debug("SynchSitefProcessor - ENDED Success - OrderId: {0} - IP SiTef: {1}".format(order_id, self.ip_sitef))
                        return True, response
                else:
                    #  Limpa o visor do operador em caso de erro
                    self.callback(pos_id, "", display_via_api)
                    if self.anulado or ret == -2 or ret == -120:
                        response = "<EftXml Result=\"Cancelado\" />"
                    elif ret == -5:
                        self.sitef_service_finder.sitef_unavailable(self.ip_sitef)
                        self.mbcontext.MB_EasyEvtSend('SITEF', 'PROCESS_ENDED', xml='', sourceid=int(pos_id), synchronous=True)

                        if self.current_processing == (order_id, self.ip_sitef):
                            sysactions.show_info_message(pos_id, "Falha Servidor SiTEF.", msgtype="warning")
                            response = "<EftXml Result=\"Falha Servidor SiTEF\" />"
                        else:
                            sysactions.show_info_message(pos_id, "Falha Servidor SiTEF. Trocando Servidor.", msgtype="warning")
                            response = "<EftXml Result=\"Falha Servidor SiTEF - Trocando Servidor\" />"

                    elif ret == -43:
                        response = "<EftXml Result=\"Erro PinPad\" />"
                    elif ret == -6:
                        response = "<EftXml Result=\"Operacao Cancelada pelo Usuario\" />"
                    elif ret == -40:
                        response = "<EftXml Result=\"Nao Autorizado - SiTEF\" />"
                    elif ret > 0:
                        response = "<EftXml Result=\"Nao Autorizado\" />"
                    else:
                        response = "<EftXml Result=\"Falha na Operacao: Erro %s\" />" % str(ret)
        else:
            response = "<EftXml Result=\"Falha na Operacao: Erro %s\" />" % str(ret)

        logger.debug("SynchSitefProcessor - ENDED Response: {0}".format(response))
        return True, response

    def finalizar(self, pos_id, order_id, data_fiscal, hora_fiscal, status):
        try:
            logger.info("SITEF Finalizar - Pos: {0} / Order: {1} / Status: {2}".format(pos_id, order_id, status))
            self.sitef_service_finder.lock_sitef()
            if self.current_processing[0] == order_id:
                self.ip_sitef = self.current_processing[1]
                id_terminal = "SW%06d" % int(pos_id)
                logger.info("SITEF Finalizar - Pos: {0} / Order: {1} / Status: {2} / {3}-{4}-{5}".format(pos_id, order_id, status, self.ip_sitef, self.id_loja, id_terminal))
                self.configuraIntSiTefInterativo(self.ip_sitef, self.id_loja, id_terminal, 0)
                self.finalizaFuncaoSiTefInterativo(status, pos_id + order_id, data_fiscal, hora_fiscal, None)
                self.current_processing = None, None
        except Exception as _:
            logger.exception("SITEF Finalizar - Pos: {0} / Order: {1} / Status: {2}".format(pos_id, order_id, status))
            raise
        finally:
            self.sitef_service_finder.release_sitef()

    def config(self, id_loja, ip_sitef, timeout, sitef_service_finder):
        self.id_loja = id_loja

        self.ip_sitef = ip_sitef[0] if isinstance(ip_sitef, list) else ip_sitef
        self.timeout = timeout
        self.sitef_service_finder = sitef_service_finder

    def cancel(self):
        with self.lock:
            self.cancela = True

    def terminate(self):
        self.sitef_service_finder.stop_search_thread()

    def _check_finalized_last_order(self, pos_id):
        for i in xrange(0, 3, 1):
            if self.current_processing != (None, None):
                from sysactions import get_model, get_posot
                order_id = self.current_processing[0]
                order = get_posot(get_model(pos_id)).orderPicture(orderid=order_id)
                order = eTree.XML(order).find("Order")
                created_at = order.get("createdAt").replace("-", "").replace(":", "")
                data_fiscal = created_at[:8]
                hora_fiscal = created_at[9:15]
                if order.find("StateHistory/State[@state='PAID']") is not None:
                    status = "1"
                elif order.find("StateHistory/State[@state='VOIDED']") is not None:
                    status = "0"
                else:
                    logger.error("Order %s sem status PAID ou VOIDED" % order_id)
                    return
                self.finalizar(pos_id, order_id, data_fiscal, hora_fiscal, status)
            else:
                return
        self.current_processing = None, None
