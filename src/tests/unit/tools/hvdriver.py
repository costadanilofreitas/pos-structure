# encoding: utf-8
import requests
import bustoken
import persistence
import time
import os

from xml.etree import cElementTree as eTree
from msgbus import MBEasyContext


class HyperVisorDriver(object):
    ServicesPath = "/mwapp/services"

    MSGGRP_HV = "2"

    TK_HV_COMPSTART = bustoken.create_token(bustoken.MSGPRT_LOW, MSGGRP_HV, "1")
    TK_HV_COMPKILL = bustoken.create_token(bustoken.MSGPRT_HIGH, MSGGRP_HV, "2")
    TK_HV_COMPLIST = bustoken.create_token(bustoken.MSGPRT_LOW, MSGGRP_HV, "3")

    def __init__(self, mwapp_url):
        self.mwapp_url = mwapp_url
        self.services_url = mwapp_url + HyperVisorDriver.ServicesPath

    def kill_component(self, service_name):
        xml = self._get_service_list_xml(service_name)
        pid = self._find_service_pid_from_xml(xml, service_name)
        self._kill_service_by_pid(pid)

    def start_component(self, service_name):
        self._start_service_by_service_name(service_name)

    def restart_component(self, service_name):
        self.kill_component(service_name)
        self.start_component(service_name)

    def _get_service_list_xml(self, service_name):
        url = self.services_url + "/HyperVisor/HyperVisor/?token=" + bustoken.get_token_hexa_string(HyperVisorDriver.TK_HV_COMPLIST) + "&format=xml&timeout=-1&isBase64=false"
        response = requests.post(url, timeout=10.0)
        HyperVisorDriver._check_response_and_token_errors(url, response)
        if response:
            response_xml = eTree.XML(response.text)
            return response_xml
        else:
            raise Exception("Error posting data to service. Url: {0}, Error code: {1}, ".format(url, response.status_code))

    def _find_service_pid_from_xml(self, xml, service_name):
        all_services = xml.findall("component[@name='" + service_name + "']")
        if len(all_services) == 0:
            raise Exception("Service {0} not found".format(service_name))
        elif len(all_services) > 1:
            raise Exception("Found more than one service with the name {0}".format(service_name))

        service_node = all_services[0]

        # Lets get the PID of the service
        if "pid" not in all_services[0].attrib:
            raise Exception("pid attribute not found on service node: {0}".format(eTree.tostring(service_node)))

        service_pid = all_services[0].get("pid")

        return service_pid

    def _kill_service_by_pid(self, pid):
        url = self.services_url + "/HyperVisor/HyperVisor?token=" + bustoken.get_token_hexa_string(HyperVisorDriver.TK_HV_COMPKILL) + "&format=string&timeout=-1&isBase64=false"
        response = requests.post(url, data=pid, timeout=10.0)
        HyperVisorDriver._check_response_and_token_errors(url, response)

    def _start_service_by_service_name(self, service_name):
        url = self.services_url + "/HyperVisor/HyperVisor?token=" + bustoken.get_token_hexa_string(HyperVisorDriver.TK_HV_COMPSTART) + "&format=string&timeout=-1&isBase64=false"
        response = requests.post(url, data=service_name, timeout=10.0)
        HyperVisorDriver._check_response_and_token_errors(url, response)

    @staticmethod
    def _check_response_and_token_errors(url, response):
        # type: (str, requests.Response) -> None
        token_header_name = "X-token-name"
        if response:
            if token_header_name not in response.headers:
                raise Exception("Token name not found in response")

            if response.headers[token_header_name] != "TK_SYS_ACK":
                raise Exception("Invalid token returned from service: {0}".format(response.headers[token_header_name]))
        else:
            raise Exception("Error posting data to service. Url: {0}, Error code: {1}, ".format(url, response.status_code))


class HyperVisorComunicator(object):
    def __init__(self, bin_dir):
        # type: (unicode) -> None
        # Variáveis que precisam estar no environment para conseguimos utilizat o mbcontext
        os.environ["HVPORT"] = "14000"
        os.environ["HVIP"] = "127.0.0.1"
        os.environ["HVCOMPPORT"] = "35686"

        self.old_cwd = os.getcwd()
        bin_dir = os.path.abspath(bin_dir)
        os.chdir(bin_dir)

        self.mbcontext = MBEasyContext("End2EndTests")

    def finalize(self):
        self.mbcontext.MB_EasyFinalize()

    def wait_persistence(self):
        count = 0
        while True:
            conn = None
            try:
                print("Abrindo conexão")
                conn = persistence.Driver().open(self.mbcontext)
                print("Conexão Aberta")
                conn.close()
                print("Conexão Fechada")
                break
            except Exception as ex:
                print("HV nao encontrado: " + ex.message)
                if conn is not None:
                    conn.close()
                    
                count += 1
                time.sleep(3)
                if count == 5:
                    raise ex


def main():
    hyper_visor_driver = HyperVisorDriver("http://localhost:8080")
    hyper_visor_driver.kill_component("auditlogger")
    hyper_visor_driver.start_component("auditlogger")

if __name__ == '__main__':
    main()