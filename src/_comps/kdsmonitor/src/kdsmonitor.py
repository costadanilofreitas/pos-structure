# -*- coding: utf-8 -*-
import logging
import bustoken
import re
import subprocess
from threading import Thread, Condition
from msgbus import MBEasyContext, MBException, FM_PARAM, TK_SYS_ACK

logger = logging.getLogger("KdsMonitor")


class Kds:
    def __init__(self, name, ip, view_name):
        # type: (str, str) -> None
        self.name = name
        self.ip = ip
        self.view_name = view_name
        self.error_count = 0
        self.enabled = False


class KdsMonitor(Thread):
    def __init__(self, mbcontext, kdss_to_monitor, monitor_interval, max_error_count, start_wait_time):
        # type: (MBEasyContext, list, int) -> None
        super(KdsMonitor, self).__init__()

        self.mbcontext = mbcontext
        self.kdss_to_monitor = kdss_to_monitor
        self.monitor_interval = monitor_interval
        self.max_error_count = max_error_count
        self.start_wait_time = start_wait_time

        self.running = True
        self.thread_condition = Condition()
        self.ping_regex = re.compile(r'((tempo)|(time))([=<])(.*)ms')

    def run(self):
        self._thread_sleep(self.start_wait_time)
        while self.running:
            try:
                for kds in self.kdss_to_monitor:  # type: Kds
                    logger.info("Monitoring KDS %s" % kds.view_name)
                    if not self._ping(kds.ip):
                        if kds.error_count < self.max_error_count:
                            kds.error_count += 1
                            continue
                        logger.info("Disable KDS %s" % kds.view_name)
                        self._disable_kds(kds)
                    else:
                        if kds.error_count > 0:
                            kds.error_count -= 1
                            continue
                        logger.info("Enable KDS %s" % kds.view_name)
                        self._enable_kds(kds)
            except Exception:
                logger.exception("Erro durante monitoramento dos KDSs")
            finally:
                self._thread_sleep(self.monitor_interval)

    def finish(self):
        with self.thread_condition:
            self.running = False
            self.thread_condition.notifyAll()

    def _disable_kds(self, kds):
        # noinspection PyBroadException
        try:
            # Timeout = 5 Seconds
            ret = self.mbcontext.MB_EasySendMessage("ProductionSystem", bustoken.TK_PROD_DISABLEVIEW, format=FM_PARAM, data="%s" % kds.view_name, timeout=5000 * 1000)
            if ret.token == TK_SYS_ACK:
                kds.enabled = False
        except MBException:
            pass
        except Exception:
            logger.exception("Erro enviando mensagem para desabilitar KDS")

    def _enable_kds(self, kds):
        # noinspection PyBroadException
        try:
            # Timeout = 5 Seconds
            ret = self.mbcontext.MB_EasySendMessage("ProductionSystem", bustoken.TK_PROD_ENABLEVIEW, format=FM_PARAM, data="%s" % kds.view_name, timeout=5000 * 1000)

            if ret.token == TK_SYS_ACK:
                kds.enabled = True
        except MBException:
            pass
        except Exception:
            logger.exception("Erro enviando mensagem para habilitar KDS")

    def _thread_sleep(self, time):
        self.thread_condition.acquire()
        self.thread_condition.wait(time)
        self.thread_condition.release()

    def _ping(self, host):
        import platform

        command = ["ping"]
        params = ["-n", "1"] if platform.system().lower() == "windows" else ["-c", "1"]
        command.extend(params)
        command.append(str(host))
        ping_response = ""

        si = None
        if platform.system().lower() == "windows":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        ping = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si)
        for line in ping.stdout.readlines():
            ping_response += line

        ping.kill()
        if self.ping_regex.search(ping_response) is None:
            return False
        return True
