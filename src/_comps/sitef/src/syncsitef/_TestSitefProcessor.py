# -*- coding: utf-8 -*-
import logging
import os
import re
import time
from ctypes import WinDLL, c_long, addressof, create_string_buffer

from systools import sys_log_exception

logger = logging.getLogger("Sitef")


class TestSitefProcessor(object):
    def __init__(self, id_loja):
        self.id_loja = id_loja

        clisitef_lib = "{BUNDLEDIR}/lib/clisitef32i.dll"
        for var in re.findall("{[a-zA-Z0-9]*}+", clisitef_lib):
            clisitef_lib = clisitef_lib.replace(var, os.environ.get(var.replace('{', '').replace('}', ''), ""))

        self.sitefDll = WinDLL(clisitef_lib)
        self.configuraIntSiTefInterativo = self.sitefDll["ConfiguraIntSiTefInterativo"]
        self.iniciaFuncaoSiTefInterativo = self.sitefDll["IniciaFuncaoSiTefInterativo"]
        self.continuaFuncaoSiTefInterativo = self.sitefDll["ContinuaFuncaoSiTefInterativo"]
        self.finalizaFuncaoSiTefInterativo = self.sitefDll["FinalizaFuncaoSiTefInterativo"]

    def process(self, pos_id, data_fiscal, hora_fiscal, ip_sitef):
        time_limit = (time.time() + 5.0)
        while (time.time() < time_limit) and (not self.sitefDll["VerificaPresencaPinPad"]()):
            time.sleep(0.2)

        id_terminal = "SW99%04d" % int(pos_id)
        logger.debug("TestSitefProcessor - IP Sitef: {0}, ID Loja: {1}, ID Terminal: {2}".format(ip_sitef, self.id_loja, id_terminal))

        ret = -12
        while ret == -12:
            ret = self.configuraIntSiTefInterativo(ip_sitef, self.id_loja, id_terminal, 0)

        if ret == 0:
            ret = self.iniciaFuncaoSiTefInterativo(111, "", pos_id + "", data_fiscal, hora_fiscal, "", "")
            if ret == 10000:
                comando = c_long(0)
                tipo_campo = c_long(0)
                tam_minimo = c_long(0)
                tam_maximo = c_long(0)
                tam_buffer = 32768
                output_buffer = create_string_buffer('\000' * tam_buffer)

                while ret == 10000:
                    ret = self.continuaFuncaoSiTefInterativo(addressof(comando), addressof(tipo_campo), addressof(tam_minimo), addressof(tam_maximo), output_buffer, tam_buffer, 0)

                    if ret != 10000:
                        break

                    try:
                        if not comando.value == 0:
                            if comando.value == 20:
                                output_buffer.value = "0"
                                time.sleep(0.5)

                    except Exception as ex:
                        sys_log_exception("Exception Trapped on SiTef Processor %" + str(ex))

                response = "Teste Realizado com Sucesso" if ret == 0 else "Falha no Teste: Erro %s" % str(ret)
                logger.debug("TestSitefProcessor - Resposta: {}".format(response))

                self.finalizaFuncaoSiTefInterativo("0", pos_id + "", data_fiscal, hora_fiscal, None)
                return True if ret == 0 else False

        logger.debug("TestSitefProcessor - Erro Configurando SiTef Interativo")
        return False