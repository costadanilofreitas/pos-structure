# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\cronnotify.py
from __future__ import with_statement
import time
import persistence
import systools
from mwapp.components import CronJob

class CronNotify(object):

    def __init__(self):
        self.dbd = None
        self.component = None
        self.settings = None
        self.service_name = None
        return

    def exec_procedure_sql(self, procedure, **kwargs):
        self.dbd = persistence.Driver()
        conn = None
        conn_allocated = False
        trans_opened = False
        success = False
        res = []
        try:
            conn = self.dbd.open(self.component.mbcontext, service_name=self.settings.postgrespersistence.encode('UTF-8'))
            conn.transaction_start()
            conn_allocated = True
            conn.query('BEGIN TRANSACTION;')
            trans_opened = True
            cursor = conn.pselect(procedure, **kwargs)
            for row in cursor:
                res.append(dict([ (cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols()) ]))

            success = True
        except Exception as e:
            res = ['error: %s' % e]
        finally:
            if trans_opened:
                try:
                    if success:
                        conn.query('COMMIT TRANSACTION;')
                    else:
                        conn.query('ROLLBACK TRANSACTION;')
                except:
                    pass

            if conn_allocated:
                conn.transaction_end()
            if conn:
                conn.close()

        return res

    def event_handler(self, data):
        pass

    def event_handler_man(self, data):
        systools.sys_log_info('[AUTONOTIFY] Started {0} service.'.format(self.service_name))
        if data:
            systools.sys_log_info('[AUTONOTIFY] EVENT HANDLER: data {0}'.format(data))

        def current_milli_time():
            return int(round(time.time() * 1000))

        milli_start = current_milli_time()
        self.event_handler(data)
        milli_end = current_milli_time()
        total = (milli_end - milli_start) / 1000
        systools.sys_log_info('[AUTONOTIFY] Finished %s service - time: %d seconds' % (self.service_name, total))

    def main(self):
        try:
            self.component = CronJob(self.service_name, self.event_handler_man)
            self.settings = self.component.config.settings
            self.component.start()
        except Exception:
            systools.sys_log_exception('[AUTONOTIFY] Service {0} closing'.format(self.service_name))