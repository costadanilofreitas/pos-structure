# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\components.py
import os
import sys
import threading
import json
import urllib
import urllib2
import sqlite3
import time
import datetime
import Queue
from collections import namedtuple
from xml.etree import cElementTree as etree
import msgbus
import persistence
import cfgtools
import systools
import syserrors

class BaseComponent(object):
    """ BaseComponent(name, service_type=None, required_services=None) -> BaseComponent
    
        This class represents a generic component class that connects to the
        message bus and waits for messages. This class should be sub classed to
        add more functionality.
    
        @param name: {str} - component name
        @param service_type: {str} - service type used during registration
        @param required_services: {str} - MWAPP service string
        @return: BaseComponent instance.
    """

    def __init__(self, name, service_type = None, required_services = None):
        self.name = name
        self.exit_status = 0
        self.service_type = service_type or name
        self.exported_services = '{0}:{1}'.format(self.name, self.service_type)
        self.required_services = required_services
        self.config = cfgtools.read(os.environ['LOADERCFG'])
        systools.sys_log_info("Initializing '{0}'.".format(self.name))
        self.mbcontext = self._init_msgbbus()
        self.dbd = self._init_persistence()

    def _init_msgbbus(self):
        """ _init_msgbbus
        
        @param name: {str} - component name
        @param required_services: {str} - MWAPP service string
        @return: MBContext instance
        """
        try:
            systools.sys_log_info("Initializing message-bus context for '{0}'".format(self.name))
            mbcontext = msgbus.MBEasyContext(self.name)
            if syserrors.SE_SUCCESS != mbcontext.MB_EasyWaitStart(self.exported_services, self.required_services):
                systools.sys_log_info("Terminating '{0}' component after 'MB_EasyWaitStart'".format(self.name))
                sys.exit(syserrors.SE_SUCCESS)
        except msgbus.MBException:
            systools.sys_log_exception('Message-bus error while initializing the PROXY component. Terminating.')
            sys.exit(syserrors.SE_MB_ERR)

        systools.sys_log_info("Message-bus context for '{0}' successfully initiated.".format(self.name))
        return mbcontext

    def _init_persistence(self):
        """ _init_persistence
        
        initializes the persistence layer
        
        @return: Driver instance
        """
        try:
            return persistence.Driver()
        except:
            systools.sys_log_exception('Error initializing persistence layer. Terminating')
            sys.exit(syserrors.SE_MB_ERR)

    @staticmethod
    def _get_config():
        """ _get_config
        
            Get the loader.cfg values and translate into a namedtuple.
        
        @return: namedtuple holding loader.cfg settings
        """
        cfg = cfgtools.read(os.environ['LOADERCFG'])
        c = {}
        for group in cfg.groups:
            d = dict(((key.name, key.values if len(key.values) > 1 else key.values[0]) for key in group.keys))
            c[group.name] = namedtuple(group.name, d.keys())(**d)

        return namedtuple('Config', c.keys())(**c)

    def _send_nack(self, msg):
        """ _send_nack(msg)
        
            Convenience method for return a TK_SYS_NAK
        
        @param msg: {MBMessage} - received message that is being replied to
        """
        msg.token = msgbus.TK_SYS_NAK
        self.mbcontext.MB_EasyReplyMessage(msg)

    def _send_ack(self, msg):
        """ _send_ack(msg)
        
            Convenience method for return a TK_SYS_ACK
        
        @param msg: {MBMessage} - received message that is being replied to
        """
        msg.token = msgbus.TK_SYS_ACK
        self.mbcontext.MB_EasyReplyMessage(msg)

    def start(self):
        """ start
        
            Method that starts a blocking loop to listen for incoming messages.
            This method will be overridden for other component use cases.
        """
        systools.sys_log_info("Starting '{0}'.".format(self.name))
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            systools.sys_log_info('Message received')
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            else:
                self._send_ack(msg)

        self.on_stop()
        sys.exit(self.exit_status)

    def on_stop(self):
        systools.sys_log_info("'{0}' stopped.".format(self.name))

    def get_store_wide_value(self, key):
        """ get_store_wide_value(key)
        
            Get a "store-wide" configuration value based on the key provided.
        
            @param key: {str} - name of store-wide key
        """
        response = self.mbcontext.MB_EasySendMessage('StoreWideConfig', token=msgbus.TK_STORECFG_GET, format=msgbus.FM_PARAM, data=key)
        if response.token == msgbus.TK_SYS_NAK:
            raise Exception('Unable to get Store Wide Configuration {%s}' % key)
        return str(response.data)

    def send_basic_message(self, service, data, format = msgbus.FM_STRING):
        """ send_basic_message(service, data)
        
        Convenience method for sending a "TK_EVT_EVENT" message to the supplied service
        
        @param service: {str} name of receiving service
        @param data: {str} data payload
        @return: None
        """
        reply = self.mbcontext.MB_EasySendMessage(service, token=msgbus.TK_EVT_EVENT, format=format, data=data)
        return reply

    def send_request(self, url, method = 'GET', data = None, headers = None, timeout = 10):
        if not headers:
            headers = {}
        headers['pragma'] = 'no-cache'
        if method == 'GET':
            if data:
                data_params = '&'.join([ '{0}={1}'.format(k, urllib.quote(v.encode('utf-8'))) for k, v in data.items() ])
                url = '{0}?{1}'.format(url, data_params)
            request = urllib2.Request(url, headers=headers)
        elif method == 'POST':
            if 'content-type' not in headers.keys():
                headers['content-type'] = 'application/x-www-form-urlencoded'
            if not data:
                data = ''
            request = urllib2.Request(url, data, headers=headers)
        elif method == 'PUT':
            if 'content-type' not in headers.keys():
                headers['content-type'] = 'application/json'
            if not data:
                data = ''
            request = urllib2.Request(url, data, headers=headers)
            request.get_method = lambda : 'PUT'
        try:
            systools.sys_log_debug('Sending request to: {0}'.format(url))
            response = urllib2.urlopen(request, timeout=timeout)
        except urllib2.HTTPError as error:
            systools.sys_log_error(error.read())
            result = {'code': 1,
             'desc': 'HTTP Request failure'}
            systools.sys_log_exception('HTTP Error: {0}'.format(error.msg))
        except urllib2.URLError as error:
            systools.sys_log_exception('URL Request failure.')
            result = {'code': 1,
             'desc': 'URL Request failure'}
            systools.sys_log_exception('URL Error: {0}'.format(error.reason))
        except Exception as error:
            systools.sys_log_exception('Request failure.')
            result = {'code': 1,
             'desc': 'Request failure'}
            systools.sys_log_exception('Request Error: {0}'.format(error.reason))
        else:
            result = {'code': 0,
             'desc': 'Success',
             'response': response.read()}

        systools.sys_log_debug('Request result: {0}'.format(result))
        return result


class CronJob(BaseComponent):
    """ CronJob(name, handler, required_services=None, typed_handler=False) -> CronJob
    
        This class represents a component that can be used to handle events
        sent from the "schedcomp" component.
    
        @param name: {str} - component name
        @param handler: {str} - callable handler function
        @param required_services: {str} - MWAPP service string
        @param typed_handler: {boolean} - Indicates if the handler provided for the cron job wants to receive the subject type as parameter
        @return: CronJob instance.
    """

    def __init__(self, name, handler, required_services = None, typed_handler = False):
        super(CronJob, self).__init__(name, required_services=required_services)
        self.handler = handler
        self.typed_handler = typed_handler
        self.mbcontext.MB_EasyEvtSubscribe(self.name)

    def start(self):
        """ start
        
            Wait for a TK_EVT_EVENT message and if the first tokenized string
            matches the component name then call the supplied handler.
        """
        systools.sys_log_info("Starting '{0}'.".format(self.name))
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                params = msg.data.split('\x00') if msg.data else []
                if not params or len(params) < 3:
                    systools.sys_log_error('Event missing parameters')
                    self._send_nack(msg)
                    continue
                data, subject, evttype = params[0], params[1], params[2]
                systools.sys_log_debug("Received event '{0}' (data={1}, evttype={2})".format(subject, data, evttype))
                if subject == self.name:
                    try:
                        if self.typed_handler:
                            self.handler(data, evttype)
                        else:
                            self.handler(data)
                    except:
                        systools.sys_log_exception('Could not start thread')

                else:
                    systools.sys_log_error('Received event from unsubscribed subject: {0}'.format(subject))
                self._send_ack(msg)
            else:
                self._send_nack(msg)


class MessageHandler(BaseComponent):
    """ MessageHandler(name, handlers, required_services=None) -> MessageHandler
    
        This class represents a component that handles specific tokens
    
        @param name: {str} - component name
        @param handlers: {dict} - dict with a function for each token the component accepts.
                                    Each handler function must accept a data parameter and
                                    return True so component continues to run
                                    or False for the component to stop
        @param required_services: {str} - MWAPP service string
        @return: MessageHandler instance.
    
        handler function example:
    
        def handler(data):
            # do something
    
            return True   # True to keep running, False to stop component
    
    """

    def __init__(self, name, handlers, required_services = None):
        super(MessageHandler, self).__init__(name, required_services=required_services)
        self.handlers = handlers
        self.keep_running = True

    def start(self):
        systools.sys_log_info('[{}] component started'.format(self.name))
        while self.keep_running:
            message = self.mbcontext.MB_EasyGetMessage()
            if message is None:
                systools.sys_log_warning('[{}] Received empty message'.format(self.name))
                self._send_nack(message)
                continue
            if message.token == msgbus.TK_CMP_TERM_NOW:
                self.finish()
                self._send_ack(message)
                return
            if message.token in self.handlers:
                try:
                    self.handlers[message.token](message)
                except BaseException as error:
                    systools.sys_log_exception('[{}] Error handling message {}({}):{}'.format(self.name, msgbus.MB_GetTokenName(message.token), message.token, repr(error)))
                    self._send_nack(message)

            else:
                systools.sys_log_warning('[{}] Received unrecognzied token:{}({})'.format(self.name, msgbus.MB_GetTokenName(message.token), message.token))

        self.finish()
        return

    def send_reply(self, message, format = msgbus.FM_PARAM, data = None):
        if data is not None:
            if hasattr(data, '__iter__'):
                payload = '\x00'.join(map(str, data))
            else:
                payload = str(data)
        self.mbcontext.MB_ReplyMessage(message, format, payload)
        return

    def finish(self):
        pass

    def stop_component(self):
        self.keep_running = False


class Service(BaseComponent):
    """ Service(name, task_table, required_services=None) -> Service
    
        This class represents a component that can be used to handle background tasks.
        These tasks are serialized and sent as JSON strings with the following structure:
    
            {"task": <name_of_task>,
                "params": ["param1: <param_1>,
                            "param2": <param2>]
            }
    
        @param name: {str} - component name
        @param task_table: {dict} - (task_name, handler) pair
        @param required_services: {str} - MWAPP service string
        @return: Service instance.
    """

    def __init__(self, name, task_table, required_services = None):
        super(Service, self).__init__(name, required_services=required_services)
        self.task_table = task_table

    def start(self):
        """ start
        
            Wait for a TK_EVT_EVENT message. Then deserialize the "task" object
            and call the associated handler.
        """
        systools.sys_log_info("Starting '{0}'.".format(self.name))
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                try:
                    data = json.loads(msg.data)
                    task = data['task']
                    params = data['params']
                except ValueError:
                    systools.sys_log_exception('Invalid parameters')
                    self._send_nack(msg)
                    continue

                systools.sys_log_debug('Received params {0} for task {1}'.format(params, task))
                if task in self.task_table.keys():
                    try:
                        threading.Thread(target=self.task_table[task], args=(msg,), kwargs=params).start()
                    except:
                        systools.sys_log_error('Could not start thread')
                        self._send_nack(msg)

                else:
                    systools.sys_log_error('Task {0} does not have handler'.format(task))
                    self._send_nack(msg)
            else:
                self._send_nack(msg)

    def send_response(self, msg, msgerr = 'SUCCESS', rc = 0, stack = None, data = None):
        """ send_response
        
            Convenience function for sending a response through the web service.
        """
        rsp = {'msgerr': msgerr,
         'rc': rc,
         'stack': stack,
         'data': data}
        msg.token = msgbus.TK_SYS_ACK if rc == 0 else msgbus.TK_SYS_NAK
        self.mbcontext.MB_ReplyMessage(msg, format=msgbus.FM_STRING, data=json.dumps(rsp))


class Subscriber(BaseComponent):
    """ Subscriber(name, events={}, required_services=None) -> Subscriber
    
        This class represents a component that can be used to subscribe to
        multiple events and handle each one with a callable function.
    
        @param name: {str} - component name
        @param events: {str} - (event_name, handler) pair
        @param required_services: {str} - MWAPP service string
        @return: Subscriber instance.
    """

    def __init__(self, name, events = {}, required_services = None):
        super(Subscriber, self).__init__(name, required_services=required_services)
        self.event_table = events
        self.mbcontext.MB_EasyEvtSubscribe('EVT_PROXY_CONTENT_AVAILABLE')
        for event in self.event_table:
            systools.sys_log_info('Subscribed to {0}'.format(event))
            self.mbcontext.MB_EasyEvtSubscribe(event)

    def start(self):
        """ start
        
            Wait for a TK_EVT_EVENT message and if the first tokenized string
            matches an entry in the events table then call the associated handler.
        """
        systools.sys_log_info("Starting '{0}'.".format(self.name))
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                params = msg.data.split('\x00') if msg.data else []
                if not params or len(params) < 3:
                    self._send_nack(msg)
                    continue
                data, subject, type = params[0], params[1], params[2]
                if subject in self.event_table:
                    func = self.event_table[subject]
                    try:
                        threading.Thread(target=func, args=(data, subject, type)).start()
                    except:
                        systools.sys_log_exception('Could not start thread')

                self._send_ack(msg)
            else:
                self._send_nack(msg)


class Consumer(BaseComponent):
    """ Consumer(name, handler, required_services=None) -> Consumer
    
        This class represents a component that can be used to consume generic data payloads. It is setup
        to listen for messages sent with the subject matching the classes "name" argument. A consumer
        is also registered under the "Consumer" type.
    
        @param name: {str} - component name
        @param handler: {func} - a callable
        @param required_services: {str} - MWAPP service string
        @return: Consumer instance.
    """

    def __init__(self, name, handler, required_services = None):
        super(Consumer, self).__init__(name, service_type='Consumer', required_services=required_services)
        self.handler = handler

    def start(self):
        """ start
        
            Wait for a TK_EVT_EVENT message. Then pass the message data to the associated handler.
        """
        systools.sys_log_info("Starting '{0}'.".format(self.name))
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                self.handler(msg, msg.data)
            else:
                self._send_nack(msg)

    def send_response(self, msg, code = 200):
        """ send_response
        
            Convenience function for sending a "http response code" back to the calling service as a reply message.
        """
        msg.token = msgbus.TK_SYS_ACK if 200 < code < 300 else msgbus.TK_SYS_NAK
        self.mbcontext.MB_ReplyMessage(msg, format=msgbus.FM_PARAM, data=json.dumps({'code': code}))


class AuditEventConsumer(BaseComponent):

    def __init__(self, service_name, service_type, process, cfg_group = None, required_services = None):
        super(AuditEventConsumer, self).__init__(service_name, service_type, required_services)
        self.service_name = service_name
        self.service_type = service_type
        self.eventFilter = []
        self.eventFilterData = {}
        self.lastRowId = None
        self.initialPeriod = None
        self.lastError = msgbus.SE_SUCCESS
        self.buffer = []
        self.force_resync = False
        self.lock = False
        self.terminating = False
        self.skip_event = False
        self.mode = 'DEFAULT'
        cfg_group = cfg_group if cfg_group else service_name
        self.mbcontext.MB_EasyEvtSubscribe('AUDITLOGGER')
        self.mbcontext.MB_EasyEvtSubscribe(self.name)
        self.initialPeriod = int(self.config.find_value('%s.initialPeriod' % cfg_group, '0'))
        if self.initialPeriod == 0:
            systools.sys_log_error('[%s] Configuration error: %s.initialPeriod is undefined.' % (self.service_name, cfg_group))
            sys.exit(msgbus.SE_NOTFOUND)
        self.resyncRequired = self.config.find_value('%s.resyncRequired' % cfg_group, 'true').lower() == 'true'
        control = self.config.find_value('%s.controlFilePath' % cfg_group)
        if not control:
            systools.sys_log_error('[%s] Configuration error: %s.controlFilePath is undefined.' % (self.service_name, cfg_group))
            sys.exit(msgbus.SE_NOTFOUND)
        self.controlFilePath = systools.sys_parsefilepath(control)
        if not self.controlFilePath:
            systools.sys_log_error('[%s] Configuration error: %s.controlFilePath is undefined.' % (self.service_name, cfg_group))
            sys.exit(msgbus.SE_NOTFOUND)
        controlPath = os.path.dirname(self.controlFilePath)
        if not os.path.exists(controlPath):
            os.mkdir(controlPath, 511)
        self.queue_max_size = int(self.config.find_value('%s.queueMaxSize' % cfg_group, '100'))
        for evtfilter in self.config.find_values('%s.eventFilter' % cfg_group) or []:
            event = evtfilter.split('/')
            self.eventFilter.append(event[0])
            if len(event) > 1:
                self.eventFilterData[event[0]] = event[1:]

        self.evt_batch_size = int(self.config.find_value('%s.eventBatchSize' % cfg_group, '0'))
        self.evt_batch_time = self.config.find_value('%s.eventBatchTime' % cfg_group, 'false').lower() == 'true'
        if self.evt_batch_size:
            self.mode = 'BATCH_SIZE'
        if self.evt_batch_time:
            self.mode = 'BATCH_TIME'
        self.q = Queue.Queue()
        self.buffer_q = Queue.Queue(maxsize=self.queue_max_size)
        self.process = process
        self.init_control_file()
        return

    def init_control_file(self):
        try:
            ctrlConn = sqlite3.connect(self.controlFilePath)
            ctrlConn.execute('\n                CREATE TABLE IF NOT EXISTS EventsSent (\n                    Period      INTEGER NOT NULL,\n                    LastRowId   INTEGER NOT NULL,\n                    PRIMARY KEY (LastRowId)\n                );\n            ')
            ctrlConn.execute('CREATE INDEX IF NOT EXISTS `index_LastRowId` ON `EventsSent` (`LastRowId` DESC);')
            c = ctrlConn.cursor()
            r = c.execute('\n                SELECT Period,LastRowId FROM EventsSent where period >= (SELECT max(Period) FROM EventsSent) order by LastRowId desc limit 1;\n            ').fetchone()
            if r:
                self.lastPeriod = r[0]
                self.lastRowId = r[1]
            else:
                self.lastPeriod = self.initialPeriod
                self.lastRowId = '-1'
            c.close()
            ctrlConn.close()
        except:
            systools.sys_log_exception('[%s] Failure during control file initialization.' % self.service_name)
            sys.exit(msgbus.SE_BADPARAM)

    def resync(self):
        systools.sys_log_info('[%s] Running resync.' % self.service_name)
        try:
            evttypes = ','.join(self.eventFilter)
            params = [self.lastPeriod, evttypes, self.lastRowId]
            d = '\x00'.join((str(p) for p in params))
            self.mbcontext.MB_EasySendMessage('AuditLogger', msgbus.TK_AUDITLOG_RESYNC, format=msgbus.FM_PARAM, data=d)
        except:
            if self.resyncRequired:
                systools.sys_log_exception('[%s] Exception occurred during resynchronization.' % self.service_name)
                sys.exit(syserrors.SE_MB_ERR)

        return (self.lastRowId, self.lastPeriod)

    def start(self):
        """ start
        
            Wait for a TK_EVT_EVENT message and if the first tokenized string
            matches an entry in the events table then call the associated handler.
        """
        t = threading.Thread(target=self.worker)
        t.daemon = True
        t.start()
        while not self.terminating:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                params = msg.data.split('\x00') if msg.data else []
                if not params:
                    self._send_nack(msg)
                    continue
                xml, subject, type = params[0], params[1], params[2]
                if subject == 'SKIPEVENT':
                    self.skip_event = True
                    self._send_ack(msg)
                    continue
                if subject == 'AUDITLOGGER':
                    if type not in self.eventFilter:
                        continue
                    item = [xml, type]
                    try:
                        if not self.lock:
                            if not self.evt_batch_size and not self.evt_batch_time:
                                item = [item]
                                self.q.put(item, False)
                            else:
                                self.buffer_q.put(item, False)
                            systools.sys_log_info("[{0}] Inserting into queue, size:'{1}'.".format(self.service_name, self.q.qsize()))
                        if self.evt_batch_size and self.buffer_q.qsize() >= self.evt_batch_size:
                            for q_item in range(self.evt_batch_size):
                                item = self.buffer_q.get()
                                self.buffer.append(item)

                            self.q.put(self.buffer, False)
                            self.buffer = []
                    except Queue.Full:
                        systools.sys_log_info("[{0}] Locking queue, size:'{1}'.".format(self.q.qsize(), self.service_name))
                        self.lock = True

                elif subject == 'BohPump':
                    if type == 'SendEvents':
                        for i in range(self.buffer_q.qsize()):
                            item = self.buffer_q.get()
                            self.buffer.append(item)

                        self.q.put(self.buffer, False)
                        self.buffer = []
                else:
                    self._send_nack(msg)
                    continue
            else:
                self._send_nack(msg)
                continue

    def fib(self, n):
        a, b = (1, 1)
        for i in range(n - 1):
            a, b = b, a + b

        return a

    def worker(self):
        systools.sys_log_info("Starting worker process for '{0}'.".format(self.name))
        lastRowId, lastPeriod = self.resync()
        self.lastError = None
        try:
            ctrlConn = sqlite3.connect(self.controlFilePath)
            ctrlConn.isolation_level = None
        except:
            systools.sys_log_exception("[%s] Failed to get the thread's control file handle." % self.service_name)
            self.lastError = msgbus.SE_DBINIT
            return

        while True:
            self.lastError = None
            retry_count = 1
            item = self.q.get()
            for idx, q_item in enumerate(item):
                event = etree.XML(q_item[0])
                auditlog = event.find('AuditLog')
                evtrowid = auditlog.get('rowId')
                evtperiod = auditlog.get('period')
                systools.sys_log_info('[%s] Processing event %s for period %s ...' % (self.service_name, evtrowid, evtperiod))
                if int(evtrowid) <= int(lastRowId):
                    evt_check = ctrlConn.execute('SELECT 1 FROM EventsSent WHERE LastRowId = %s and Period = %s;' % (evtrowid, evtperiod)).fetchone()
                    if evt_check:
                        item.pop(idx)

            while self.lastError != msgbus.SE_SUCCESS:
                try:
                    self.lastError = self.process(ctrlConn, item)
                    if self.lastError != syserrors.SE_SUCCESS and not self.skip_event:
                        if retry_count < 14:
                            retry_count += 1
                        systools.sys_log_info('[%s] Error sending event, retriyng in %s seconds ...' % (self.service_name, self.fib(retry_count)))
                        time.sleep(self.fib(retry_count))
                        continue
                    for idx, q_item in enumerate(item):
                        event = etree.XML(q_item[0])
                        auditlog = event.find('AuditLog')
                        evtrowid = auditlog.get('rowId')
                        evtperiod = auditlog.get('period')
                        ctrlConn.execute('INSERT OR IGNORE INTO EventsSent(Period, LastRowId) VALUES(:period, :rowid)', {'period': evtperiod,
                         'rowid': evtrowid})
                        lastRowId = evtrowid

                    if self.skip_event:
                        systools.sys_log_info('[%s] Event id %s skipped' % (self.service_name, evtrowid))
                        self.lastError = msgbus.SE_SUCCESS
                        self.skip_event = False
                    if datetime.datetime.strptime(str(evtperiod), '%Y%m%d') > datetime.datetime.strptime(str(lastPeriod), '%Y%m%d'):
                        date_subtract = datetime.datetime.strptime(str(lastPeriod), '%Y%m%d') - datetime.timedelta(days=15)
                        ctrlConn.execute('DELETE FROM EventsSent WHERE Period <= %s' % int(date_subtract.strftime('%Y%m%d')))
                        lastPeriod = evtperiod
                    if self.lock and self.buffer_q.qsize() == 0 and self.q.qsize() == 0:
                        systools.sys_log_info('[%s] Exiting to force resync events processed ...' % self.service_name)
                        self.mbcontext.MB_SendOneWayMessage(self.mbcontext.hv_service, msgbus.TK_HV_COMPSTOP, format=msgbus.FM_STRING, data='BohPump')
                except:
                    systools.sys_log_exception('[%s] Could not start thread' % self.service_name)

        ctrlConn.close()
        return

    def send_response(self, msg, code = 200):
        """ send_response
        
            Convenience function for sending a "http response code" back to the calling service as a reply message.
        """
        msg.token = msgbus.TK_SYS_ACK if 200 < code < 300 else msgbus.TK_SYS_NAK
        self.mbcontext.MB_ReplyMessage(msg, format=msgbus.FM_PARAM, data=json.dumps({'code': code}))


class CherryPyComponent(BaseComponent):
    """ CherryPyComponent(name, evt_table, wsgi_app, service_type, required_services) -> CherryPyComponent
    
        This class represents a component that runs a CherryPy server
        and have an opened thread for handling msgbus messages
    
        @param name: {str} - component name
        @param evt_table: {list} - list of event subjects that need to be handled
        @param wsgi_app: {func} - webapp2 app
        @param service_type: {str} - service type used during registration
        @param required_services: {str} - MWAPP service string
        @return: CherryPyComponent instance.
    """

    def __init__(self, name, evt_table, wsgi_app, listening_port = None, host = '127.0.0.1', service_type = None, required_services = None, auto_reply = True):
        super(CherryPyComponent, self).__init__(name, service_type, required_services)
        self.wsgi_app = wsgi_app
        self.evt_table = evt_table
        self.host = host
        self.auto_reply = auto_reply
        if listening_port:
            self.listening_port = listening_port
        else:
            self.listening_port = self.config.Config.Port
        for event in self.evt_table:
            systools.sys_log_info('Subscribing to event "{0}"'.format(event))
            self.mbcontext.MB_EasyEvtSubscribe(event)

    def _mb_thread(self):
        """ _mb_thread
        
            Wait for a message. Then pass the message data to the associated handler.
            It can be overridden if necessary for specific message handling of the
            component
        """
        import cherrypy
        while True:
            msg = self.mbcontext.MB_EasyGetMessage()
            if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
                self._send_nack(msg)
                break
            elif msg.token == msgbus.TK_EVT_EVENT:
                params = msg.data.split('\x00') if msg.data else []
                if not params or len(params) < 3:
                    self._send_nack(msg)
                    continue
                data, subject, evt_type = params[0], params[1], params[2]
                if subject in self.evt_table:
                    try:
                        func = getattr(self, 'handle_{0}'.format(subject.lower()))
                    except AttributeError:
                        systools.sys_log_exception('Handler not found for "{0}" event.'.format(subject))
                        self._send_nack(msg)
                    else:
                        try:
                            threading.Thread(target=func, args=(data, subject, evt_type), kwargs={'current_msg': msg}).start()
                            if self.auto_reply:
                                self._send_ack(msg)
                        except:
                            systools.sys_log_exception('Could not start thread for "{0}" event handler.'.format(subject))
                            self._send_nack(msg)

                else:
                    self._send_nack(msg)
            else:
                self._send_nack(msg)

        cherrypy.engine.exit()
        if self.server:
            self.server.stop()
        sys.exit(syserrors.SE_SUCCESS)

    def start(self):
        from cherrypy import wsgiserver
        try:
            mb_thread = threading.Thread(target=self._mb_thread, name='{0}._mb_thread'.format(self.name))
            mb_thread.start()
            systools.sys_log_debug('{0} CherryPyWSGIServer listening at port {1}'.format(self.name, self.listening_port))
            self.wsgi_app.mbcontext = self.mbcontext
            self.wsgi_app.component = self
            self.server = wsgiserver.CherryPyWSGIServer((self.host, int(self.listening_port)), self.wsgi_app, numthreads=64)
            self.server.start()
        except KeyboardInterrupt:
            if hasattr(self, 'server'):
                self.server.stop()
            sys.exit(syserrors.SE_USERCANCEL)
        except:
            if hasattr(self, 'server'):
                self.server.stop()
            systools.sys_log_exception('Error starting {0} component'.format(self.name))
            sys.exit(syserrors.SE_USERCANCEL)


class parameters(object):
    """ parameters(params)
    
        This class represents a decorator object that will validate the
        decorated functions keyword arguments against the supplied list of params.
    
        @param params: {[str]} - list of "parameter" names to be validated
    """

    def __init__(self, params):
        self.params = params

    def __call__(self, func):

        def check_params(*args, **kwargs):
            for p in self.params:
                if p not in kwargs.keys():
                    raise ValueError

            return func(*args, **kwargs)

        return check_params