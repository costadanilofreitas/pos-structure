# -*- coding: utf-8 -*-

import logging
import os
import re
import time
from ctypes import WinDLL
from threading import Thread, Condition

from typing import Optional

logger = logging.getLogger("Sitef")


class SitefServiceFinder(object):
    def __init__(self, mbcontext, sitef_test_processor, sleep_time, sitef_ip_list, id_loja, pos_id):
        self.sitef_test_processor = sitef_test_processor
        self.mbcontext = mbcontext
        self.pos_id = pos_id
        self.id_loja = id_loja
        self.sitef_ip_list = sitef_ip_list
        self.sleep_time = sleep_time

        self.search_thread = None  # type: Thread
        self.search_thread_condition = Condition()
        self.search_thread_running = False
        self.id_terminal = "SW%06d" % 99

        self.available_sitefs = []
        self.next_sitef_index = 0
        self.available_sitef_lock = Condition()

        clisitef_lib = "{BUNDLEDIR}/lib/clisitef32i.dll"
        for var in re.findall("{[a-zA-Z0-9]*}+", clisitef_lib):
            clisitef_lib = clisitef_lib.replace(var, os.environ.get(var.replace('{', '').replace('}', ''), ""))

        self.sitefDll = WinDLL(clisitef_lib)
        self.configuraIntSiTefInterativo = self.sitefDll["ConfiguraIntSiTefInterativo"]
        self.iniciaFuncaoSiTefInterativo = self.sitefDll["IniciaFuncaoSiTefInterativo"]

        self.search_sitef_modules()
        self.start_search_thread()

    def find_sitef_service(self):
        # type: () -> Optional[str]
        logger.debug("Iniciando => find_sitef_service")
        if len(self.available_sitefs) == 0:
            logger.debug("Nenhum IP foi encontrado na lista, retornamos vazio")
            return None
        else:
            logger.debug("Retornando IP => {0}".format(self.available_sitefs[0]))
            return self.available_sitefs[0]

    def sitef_unavailable(self, ip_sitef):
        # type: (str) -> None
        logger.debug("Iniciando => sitef_unavailable")
        logger.debug("Removendo IP da lista de IPs válidos. IP => {0}".format(ip_sitef))
        if ip_sitef in self.available_sitefs:
            self.available_sitefs.remove(ip_sitef)

    def lock_sitef(self):
        self.available_sitef_lock.acquire()

    def release_sitef(self):
        self.available_sitef_lock.release()

    def wakeup_search(self):
        if self.search_thread_running:
            with self.search_thread_condition:
                self.search_thread_condition.notifyAll()

    def search_sitef_modules(self):
        with self.available_sitef_lock:
            logger.debug("Iniciando => search_sitef_modules")
            logger.debug("Quantidade de IPs para validação => {0}".format(len(self.sitef_ip_list)))
            for ip in self.sitef_ip_list:
                logger.debug("Validando IP => {0}".format(ip))
                try:
                    data_fiscal = time.strftime("%Y%m%d")  # '20171017'
                    hora_fiscal = time.strftime("%H%M%S")  # '162130'

                    ret = self.sitef_test_processor.process(str(self.pos_id), data_fiscal, hora_fiscal, ip)

                    if ret:
                        logger.debug("Sucesso na validação do IP => {0}".format(ip))
                        if ip not in self.available_sitefs:
                            self.available_sitefs.append(ip)
                    else:
                        logger.error("Falha na validação do IP => {0}".format(ip))
                        if ip in self.available_sitefs:
                            self.sitef_unavailable(ip)

                except Exception:
                    logger.exception("Erro validando IP SiTEF")

    def start_search_thread(self):
        self.search_thread_running = True
        self.search_thread = Thread(target=self._search_thread_loop)
        self.search_thread.daemon = True
        self.search_thread.name = "search_sitef_modules"
        self.search_thread.start()

    def stop_search_thread(self):
        if self.search_thread_running:
            with self.search_thread_condition:
                self.search_thread_running = False
                self.search_thread_condition.notifyAll()

    def _search_thread_loop(self):
        while self.search_thread_running:
            self.search_sitef_modules()
            with self.search_thread_condition:
                self.search_thread_condition.wait(self.sleep_time)

