# -*- coding: utf-8 -*-
import os
import sys
import base64
import msgbus
import six
import logging
import sysactions

from sysactions import set_custom
from fiscalinterface import FiscalProcessor
from xml.etree import cElementTree as eTree
from threading import Thread, Condition
from msgbus import MBException, FM_STRING, FM_PARAM, TK_SYS_ACK, SE_NOTFOUND
from systools import sys_log_exception, sys_log_error
from bustoken import TK_SAT_PROCESS_REQUEST, TK_SAT_STATUS_REQUEST, TK_SAT_CANCEL_SALE
from old_helper import convert_from_localtime_to_utc
from pos_model import OrderParser
from satbuilder import CfeBuilder, ContextKeys
from datetime import datetime
from common import FiscalParameterController
from pos_util import SaleLineUtil

logger = logging.getLogger("FiscalWrapper")


class SatRequestBuilder:
    def __init__(self, mbcontext, crt, cnpj_sw, sign_ac, cnpj_contribuinte, inscr_estadual, order_parser, fiscal_parameter_controller, sale_line_util, cfe_builder, is_mfe):
        self.crt = crt
        self.mbcontext = mbcontext
        self.cnpj_sw = cnpj_sw
        self.sign_ac = sign_ac
        self.cnpj_contribuinte = cnpj_contribuinte
        self.inscr_estadual = inscr_estadual
        self.order_parser = order_parser  # type: OrderParser
        self.fiscal_parameter_controller = fiscal_parameter_controller  # type: FiscalParameterController
        self.sale_line_util = sale_line_util  # type: SaleLineUtil
        self.cfe_builder = cfe_builder  # type: CfeBuilder
        self.is_mfe = is_mfe

    def get_sat_info(self):
        return self.cnpj_sw, self.sign_ac

    def build_request(self, pos_id, order_xml, tenders):
        # type: (str, eTree.Element, list) -> unicode
        order = self.order_parser.parse_order(order_xml)

        # Geracao do XML
        context = {}
        xml = self.cfe_builder.build_xml(order, context)
        return xml


class SatService:
    def __init__(self, service_name):
        self.service_name = service_name
        self.available = True


class SatServiceFinder:
    def __init__(self, mbcontext, max_sat_number, sleep_time):
        # type: (msgbus.MBEasyContext) -> None
        self.mbcontext = mbcontext
        self.max_sat_number = max_sat_number
        self.sleep_time = sleep_time

        self.search_thread = None  # type: Thread
        self.search_thread_condition = Condition()
        self.search_thread_running = False
        self.available_sats = {}  # type: dict{str, SatService}
        self.available_sats_keys = []
        self.next_sat_index = 0
        self.available_sats_lock = Condition()

        self.service_name_initial = "SAT"

        self.search_sat_modules()
        self.start_search_thread()

    def find_and_lock_sat_service(self, order_id):
        # type: () -> str
        with self.available_sats_lock:
            if not self.available_sats:
                with self.search_thread_condition:
                    self.search_thread_condition.notify()
                raise Exception("No SAT modules available")

            initial_sat_index = self.next_sat_index

            try:
                sat_service_name = self.available_sats_keys[self.next_sat_index]
            except IndexError:
                logger.exception("Erro ao acessar SAT com indice %d. Sats disponiveis: %d" % (self.next_sat_index, len(self.available_sats_keys)))
                self.next_sat_index = 0
                initial_sat_index = len(self.available_sats_keys)
                sat_service_name = self.available_sats_keys[self.next_sat_index]
            else:
                self.next_sat_index += 1
                if self.next_sat_index >= len(self.available_sats):
                    self.next_sat_index = 0

            while not self.available_sats[sat_service_name].available:
                sat_service_name = self.available_sats_keys[self.next_sat_index]
                self.next_sat_index += 1
                if self.next_sat_index >= len(self.available_sats):
                    self.next_sat_index = 0

                if self.next_sat_index == initial_sat_index:
                    # Todos os SATs disponiveis estao ocupados, vamos esperar alguem liberar algum
                    self.available_sats_lock.wait()

                    # Alguem liberou um sat, vamos tentar pega-lo
                    initial_sat_index = self.next_sat_index
                    sat_service_name = self.available_sats_keys[self.next_sat_index]

            self.available_sats[sat_service_name].available = False
            return sat_service_name

    def unlock_sat_service(self, sat_service_name):
        # type: (str) -> None
        with self.available_sats_lock:
            if sat_service_name in self.available_sats:
                self.available_sats[sat_service_name].available = True

                # Como liberamos um SAT, vamos notificar para caso alguem esteja esperando
                self.available_sats_lock.notify()

    def sat_unavailable(self, sat_service_name):
        # type: (str) -> None
        with self.available_sats_lock:
            if sat_service_name in self.available_sats:
                del self.available_sats[sat_service_name]
                self.available_sats_keys.remove(sat_service_name)
                posid = int(sat_service_name[3:])
                set_custom(posid, 'SAT_STATUS', '2')

                # Removemos um SAT - Vamos arrumar os indices
                self._fix_sat_index()

    def search_sat_modules(self):
        logger.debug("Start Search SAT Function")

        now_available = {}
        for i in range(0, self.max_sat_number + 1):
            sat_service_name = "SAT%s" % str(i).zfill(2)

            try:
                # TODO: definir um timeout que minimize ao maximo o numero de falsos positivos sem comprometer o funcionamento do sistema
                ret = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_STATUS_REQUEST, format=FM_PARAM, timeout=100 * 100000)
                if ret.data == "OK":
                    now_available[sat_service_name] = SatService(sat_service_name)
                    try:
                        set_custom(i, 'SAT_STATUS', '1') if i is not 0 else None
                    except:
                        pass
                else:
                    sys_log_error("{0} not available: {1}".format(sat_service_name, ret.data))
                    try:
                        set_custom(i, 'SAT_STATUS', '2') if i is not 0 else None
                    except:
                        pass
            except MBException as e:
                try:
                    set_custom(i, 'SAT_STATUS', '3') if i is not 0 else None
                except:
                    pass
                if e.errorcode != SE_NOTFOUND:
                    sys_log_exception(e.message)

        with self.available_sats_lock:
            # Primeiro removemos os que estavam disponiveis e agora nao estao mais
            sats_to_remove = []
            for sat_service_name in self.available_sats:  # type: str
                if sat_service_name not in now_available:
                    sats_to_remove.append(sat_service_name)

            for sat_service_name in sats_to_remove:
                del self.available_sats[sat_service_name]
                self.available_sats_keys.remove(sat_service_name)

            # Agora adicionamos os que passaram a estar disponiveis
            sats_novos = False
            for sat_service_name in now_available:  # type: str
                if sat_service_name not in self.available_sats:
                    sat = now_available[sat_service_name]  # type: SatService

                    self.available_sats[sat.service_name] = sat
                    self.available_sats_keys.append(sat.service_name)

                    sats_novos = True

            # Removemos um SAT - Vamos arrumar os indices
            self._fix_sat_index()

            if sats_novos:
                # Como temos SATs novos disponiveis, vamos avisar caso algume thread esteja esperando
                self.available_sats_lock.notify()
        logger.debug("End Search SAT Function")

    def start_search_thread(self):
        self.search_thread_running = True
        self.search_thread = Thread(target=self._search_thread_loop)
        self.search_thread.daemon = True
        self.search_thread.start()
        pass

    def stop_search_thread(self):
        if self.search_thread_running:
            with self.search_thread_condition:
                self.search_thread_running = False
                self.search_thread_condition.notifyAll()

    def _search_thread_loop(self):
        while self.search_thread_running:
            with self.search_thread_condition:
                if not self.available_sats:
                    self.search_thread_condition.wait(15)
                else:
                    self.search_thread_condition.wait(self.sleep_time)
            self.search_sat_modules()

    def _fix_sat_index(self):
        # Atualizamos o indice, pois houve alguma remoção de SATs
        if self.next_sat_index >= len(self.available_sats):
            self.next_sat_index = len(self.available_sats) - 1

            # Não permirte que o índice fique negativo
            if self.next_sat_index < 0:
                self.next_sat_index = 0


class MfeServiceFinder(SatServiceFinder):
    def find_and_lock_sat_service(self, order_id):
        # type: () -> str
        with self.available_sats_lock:
            if not self.available_sats:
                raise Exception("No SAT modules available")

            sat_service_name = self.available_sats_keys[int(order_id) % len(self.available_sats_keys)]

            while not self.available_sats[sat_service_name].available:
                self.available_sats_lock.wait()

            self.available_sats[sat_service_name].available = False
            return sat_service_name


class SatProcessor(FiscalProcessor):
    def __init__(self, mbcontext, sat_service_finder, sat_request_builder, fiscal_sent_dir):
        # type: (msgbus.MBEasyContext, SatServiceFinder, SatRequestBuilder, list) -> SatProcessor
        super(SatProcessor, self).__init__()

        self.mbcontext = mbcontext
        self.sat_service_finder = sat_service_finder
        self.sat_request_builder = sat_request_builder
        self.last_sat_used = {}
        self.fiscal_sent_dir = fiscal_sent_dir
        sysactions.mbcontext = self.mbcontext

    def get_sat_info(self):
        return self.sat_request_builder.get_sat_info()

    def request_fiscal(self, posid, order, tenders, paf=False):
        # type: (str, eTree.Element) -> eTree.Element
        request = self.sat_request_builder.build_request(posid, order, tenders)  # type: str

        sat_service_name = self.sat_service_finder.find_and_lock_sat_service(order.get("orderId"))

        self.last_sat_used[posid] = sat_service_name

        try:
            order_id = order.get("orderId")
            order_id = order_id.zfill(9)

            dir_enviadas = os.path.join(self.fiscal_sent_dir, "Enviados")
            if not os.path.exists(dir_enviadas):
                os.makedirs(dir_enviadas)
            req = '\0'.join([posid, order.attrib["orderId"], request.encode('utf-8')])
            msg = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_PROCESS_REQUEST, format=FM_STRING, data=req)

            # Liberamos o SAT para processar as proximas requisicoes
            self.sat_service_finder.unlock_sat_service(sat_service_name)

            if msg.token == TK_SYS_ACK:
                ret_xml = eTree.XML(msg.data)

                element = ret_xml.find("XmlRequest").text
                # Arrumamos o padding, que pode ter vindo errado e o base64 exige que o mesmo esteja com padding correto
                logger.debug("OrderId: %s; request size: %d..." % (order_id, len(element)))
                padded = element + "=" * ((4 - len(element) % 4) % 4)
                logger.debug("OrderId: %s; padded size: %d..." % (order_id, len(padded)))
                base64_xml = base64.b64decode(padded)
                logger.debug("OrderId: %s; base64_xml: %s..." % (order_id, base64_xml[:10]))
                req_xml = eTree.XML(base64_xml)

                num_nota_cfe_el = req_xml.find("infCFe/ide/nCFe")
                num_nota_cfe = num_nota_cfe_el.text.zfill(9) if num_nota_cfe_el is not None else '000000000'
                data_emissao = req_xml.find("infCFe/ide/dEmi").text
                hora_emissao = req_xml.find("infCFe/ide/hEmi").text
                emissao_date = convert_from_localtime_to_utc(datetime.strptime(data_emissao + hora_emissao, "%Y%m%d%H%M%S"))
                dir_nota = os.path.join(dir_enviadas, data_emissao[0:4], data_emissao[4:6], data_emissao[6:8])
                if not os.path.exists(dir_nota):
                    os.makedirs(dir_nota)

                sysactions.get_posot(sysactions.get_model(posid)).setOrderCustomProperty("FISCALIZATION_DATE", emissao_date.strftime("%Y-%m-%dT%H:%M:%S"))

                # Liberamos o SAT para processar as proximas requisicoes
                self.sat_service_finder.unlock_sat_service(sat_service_name)

                cfe_code = ret_xml.find("FiscalData").find("satkey").text

                response_file_dir = os.path.join(dir_nota, "S{0}_{1}_{2}_response_pos{3}_CFe{4}.xml".format(sat_service_name[-2:], num_nota_cfe, order_id, str(posid).zfill(2), cfe_code))
                logger.debug("OrderId: %s; response_file_dir: %s" % (order_id, response_file_dir))
                with open(response_file_dir, "w+") as response_file:
                    logger.debug("OrderId: %s; response_file_dir was opened for writing" % order_id)
                    response_file.write(base64_xml)
                    logger.debug("OrderId: %s; response_file_dir was written" % order_id)
                logger.debug("OrderId: %s; response_file_dir was closed" % order_id)
                return ret_xml
            else:
                dir_erro = os.path.join(self.fiscal_sent_dir, "Erros")
                if not os.path.exists(dir_erro):
                    os.makedirs(dir_erro)
                # Salvamos o arquivo com erro em arquivo, no formato request_sat<satname>_pos<posid>_order<orderid>_erro
                logger.debug("OrderId: %s; error file was opened for writing" % order_id)
                request_erro = open(os.path.join(dir_erro, "{0}_request_{1}_pos{2}_order{3}_erro.xml".format(order_id, sat_service_name, str(posid).zfill(2), order.get("orderId"))), "w+")
                request_erro.write(request)
                logger.debug("OrderId: %s; error file was written" % order_id)
                request_erro.close()
                logger.debug("OrderId: %s; error file was closed" % order_id)
                raise Exception(msg.data)

        except Exception as e:
            sys_log_exception(e.message)
            self.sat_service_finder.sat_unavailable(sat_service_name)
            raise six.reraise(Exception, e, sys.exc_info()[2])

    def do_validation(self, get_days_to_expiration=None):
        return True, "OK"

    def get_fiscal_sent_dir(self):
        return self.fiscal_sent_dir

    def terminate(self):
        self.sat_service_finder.stop_search_thread()

    def cancel_sale(self, order_data):
        sat_service = "SAT" + order_data[0]
        cancel_data = self.build_cancel_xml(order_data[1])
        msg = self.mbcontext.MB_EasySendMessage(sat_service, TK_SAT_CANCEL_SALE, format=FM_PARAM, timeout=100 * 100000, data=str(cancel_data))
        if msg.token == TK_SYS_ACK:
            ret_xml = eTree.XML(msg.data)

            element = ret_xml.find("XmlResponse").text
            message = ret_xml.find("Message").text
            # Se veio XML Response, arrumamos o padding, que pode ter vindo errado e o base64 exige que o mesmo esteja com padding correto e salvamos em arquivo
            if element:
                padded = element + "=" * ((4 - len(element) % 4) % 4)
                base64_xml = base64.b64decode(padded)
                num_nota_cfe = cancel_data[1][34:40]
                idx_start = base64_xml.find("<dEmi>") + 6
                idx_final = base64_xml.find("</dEmi>")
                data_emissao = base64_xml[idx_start:idx_final]
                dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[4:6], data_emissao[6:8])
                with open(os.path.join(self.fiscal_sent_dir, "Enviados", dir_arquivo, "S{0}_{1}_cfe_cancelamento.xml".format(sat_service[-2:], num_nota_cfe)), "w+") as cfe_proc_file:
                    cfe_proc_file.write(base64_xml)
            return True, message
        else:
            return False, msg.data

    def build_cancel_xml(self, order_request):
        sale_request_xml = eTree.XML(base64.b64decode(order_request + "==="))

        chcanc = sale_request_xml.find("infCFe").attrib.get("Id")
        cnpj = self.sat_request_builder.cnpj_contribuinte if not self.sat_request_builder.is_mfe \
            else self.sat_request_builder.cnpj_sw
        signac = self.sat_request_builder.sign_ac
        posid = sale_request_xml.find("infCFe").find("ide").find("numeroCaixa").text

        cancel_xml = "<CFeCanc>" \
                     "<infCFe chCanc=\"{chcanc}\">" \
                     "<ide>" \
                     "<CNPJ>{cnpj}</CNPJ>" \
                     "<signAC>{signac}</signAC>" \
                     "<numeroCaixa>{posid}</numeroCaixa>" \
                     "</ide>" \
                     "<emit/>" \
                     "<dest/>" \
                     "<total/>" \
                     "</infCFe>" \
                     "</CFeCanc>" \
            .format(chcanc=chcanc, cnpj=cnpj, signac=signac, posid=posid)
        return cancel_xml, chcanc
