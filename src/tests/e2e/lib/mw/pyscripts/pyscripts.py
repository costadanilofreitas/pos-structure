# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\pyscripts.py
"""
Implementation script of the "pyscripts" component.
This module also contains some helper functions for using on other modules
"""
import sys
import os
import time
import unittest
import StringIO
import collections
import threading
import msgbus
import cfgtools
from systools import sys_log_debug, sys_log_exception
__all__ = ('mbcontext', 'subscribe_event_listener', 'unsubscribe_event_listener', 'include_test_case')
SERVICE_NAME = 'PythonScripts'
SERVICE_TYPE = 'Scripts'
EXPORTED_SERVICES = '%s:%s' % (SERVICE_NAME, SERVICE_TYPE)
REQUIRED_SERVICES = None
mbcontext = None
__eventlisteners = collections.defaultdict(list)
__test_cases = []

def subscribe_event_listener(subject, callback):
    """subscribe_event_listener(subject, callback)
    Subscribes the given callback function to receive events of the given subject
    @param subject - {str} - event subject to subscribe
    @param callback - {callable} - callback function to receive event notifications: def callback(event_parameters=[]): pass
    """
    global mbcontext
    listeners = __eventlisteners[str(subject)]
    if callback in listeners:
        return
    if len(listeners) == 0:
        sys_log_debug('pyscripts is subscribing to event: [%s]...' % subject)
        mbcontext.MB_EasyEvtSubscribe(subject)
    listeners.append(callback)


def unsubscribe_event_listener(subject, callback):
    """unsubscribe_event_listener(subject, callback)
    Unsubscribes the given callback function from receiving events of the given subject
    @param subject - {str} - event subject to unsubscribe
    @param callback - {callable} - callback function to unsubscribe
    """
    __eventlisteners[str(subject)].remove(callback)


def include_test_case(test_case):
    """include_test_case(test_case)
    Include a TestCase to be executed when a TK_EVT_RUNTESTS message is received
    @param test_case - {unittest.TestCase} - test case to be executed
    """
    __test_cases.append(test_case)


def __import_modules():
    config = cfgtools.read(os.environ['LOADERCFG'])
    modules = config.find_values('PythonScripts.Modules') or []
    for name in modules:
        sys_log_debug('Loading python script module: %s' % name)
        try:
            module = __import__(name)
            if hasattr(module, 'main'):
                module.main()
        except:
            sys_log_exception('FATAL Exception trapped while importing module %s - going down' % name)
            sys.exit(1)


def __loop_receive_messages():
    while True:
        msg = mbcontext.MB_EasyGetMessage()
        if not msg or msg.token == msgbus.TK_CMP_TERM_NOW:
            sys_log_debug('Terminating pyscripts component')
            if msg:
                msg.token = msgbus.TK_SYS_ACK
                mbcontext.MB_EasyReplyMessage(msg)
            sys.exit(0)
        if msg.token == msgbus.TK_EVT_EVENT:
            th = threading.Thread(target=__event_dispatcher, args=(msg,))
            th.setDaemon(True)
            th.start()
            del th
            continue
        if msg.token == msgbus.TK_EVT_RUNTESTS:
            HVDATADIR = os.environ.get('HVDATADIR')
            if HVDATADIR:
                test_result_file = os.path.join(HVDATADIR, 'pyscripts_test_report.log')
            th = threading.Thread(target=__run_tests, args=(__test_cases, test_result_file))
            th.setDaemon(True)
            th.start()
            del th
            mbcontext.MB_EasyReplyMessage(msg)
            continue
        msg.token = msgbus.TK_SYS_NAK
        try:
            mbcontext.MB_EasyReplyMessage(msg)
        except:
            pass


def __event_dispatcher(msg):
    try:
        params = msg.data.split('\x00')
        xml = params[0] if len(params) > 0 else None
        subject = params[1] if len(params) > 1 else None
        type = params[2] if len(params) > 2 else None
        isSync = True if len(params) > 3 and params[3] == 'true' else False
        params = (xml, subject, type) + tuple(params[3:])
        if not isSync:
            mbcontext.MB_EasyReplyMessage(msg)
        for listener in __eventlisteners[subject]:
            data = listener(params)
            if isSync and data is not None:
                format = msgbus.FM_STRING
                if not isinstance(data, basestring):
                    format = data[0]
                    data = data[1]
                msg.token = msgbus.TK_SYS_ACK
                mbcontext.MB_ReplyMessage(msg, data=data, format=format)
                return

    except:
        sys_log_exception('Exception trapped (and ignored) while calling event listener')
        msg.token = msgbus.TK_SYS_NAK

    if isSync:
        mbcontext.MB_EasyReplyMessage(msg)
    return


def __run_tests(test_cases, test_result_file = None):
    test_results = []
    for test_case in test_cases:
        startTime = time.time()
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_result = unittest.TextTestRunner(verbosity=2).run(suite)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        test_output = StringIO.StringIO()
        for error in test_result.errors:
            test_output.write('{0}\n'.format(test_result.separator1))
            test_output.write('ERROR: {0}\n'.format(str(error[0])))
            test_output.write('{0}\n'.format(test_result.separator2))
            test_output.write('{0}\n'.format(str(error[1])))

        for failure in test_result.failures:
            test_output.write('{0}\n'.format(test_result.separator1))
            test_output.write('FAILED: {0}\n'.format(str(failure[0])))
            test_output.write('{0}\n'.format(test_result.separator2))
            test_output.write('{0}\n'.format(str(failure[1])))

        test_output.write('{0}\n'.format(test_result.separator2))
        test_output.write('Ran %d test%s in %.3fs\n' % (test_result.testsRun, test_result.testsRun != 1 and 's' or '', timeTaken))
        if not test_result.wasSuccessful():
            test_output.write('FAILED (')
            failed, errored = map(len, (test_result.failures, test_result.errors))
            if failed:
                test_output.write('failures=%d' % failed)
            if errored:
                if failed:
                    test_output.write(', ')
                test_output.write('errors=%d' % errored)
            test_output.write(')\n')
        else:
            test_output.write('OK\n')
        test_results.append(test_output.getvalue())
        test_output.close()

    if test_result_file:
        with open(test_result_file, 'w') as trf:
            for result in test_results:
                trf.write(result)
                trf.write('\n')

    return '\n'.join(test_results)


def __main():
    global mbcontext
    sys_log_debug('Starting pyscripts component')
    mbcontext = msgbus.MBEasyContext('pyscripts')
    try:
        if mbcontext.MB_EasyWaitStart(EXPORTED_SERVICES, REQUIRED_SERVICES) == 0:
            __import_modules()
            __loop_receive_messages()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        sys_log_exception('Exception trapped. Component is going down!!')
        sys.exit(1)

    sys.exit(0)