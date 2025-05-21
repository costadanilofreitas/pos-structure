# -*- coding: utf-8 -*-

import logging
import os

from persistence import Driver


logger = logging.getLogger("Maintenance")


class AppendFiscalFilesProcessor(object):
    def __init__(self, mbcontext, number, fiscal_path, fiscal_sended):
        self.mbcontext = mbcontext
        self.number = number
        self.files_appended = False

        self.fiscal_xml_path = fiscal_path
        self.fiscal_sended = fiscal_sended
        self.maintenance_processor = None

    def set_server_parameters(self, maintenance_processor):
        self.maintenance_processor = maintenance_processor

    def append_fiscal_files(self):
        if None in [self.fiscal_xml_path, self.fiscal_sended]:
            return

        try:
            # Server
            if self.number == 0:
                path_enviados = os.path.join(self.fiscal_xml_path, self.fiscal_sended)
                self._append_response_fiscal(path_enviados)
            # POS
            else:
                pass

        except Exception as _:
            logger.exception("Error appending fiscal files")

    def _append_response_fiscal(self, path_enviados):
        # find fiscal xml request files
        if os.path.exists(path_enviados):
            nfce_xml_requests = filter(lambda x: x.startswith('request') and "SAT" not in x and x.endswith('xml'),
                                       [f for f in os.listdir(path_enviados) if os.path.isfile(os.path.join(path_enviados, f))])
            sat_xml_responses = filter(lambda x: x.startswith('response') and "cfe" in x and x.endswith('xml'),
                                       [f for f in os.listdir(path_enviados) if os.path.isfile(os.path.join(path_enviados, f))])

            logger.info("Found '{0}' files to process".format(len(nfce_xml_requests) + len(sat_xml_responses)))

            conn = None
            try:
                conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")
                for xml_request_file in nfce_xml_requests:
                    if not self.maintenance_processor.is_inside_maintenance_window():
                        return

                    try:
                        self.maintenance_processor.save_file_from_nfce_request(xml_request_file)
                    except Exception as _:
                        logger.exception("Error processing file: %s" % xml_request_file)
                        continue

                for sat_xml_response in sat_xml_responses:
                    if not self.maintenance_processor.is_inside_maintenance_window():
                        return

                    try:
                        self.maintenance_processor.save_file_from_sat_response(sat_xml_response)
                    except Exception as _:
                        logger.exception("Error processing file: %s" % sat_xml_response)
                        continue
            finally:
                if conn:
                    conn.close()
