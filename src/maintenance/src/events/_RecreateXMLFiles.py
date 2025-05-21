# -*- coding: utf-8 -*-

import base64
import logging
import os
from xml.etree import cElementTree as eTree

import iso8601
from persistence import Driver


logger = logging.getLogger("Maintenance")


class RecreateXMLFilesProcessor(object):
    def __init__(self, mbcontext, comp_no, fiscal_xml_path, fiscal_sended):
        self.mbcontext = mbcontext
        self.comp_no = comp_no
        self.fiscal_xml_path = fiscal_xml_path
        self.fiscal_sended = fiscal_sended

        self.maintenance_processor = None

    def set_server_parameters(self, maintenance_processor):
        self.maintenance_processor = maintenance_processor

    def recreate_response_fiscal(self, recreate_days="30"):
        if self.comp_no != 0:
            return

        conn = None
        errors = []
        try:
            conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")
            total_rows = int(self._get_count_rows_recreate_file(recreate_days) or 0)

            limit_start = 0
            while total_rows > 0:
                if (total_rows - 1000) < 0:
                    total_rows = 0
                else:
                    total_rows -= 1000

                cursor = conn.select("""SELECT PosId, OrderId, NumeroSat, date(datetime(datanota, 'unixepoch')) as data_nota, NumeroNota, XMLRequest, XMLResponse
                     FROM fiscal.FiscalData WHERE SentToBkOffice = 1 and date(datetime(datanota, 'unixepoch')) > date('now', '-{0} day') ORDER BY OrderId LIMIT 1000 OFFSET {1}
                        """.format(recreate_days, str(limit_start)))

                limit_start += 1000

                # Create directories and files
                for row in cursor:
                    try:
                        self._create_file(
                            conn,
                            errors=errors,
                            order_id=row.get_entry("OrderId").zfill(9),
                            pos_id=row.get_entry("PosId").zfill(2),
                            sat_num=row.get_entry("NumeroSat").zfill(2),
                            xml_request_data=row.get_entry("XMLRequest")
                        )

                    except Exception as ex:
                        errors.append("Error creating file: %s" % str(ex))
                        logger.exception("Error creating file")

        except Exception as ex:
            logger.exception("Error checking sent orders in database")
            return False, str(ex)
        finally:
            if conn:
                conn.close()
        if len(errors) > 0:
            return False, str(errors)
        return True, 'Files processed'

    def recreate_file_number(self, order_id):
        if self.comp_no != 0:
            return

        conn = None
        try:
            conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")

            cursor = conn.select(
                """SELECT 
                PosId, OrderId, NumeroSat, date(datetime(datanota, 'unixepoch')) as data_nota, NumeroNota, XMLRequest, XMLResponse
                FROM fiscal.FiscalData WHERE orderid = '{}';""".format(order_id))
            if cursor.rows() > 0:
                for row in cursor:
                    self._create_file(
                        conn,
                        errors=[],
                        order_id=row.get_entry("OrderId").zfill(9),
                        pos_id=row.get_entry("PosId").zfill(2),
                        sat_num=row.get_entry("NumeroSat").zfill(2),
                        xml_request_data=row.get_entry("XMLRequest")
                    )
            else:
                return False, 'Missing number'
        except Exception as _:
            logger.exception("Error checking sent orders in database")
            return False, "Error processing XML"
        finally:
            if conn:
                conn.close()

        return True, 'File processed with sucess'

    def _get_count_rows_recreate_file(self, days_to_recreate):
        conn = None
        try:
            conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")
            cursor = conn.select("""SELECT count(*) as total FROM FiscalData 
                                    WHERE SentToBkOffice = 1 
                                    and date(datetime(datanota, 'unixepoch')) > date('now', '-{0} day');"""
                                 .format(days_to_recreate))

            for row in cursor:
                return row.get_entry("total")
        except Exception as _:
            logger.exception("Error checking sent orders in database")
        finally:
            if conn:
                conn.close()

    def _create_file(self, conn, errors, order_id, pos_id, sat_num, xml_request_data):
        path_enviados = os.path.join(self.fiscal_xml_path, self.fiscal_sended)

        # Check if file exists
        xml_request = base64.b64decode(xml_request_data) or ''
        xml_request = self.maintenance_processor.remove_ns_from_xml(xml_text=xml_request)
        fiscal_type = None
        if xml_request.find("<NFe") != -1 and xml_request.find("<CFe") == -1:
            fiscal_type = "NFCe"
        if xml_request.find("<NFe") == -1 and xml_request.find("<CFe") != -1:
            fiscal_type = "SAT"

        if not fiscal_type:
            logger.exception("[_create_file] Erro fiscal_type = %s" % fiscal_type)

        save_path = None
        if fiscal_type in "NFCe":
            index1 = xml_request.index("<NFe")
            index2 = xml_request.index("</NFe>")
            nfce_xml = xml_request[index1:index2 + 6]
            nfce_xml = nfce_xml.replace("<Signature>", "<Signature xmlns=\"http://www.w3.org/2000/09/xmldsig#\">")

            parsed_xml = eTree.XML(nfce_xml)
            serie = parsed_xml.find("infNFe/ide/serie").text.zfill(3)

            numero_nota = parsed_xml.find("infNFe/ide/nNF").text.zfill(9)

            data_emissao_str = parsed_xml.find("infNFe/ide/dhEmi").text
            data_emissao = iso8601.parse_date(data_emissao_str)
            save_path = os.path.join(path_enviados, data_emissao.strftime("%Y"), data_emissao.strftime("%m"),
                                     data_emissao.strftime("%d"))
        if fiscal_type in "SAT":
            index1 = xml_request.index("<CFe")
            index2 = xml_request.index("</CFe>")
            nfce_xml = xml_request[index1:index2 + 6]
            nfce_xml = nfce_xml.replace("<Signature>", "<Signature xmlns=\"http://www.w3.org/2000/09/xmldsig#\">")

            parsed_xml = eTree.XML(nfce_xml)
            numero_nota = parsed_xml.find("infCFe/ide/nCFe").text.zfill(9)

            data_emissao_str = parsed_xml.find("infCFe/ide/dEmi").text
            data_emissao = iso8601.parse_date(data_emissao_str)
            save_path = os.path.join(path_enviados, data_emissao.strftime("%Y"), data_emissao.strftime("%m"),
                                     data_emissao.strftime("%d"))

        if not save_path:
            logger.exception("[_create_file] Erro save_path = {}".format(save_path))

        # Save files into bin
        xml_request = base64.b64decode(xml_request_data) or ''

        try:
            if fiscal_type in "SAT":
                self.maintenance_processor.save_file_from_sat_response(None, xml_request, order_id, pos_id, sat_num)
            if fiscal_type in "NFCe":
                self.maintenance_processor.save_file_from_nfce_request(None, xml_request, order_id, pos_id)

        except Exception as ex:
            logger.exception("Error creating order file: %s" % order_id)
            errors.append("Error creating order file: [%s, %s]" % (order_id, str(ex)))
