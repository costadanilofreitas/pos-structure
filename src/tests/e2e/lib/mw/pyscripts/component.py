# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\component.py
import logging
import os
import sys
import cfgtools
import msgbus
import syserrors
import systools

class MWAppComponentLogger(object):
    """ Handle the logging capabilities of a component. """
    LOG_FORMAT = '%(asctime) -8s %(message)s'

    def __init__(self, level, filename, *args, **kwargs):
        self.log_file = filename
        self.level = level
        logging.basicConfig(filename=self.log_file, level=self.level, format=self.LOG_FORMAT)

    def info(self, msg):
        logging.info(msg)
        systools.sys_log_info(msg)

    def debug(self, msg):
        logging.debug(msg)
        systools.sys_log_debug(msg)

    def warning(self, msg):
        logging.warning(msg)
        systools.sys_log_warning(msg)

    def error(self, msg):
        logging.error(msg)
        systools.sys_log_error(msg)

    def critical(self, msg):
        logging.critical(msg)
        systools.sys_log_critical(msg)

    def exception(self, msg):
        logging.exception(msg)
        systools.sys_log_exception(msg)

    def log(self, level, msg):
        logging.log(level, msg)
        systools.sys_log(level, msg)


class MWAppComponent(object):
    """Base class for a MWApp component developed in Python.
    
    COMPONENT_NAME {str} -> must be filled with the name of the component
    REQUIRED_SERVICES {list} -> list of services that must be started before this component can be started
    EVENTS_TO_WATCH {list} -> list of events names that must be handled by this component
    
    Creating a new component:
    You need to create a new object that inherits from this class.
    
    Example:
    >>> class MyNewComponent(MWAppComponent):
    ...    pass
    
    Starting:
    >>> MyNewComponent().start()
    
    Handling messages:
    
    In your component class implement method following this pattern:
    
    def handle_MSG_TOKEN(self):
        \"\"\" Implements the behaviour when the component receive MSG_TOKEN message \"\"\"
    
    """
    COMPONENT_NAME = ''
    EXPORTED_SERVICES = None
    REQUIRED_SERVICES = None
    EVENTS_TO_WATCH = []

    def __init__(self):
        systools.sys_log_info('Creating instance of {0}'.format(self.COMPONENT_NAME))
        self.cfg = self.get_config()
        systools.sys_log_info('After get_config')
        self.logger = self.get_logger()
        self.logger.info("Initializing '{0}'.".format(self.COMPONENT_NAME))
        self.mbcontext = self.init_msgbbus()
        self.persistence = self.init_persistence()
        self.subscribe_to_events()
        self.logger.info("Initializing '{0}' - FINISHED. You can start it now!".format(self.COMPONENT_NAME))

    def init_msgbbus(self):
        try:
            self.logger.info("Initializing message-bus context for '{0}'".format(self.COMPONENT_NAME))
            mbcontext = msgbus.MBEasyContext(self.COMPONENT_NAME)
            if syserrors.SE_SUCCESS != mbcontext.MB_EasyWaitStart(self.EXPORTED_SERVICES, self.REQUIRED_SERVICES):
                self.logger.info("Terminating '{0}' component after 'MB_EasyWaitStart'".format(self.COMPONENT_NAME))
                sys.exit(syserrors.SE_SUCCESS)
        except msgbus.MBException:
            self.logger.info("Message-bus error while initializing the '{0}' component. Terminating.".format(self.COMPONENT_NAME))
            sys.exit(syserrors.SE_MB_ERR)

        self.logger.info("Message-bus context for '{0}' successfully initiated.".format(self.COMPONENT_NAME))
        return mbcontext

    def get_config(self):
        return cfgtools.read(os.environ['LOADERCFG'])

    def get_logger(self):
        HVDATADIR = os.environ.get('HVDATADIR')
        component_log = self.cfg.find_value('Config.component_log').format(HVDATADIR=HVDATADIR)
        logger = MWAppComponentLogger(logging.DEBUG, component_log)
        return logger

    def init_persistence(self):
        pass

    def on_start(self):
        pass

    def subscribe_to_events(self):
        self.logger.info('Subscribing to events to be watched.')
        for event in self.EVENTS_TO_WATCH:
            self.logger.info('Subscribed to {0}'.format(event))
            self.mbcontext.MB_EasyEvtSubscribe(event)

    def start(self):
        exit_status = syserrors.SE_SUCCESS
        self.logger.info("Starting '{0}'.".format(self.COMPONENT_NAME))
        try:
            self.on_start()
            while True:
                msg = self.mbcontext.MB_EasyGetMessage()
                if not msg:
                    self.logger.info('Message not found. Stopping component.')
                    self.mbcontext.MB_EasyReplyMessage(msg)
                    break
                elif msg.token == msgbus.TK_CMP_TERM_NOW:
                    self.logger.info('Message TK_CMP_TERM_NOW received. Stopping component.')
                    self.mbcontext.MB_EasyReplyMessage(msg)
                    break
                try:
                    token = msgbus.MB_GetTokenName(msg.token)
                    self.logger.info('Receive message: {0}'.format(token))
                    getattr(self, 'handle_{0}'.format(token))(msg)
                except AttributeError:
                    msg.token = msgbus.TK_SYS_NAK
                    self.mbcontext.MB_EasyReplyMessage(msg)

        except KeyboardInterrupt:
            self.logger.info("Stopping '{0}' by keyboard action.".format(self.COMPONENT_NAME))
            exit_status = syserrors.SE_USERCANCEL

        self.on_stop()
        sys.exit(exit_status)

    def on_stop(self):
        self.logger.info("'{0}' stopped.".format(self.COMPONENT_NAME))