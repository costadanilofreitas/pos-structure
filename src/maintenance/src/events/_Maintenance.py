# -*- coding: utf-8 -*-

import errno
import logging
import os
import re
import shutil
import time
from base64 import b64decode
from datetime import datetime
from threading import Condition
from xml.etree import cElementTree as eTree

import iso8601
from msgbus import MBEasyContext, TK_HV_RESTART, TK_CMP_TERM_NOW, FM_PARAM, MBTimeout, MBException
from old_helper import convert_from_localtime_to_utc
from persistence import Driver
from typing import Tuple, Any

logger = logging.getLogger("Maintenance")

SLEEP_CONDITION = Condition()


class MaintenanceProcessor(object):
    def __init__(self, mbcontext, comp_no, start_hour, end_hour):
        # type: (MBEasyContext, int, int, int) -> None
        super(MaintenanceProcessor, self).__init__()

        self.mbcontext = mbcontext
        self.number = comp_no
        self.start_hour = start_hour
        self.end_hour = end_hour

        self.fiscal_xml_path = None
        self.audit_log_path = None
        self.fiscal_sent_path = None
        self.days_to_purge_audit_log = None

        self.hv_timeout = 10000000

    def set_server_parameters(self, fiscal_path, audit_path, fiscal_sent_path, days_to_purge_audit_log):
        self.fiscal_xml_path = fiscal_path
        self.audit_log_path = audit_path
        self.fiscal_sent_path = fiscal_sent_path
        self.days_to_purge_audit_log = days_to_purge_audit_log

    def delete_files(self, files_to_delete):
        logger.info("Delete files process started. files_to_delete: {}".format(files_to_delete))
        try:
            # POS
            if self.number != 0:
                for file_name in files_to_delete:
                    dirname = os.path.dirname(file_name)
                    filename = os.path.basename(file_name)
                    if os.path.isdir(dirname):
                        for f in os.listdir(dirname):
                            if re.search(filename, f):
                                os.remove(os.path.join(dirname, f))
            # Server
            else:
                return
        except OSError as _:
            logger.exception("Error deleting files. files_to_delete: {}".format(files_to_delete))

    def delete_dirs(self, dirs_to_delete):
        logger.info("Delete directories process started. dirs_to_delete: {}".format(dirs_to_delete))
        try:
            # POS
            if self.number != 0:
                for dir_name in dirs_to_delete:
                    os.path.exists(dir_name) and shutil.rmtree(dir_name)
            # Server
            else:
                return
        except OSError as _:
            logger.exception("Error deleting directories. dirs_to_delete: {}".format(dirs_to_delete))

    def clean_audit_log(self, _):
        logger.info('Clean Audit log process started')
        if None in [self.audit_log_path, self.days_to_purge_audit_log]:
            return

        search_folder = self.audit_log_path
        if os.path.exists(search_folder):
            files_to_delete = filter(lambda x: x.startswith('mwapp_audit') and x.endswith('log'), (map(lambda x: x[2], os.walk(search_folder))[0]))
            self._remove_files(files_to_delete, search_folder)

    def handle_terminate_request(self, _):
        # type: (Any) -> Tuple[bool, str]
        try:
            m = self.mbcontext.MB_SendMessage(self.mbcontext.hv_service, TK_CMP_TERM_NOW, FM_PARAM, str(self.hv_timeout))
            return True, m.data
        except (MBTimeout, MBException) as _:
            return False, "Error trying to close the system"

    def handle_restart_request(self, _):
        # type: (Any) -> Tuple[bool, str]
        try:
            m = self.mbcontext.MB_SendMessage(self.mbcontext.hv_service, TK_HV_RESTART, FM_PARAM, str(self.hv_timeout))
            return True, m.data
        except (MBTimeout, MBException) as _:
            return False, "Error trying to restart the system"

    def save_file_from_nfce_request(self, conn, xml_request_file=None, xml_request=None, order_id="", pos_id=""):
        if None in [self.fiscal_xml_path, self.fiscal_sent_path]:
            return

        path_enviados = os.path.join(self.fiscal_xml_path, self.fiscal_sent_path)

        files_to_remove = []
        if xml_request_file:
            xml_request_file_full_path = os.path.join(path_enviados, xml_request_file)
            xml_request = self.remove_ns_from_xml(xml_file=xml_request_file_full_path)

            files_to_remove.append(xml_request_file_full_path)
            files_to_remove.append(xml_request_file_full_path.replace("request", "response"))
            files_to_remove.append(xml_request_file_full_path.replace("request", "nfe_proc"))

            index1 = xml_request_file.find("_order")
            if "_conti" in xml_request_file:
                index2 = xml_request_file.find("_conti")
            else:
                index2 = xml_request_file.find(".xml")
            order_id = xml_request_file[index1 + 6: index2].zfill(9)

            index1 = xml_request_file.find("_pos")
            index2 = xml_request_file.find("_order")
            pos_id = xml_request_file[index1 + 4: index2].zfill(2)
        else:
            xml_request = self.remove_ns_from_xml(xml_text=xml_request)

        index1 = xml_request.index("<NFe")
        index2 = xml_request.index("</NFe>")
        nfce_xml = xml_request[index1:index2 + 6]
        nfce_xml = nfce_xml.replace("<Signature>", "<Signature xmlns=\"http://www.w3.org/2000/09/xmldsig#\">")

        parsed_xml = eTree.XML(nfce_xml)
        serie = parsed_xml.find("infNFe/ide/serie").text.zfill(3)
        numero_nota = parsed_xml.find("infNFe/ide/nNF").text.zfill(9)
        cfe_code = parsed_xml.find("infNFe").get("Id")
        file_name = "{0}_{1}_{2}_nfe_proc_pos{3}_{4}.xml".format(serie, numero_nota, order_id, pos_id, cfe_code)

        data_emissao_str = parsed_xml.find("infNFe/ide/dhEmi").text
        data_emissao = iso8601.parse_date(data_emissao_str)
        data_emissao_utc = convert_from_localtime_to_utc(data_emissao)
        save_path = os.path.join(path_enviados, data_emissao.strftime("%Y"), data_emissao.strftime("%m"), data_emissao.strftime("%d"))

        order_conn = None
        try:
            order_conn = Driver().open(self.mbcontext, dbname=str(pos_id))
            count = [int(x.get_entry(0)) for x in order_conn.select("select count(1) from Orders where OrderId = {0}".format(order_id))][0]
            if count > 0:
                query = "insert or replace into OrderCustomProperties (OrderId, Key, Value) VALUES ({0}, '{1}', '{2}')"
                order_conn.query(query.format(order_id, "FISCALIZATION_DATE", data_emissao_utc.strftime("%Y-%m-%dT%H:%M:%S")))
        finally:
            if order_conn is not None:
                order_conn.close()

        nfe_proc = "<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\" versao=\"3.10\">"

        # Obtemos o XML Response do banco
        try:
            lines = [x.get_entry(0) for x in conn.select("SELECT XMLResponse FROM fiscal.FiscalData WHERE OrderId = %s" % str(order_id))]
            if not lines:
                raise Exception("Order not found in database")

            response = lines[0]
            xml_response = b64decode(response)
            xml_response = re.sub('\\sxmlns="[^"]+"', '', xml_response, 0)
            index = xml_response.index("<protNFe")
            index2 = xml_response.index("</protNFe>")
            prot_nfe = xml_response[index:index2 + 10]
        except Exception as _:
            nnf = re.search(r'NFe\d+', nfce_xml).group()[3:]
            prot_nfe = "<protNFe versao=\"3.10\">" \
                       "<infProt>" \
                       "<tpAmb>1</tpAmb>" \
                       "<verAplic></verAplic>" \
                       "<chNFe>%s</chNFe>" \
                       "<dhRecbto></dhRecbto>" \
                       "<nProt></nProt>" \
                       "<digVal></digVal>" \
                       "<cStat>100</cStat>" \
                       "<xMotivo>Autorizado o uso da NF-e</xMotivo>" \
                       "</infProt>" \
                       "</protNFe>" % nnf
        nfe_proc += nfce_xml + prot_nfe + "</nfeProc>"

        if nfe_proc is not None:
            self._make_sure_path_exists(save_path)
            with open(os.path.join(save_path, file_name), "w+") as save_file:
                save_file.write(nfe_proc)

        for file_to_remove in files_to_remove:
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

    def save_file_from_sat_response(self, xml_response_file=None, xml_response=None, order_id="", pos_id="", sat_num=""):
        if None in [self.fiscal_xml_path, self.fiscal_sent_path]:
            return

        path_enviados = os.path.join(self.fiscal_xml_path, self.fiscal_sent_path)

        files_to_remove = []
        if xml_response_file:
            sat_xml_request = xml_response_file.replace("response", "request")
            cfe_index = sat_xml_request.index("_cfe")
            sat_xml_request = sat_xml_request[0:cfe_index]
            sat_xml_request += ".xml"

            xml_response_file_fullpath = os.path.join(path_enviados, xml_response_file)
            xml_response = self.remove_ns_from_xml(xml_file=xml_response_file_fullpath)

            files_to_remove.append(os.path.join(path_enviados, sat_xml_request))
            files_to_remove.append(os.path.join(path_enviados, xml_response_file))

            index1 = xml_response_file.find("_order")
            index2 = xml_response_file.find("_cfe")
            order_id = xml_response_file[index1 + 6: index2]

            index1 = xml_response_file.find("_SAT")
            index2 = xml_response_file.find("_pos")
            sat_num = xml_response_file[index1 + 4: index2]

            index1 = xml_response_file.find("_pos")
            index2 = xml_response_file.find("_order")
            pos_id = xml_response_file[index1 + 4: index2].zfill(2)
        else:
            xml_response = self.remove_ns_from_xml(xml_text=xml_response)

        sat_xml_str = xml_response
        if sat_xml_str != '':
            sat_xml = eTree.XML(sat_xml_str)

            data_emissao_str = sat_xml.find("infCFe/ide/dEmi").text
            hora_emissao_str = sat_xml.find("infCFe/ide/hEmi").text
            data_emissao = datetime.strptime(data_emissao_str + hora_emissao_str, "%Y%m%d%H%M%S")
            data_emissao_utc = convert_from_localtime_to_utc(data_emissao)

            numero_nota = sat_xml.find("infCFe/ide/nCFe").text

            sat_xml_nfe_proc = "nfe_proc_pos{0}_order{1}.xml".format(pos_id, order_id)
            files_to_remove.append(os.path.join(path_enviados, sat_xml_nfe_proc))

            order_conn = None
            try:
                order_conn = Driver().open(self.mbcontext, dbname=str(pos_id))
                count = [int(x.get_entry(0)) for x in order_conn.select("select count(1) from Orders where OrderId = {0}".format(order_id))][0]
                if count > 0:
                    query = "insert or replace into OrderCustomProperties (OrderId, Key, Value) VALUES ({0}, '{1}', '{2}')"
                    order_conn.query(query.format(order_id, "FISCALIZATION_DATE", data_emissao_utc.strftime("%Y-%m-%dT%H:%M:%S")))
            finally:
                if order_conn is not None:
                    order_conn.close()
            cfe_code = sat_xml.find("infCFe").get("Id")
            new_response_file_name = "S{0}_{1}_{2}_response_pos{3}_{4}.xml".format(sat_num[-2:], str(numero_nota).zfill(9), str(order_id).zfill(9), str(pos_id).zfill(2), cfe_code)
            save_path = os.path.join(path_enviados, data_emissao_str[0:4], data_emissao_str[4:6], data_emissao_str[6:8])

            self._make_sure_path_exists(save_path)
            with open(os.path.join(save_path, new_response_file_name), "w+") as save_file:
                save_file.write(sat_xml_str)

        for file_to_remove in files_to_remove:
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

    def is_inside_maintenance_window(self):
        current_hour = int(datetime.now().strftime("%H"))

        if self.end_hour <= self.start_hour:
            if current_hour < self.end_hour or current_hour >= self.start_hour:
                return True
        else:
            if self.start_hour <= current_hour < self.end_hour:
                return True

        return False

    def _remove_files(self, file_list, folder):
        current_time = time.time()
        for file_name in file_list:
            file_path = os.path.join(folder, file_name)
            creation_time = os.path.getmtime(file_path)
            if (current_time - creation_time) // (24 * 3600) >= self.days_to_purge_audit_log:
                os.unlink(file_path)
                logger.info('Removed - {}'.format(file_name))

    @staticmethod
    def remove_ns_from_xml(xml_file="", xml_text=None):
        try:
            # Read the contents of the XML file into xmlstring
            with open(xml_file) as f:
                xml_string = f.read()
        except IOError:
            if xml_text:
                xml_string = xml_text
            else:
                return None
        # Remove the default namespace definition (xmlns="http://some/namespace")
        xml_string = re.sub('\\sxmlns="[^"]+"', '', xml_string, 0)

        return xml_string

    @staticmethod
    def _make_sure_path_exists(path):
        try:
            os.makedirs(path)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
        return
