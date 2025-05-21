# -*- coding: utf-8 -*-
import base64
import logging
import os
import time
import clr

logger = logging.getLogger("Cappta")


class CapptaProcessor(object):
    RESPONDE_XML = """<EftXml Media='%s' Result='%s' CardNumber='%sXXXXXXXXXX' AuthCode='%s' ApprovedAmount='%s' IdAuth='%s' CNPJAuth='%s' Bandeira='%s' ReceiptMerchant='%s' ReceiptCustomer='%s' TransactionProcessor='%s'/>"""

    def process(self, bus_msg, pos_id, order_id, operator, tender_type, amount, fiscal_date, fiscal_time, tender_id):
        raise NotImplementedError()

    def finalizar(self, pos_id, order_id, data_fiscal, hora_fiscal, status):
        return

    def reprint(self, bus_msg, pos_id, slip_type):
        raise NotImplementedError()

    def cancel(self, bus_msg, pos_id, password, control_number):
        raise NotImplementedError()


class FakeCapptaProcessor(CapptaProcessor):
    def __init__(self):
        super(FakeCapptaProcessor, self).__init__()

    def process(self, bus_msg, pos_id, order_id, operator, tender_type, amount, fiscal_date, fiscal_time, tender_id):
        nome_instituicao = ''
        ret = '0'
        bin_cartao = '4111XXXXXXXXXXXX'
        auth_code = '1302'
        rede_autorizadora = '08496898000142'
        bandeira = '4'
        transaction_processor = '00051'
        b64_receipt_customer = base64.b64encode("Recibo de teste.\nSitef FAKE")
        b64_receipt_merchant = base64.b64encode("Recibo de teste.\nSitef FAKE")

        response = CapptaProcessor.RESPONDE_XML % (nome_instituicao, ret, bin_cartao, auth_code, amount, rede_autorizadora, "", bandeira, b64_receipt_merchant, b64_receipt_customer, transaction_processor)
        return response

    def finalizar(self, pos_id, order_id, data_fiscal, hora_fiscal, status):
        return

    def reprint(self, bus_msg, pos_id, slip_type):
        return

    def cancel(self, bus_msg, pos_id, password, control_number):
        return


class SynchCapptaProcessor(CapptaProcessor):
    def __init__(self, pos_id, cnpj, auth_key, module_directory, callback, env):
        super(SynchCapptaProcessor, self).__init__()
        self.cnpj = cnpj
        self.pos_id = int(pos_id)
        self.auth_key = auth_key
        self.env = env
        self.callback = callback
        self.retorno = ["Sucesso",
                        "Não autenticado. Alguma das informações fornecidas para autenticação não é válida",
                        "CapptaGpPlus está sendo inicializado",
                        "Formato da requisição recebida pelo CapptaGpPlus é inválido",
                        "Operação cancelada pelo operador",
                        "Pagamento não autorizado/pendente/não encontrado",
                        "Pagamento ou cancelamento negados pela rede adquirente ou falta de conexão com internet",
                        "Erro interno no CapptaGpPlus",
                        "Erro na comunicação entre a CappAPI e o CapptaGpPlus",
                        "Último pagamento ainda não finalizado",
                        "Uma reimpressão ou cancelamento foi executada dentro de uma sessão multi-cartões",
                        "", "", "",
                        "Valor digitado no pinpad é inválido"]
        old_dir = os.getcwd()
        os.chdir(os.path.join(module_directory, "dll"))
        clr.AddReference(os.path.join(os.getcwd(), "Cappta.Gp.Api.Com.dll"))

        from Cappta.Gp.Api.Com import ClienteCappta

        self.clienteCappta = ClienteCappta()
        os.chdir(old_dir)
        
        if self.env == 2:
            logger.info(">>>>> Ambiente de homologação ativado! <<<<<")

    def process(self, bus_msg, pos_id, order_id, operator, tender_type, amount, fiscal_date, fiscal_time, tender_id):
        from Cappta.Gp.Api.Com.Model import DetalhesCredito, IMensagem, IRespostaTransacaoPendente, \
            IRequisicaoParametro, IRespostaOperacaoAprovada, IRespostaOperacaoRecusada

        logger.debug("POS %s - Iniciando pagamento" % (str(self.pos_id if self.env == 1 else 53)))
        ret = self.clienteCappta.AutenticarPdv(self.cnpj, self.pos_id if self.env == 1 else 53, self.auth_key)
        if ret == 0:
            logger.debug("POS %s - Autenticação com sucesso." % (str(self.pos_id if self.env == 1 else 53)))
            self.clienteCappta.IniciarMultiCartoes(9)
            tender_type = int(tender_type)

            if tender_type == 2:  # Debito
                ret = self.clienteCappta.PagamentoDebito(float(amount))
            elif tender_type == 1:  # Credito
                details = DetalhesCredito()
                ret = self.clienteCappta.PagamentoCredito(float(amount), details)
            if ret != 0:
                self.callback(bus_msg, pos_id, ret, "")
                return

            tef_loop_variable = self.clienteCappta.IterarOperacaoTef()
            while True:
                if isinstance(tef_loop_variable, IMensagem):
                    message = IMensagem(tef_loop_variable)
                    msg = message.Descricao
                    self.callback(message, str(self.pos_id), msg, "MENSAGEM")
                    time.sleep(0.5)

                elif isinstance(tef_loop_variable, IRespostaTransacaoPendente):
                    pending_transactions = IRespostaTransacaoPendente(tef_loop_variable)
                    msg = pending_transactions.Mensagem
                    parameter = self.callback(bus_msg, pos_id, str(msg.encode('ascii', 'ignore')), "TRANSACAO_PENDENTE")
                    ret = self.clienteCappta.EnviarParametro(parameter, 1)

                elif isinstance(tef_loop_variable, IRequisicaoParametro):
                    req_parameter = IRequisicaoParametro(tef_loop_variable)
                    msg = req_parameter.Mensagem.encode('utf-8')
                    if "Digite" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_NUMERO_CARTAO")
                    elif "Validade" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_VALIDADE")
                    elif "desconecte" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_DESCONECTAR_PINPAD")
                    elif "cancelar" in msg or "Cancelada" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_ACAO")
                    elif "Seguranca" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_CODIGO_SEGURANÇA")
                    elif "indisponível" in msg:
                        parameter = self.callback(bus_msg, str(self.pos_id), msg, "REQUISICAO_ACAO")
                    else:
                        parameter = 0
                    if parameter == "CANCELA":
                        ret = self.clienteCappta.EnviarParametro("", 2)
                    else:
                        ret = self.clienteCappta.EnviarParametro(parameter, 1)

                elif isinstance(tef_loop_variable, IRespostaOperacaoAprovada) or isinstance(tef_loop_variable, IRespostaOperacaoRecusada):
                    break

                tef_loop_variable = self.clienteCappta.IterarOperacaoTef()

            if isinstance(tef_loop_variable, IRespostaOperacaoAprovada):
                approved_payment = IRespostaOperacaoAprovada(tef_loop_variable)
                client_slip = approved_payment.CupomCliente
                customer_slip = approved_payment.CupomLojista
                auth_code = str(approved_payment.CodigoAutorizacaoAdquirente)
                nome_instituicao = str(approved_payment.NomeBandeiraCartao)
                card_bin = str(approved_payment.NumeroCartaoCliente)[:6]
                rede_autorizadora = ""
                transaction_processor = ""
                bandeira = str(approved_payment.CodigoBandeiraCartao)

                b64_receipt_merchant = base64.b64encode(str(customer_slip).replace("\"", ""))
                b64_receipt_customer = base64.b64encode(str(client_slip).replace("\"", ""))
                response = CapptaProcessor.RESPONDE_XML % (nome_instituicao, ret, card_bin, auth_code, amount, rede_autorizadora, "", bandeira, b64_receipt_merchant, b64_receipt_customer, transaction_processor)
                logger.debug("POS %s - Operação aprovada. Order %s" % (str(self.pos_id), str(order_id)))
                return True, response

            elif isinstance(tef_loop_variable, IRespostaOperacaoRecusada):
                operacao = IRespostaOperacaoRecusada(tef_loop_variable)
                response = operacao.Motivo.encode('utf-8')
                logger.debug("POS %s - Operação recusada. Order: %s. Motivo: %s" % (str(self.pos_id), str(order_id), response))
                response = "<EftXml Result=\"%s\" />" % response
                return True, response
        else:
            logger.error("Falha ao autenticar pdv %s - Código de erro %s" % (str(self.pos_id), str(ret)))
            response = "%s" % self.retorno[ret] + ". Código de erro %s" % str(ret)
            response = "<EftXml Result=\"%s\" />" % response
            return True, response

    def finalizar(self, pos_id, order_id, data_fiscal, hora_fiscal, status):
        if status == 1:
            self.clienteCappta.ConfirmarPagamentos()
            logger.debug("POS %s - Pagamentos confirmados. Order: %s" % (str(self.pos_id), str(order_id)))
        else:
            self.clienteCappta.DesfazerPagamentos()
            logger.debug("POS %s - Pagamentos cancelados. Order: %s" % (str(self.pos_id), str(order_id)))

    def reprint(self, bus_msg, pos_id, slip_type):
        # TODO: Implement CAPPTA reprint
        return

    def cancel(self, bus_msg, pos_id, password, control_number):
        # TODO: Implement CAPPTA cancel
        return
