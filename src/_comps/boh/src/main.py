import sys


#
# Copyright (C) 2008 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#


import requests
from datetime import datetime, timedelta

from mwapp.components import CronJob
from systools import sys_log_exception, sys_log_warning, sys_log_debug, sys_log_error, sys_log_info
from msgbus import TK_STORECFG_GET, FM_PARAM
from syserrors import SE_CFGLOAD, SE_MB_CONNECT

REQUIRED_SERVICES = 'StoreWideConfig'

EXPORTED_SERVICES = 'MwBOH'


def main():

    try:
        sys_log_info('[mwboh] starting Component')
        component = MwBoh()
        component.start()
    except:
        sys_log_exception('[mwboh] Error starting component')


class MwBoh(CronJob):

    def __init__(self):
        super(MwBoh, self).__init__(EXPORTED_SERVICES, self.handle_event, REQUIRED_SERVICES, typed_handler=True)
        try:
            message = self.mbcontext.MB_EasySendMessage("StoreWideConfig", TK_STORECFG_GET, format=FM_PARAM, data="Store.Id")
            if message.data in (None, ''):
                raise Exception('Store.Id not defined')
            self.store_id = message.data
            message = self.mbcontext.MB_EasySendMessage("StoreWideConfig", TK_STORECFG_GET, format=FM_PARAM, data="BackOffice.ServerURL")
            if message.data in (None, ''):
                raise Exception('BackOffice.ServerURL not defined')
            server_url = message.data
            message = self.mbcontext.MB_EasySendMessage("StoreWideConfig", TK_STORECFG_GET, format=FM_PARAM, data="BackOffice.ApiKey")
            api_key = message.data
        except:
                sys_log_exception('[mwboh] Error reading configuration from StoreWideConfig')
                sys.exit(SE_CFGLOAD)

        try:
            self.mbcontext.MB_EasyEvtSubscribe(self.name)
        except:
            sys_log_exception('[mwboh] Error subscribing to events')
            sys.exit(SE_MB_CONNECT)

        self.server = Request(server_url, api_key)
        sys_log_info('[mwboh][UserControl] started component successfully url={}'.format(server_url))

    def handle_event(self, data, evttype):

        if evttype == 'ImportUser':
            sys_log_info("[mwboh] Received event '{}'".format(evttype))
            try:
                self.import_users()
            except:
                sys_log_exception('[mwboh] Error importing users')
        else:
            sys_log_warning('[mwboh] received unrecognized event: {}'.format(evttype))

    def import_users(self):
        sys_log_debug('[mwboh][UserControl] import users start')
        response = self.server.request('pump/hr/employee?with-details=true&store-code={}'.format(self.store_id), method='get')
        connection = None
        transaction = False
        try:
            connection = self.dbd.open(self.mbcontext)
            connection.transaction_start()
            transaction = True
            for user in response:
                user_id = int(user['pos-user-id'])
                long_name = connection.escape(user['name'].encode('utf-8'))
                password = user['pos-password']
                level = user['pos-access-level']['code']
                start_date = user['from-dt']
                end_date = user['to-dt']
                pay_rate = user['pay-rate-amount']
                status = self.get_user_status(start_date, end_date, level)

                if end_date is None:
                    end_date = 'NULL'
                else:
                    end_date = "'{}'".format(end_date)
                cursor = connection.select("SELECT 1 from users.Users WHERE UserId={}".format(user_id))
                if cursor.rows() > 0:
                    connection.query("UPDATE users.Users SET LongName='{}', Password='{}', Level={}, Status={}, AdmissionDate='{}', TerminationDate={}, PayRate={} WHERE UserId={}".format(
                        long_name, password, level, status, start_date, end_date, pay_rate, user_id))
                else:
                    sql = '''INSERT INTO users.Users(UserId, UserName, LongName, Password, Level, Status, AdmissionDate, TerminationDate, PayRate)
                                            VALUES ({0}, '{0}', '{1}', '{2}', {3}, {4}, '{5}', {6}, {7})'''.format(user_id, long_name, password, level, status, start_date, end_date, pay_rate)
                    connection.query(sql)
        finally:
            if connection:
                if transaction:
                    connection.transaction_end()
                connection.close()
        sys_log_debug('[mwboh][UserControl] import users finished')

    def get_user_status(self, start_text, end_text, level):
        start = datetime.strptime(start_text, '%Y-%m-%d')
        now = datetime.now()
        if end_text is not None:
            end = datetime.strptime(end_text, '%Y-%m-%d')
        else:
            one_day = timedelta(days=1)
            end = now + one_day
        active = False
        if start <= now and now <= end or level >= 30:
            active = True

        if active is True:
            return '0'
        else:
            return '1'


class Request(object):

    def __init__(self, server_url, api_key):
        self.server_url = server_url
        self.api_key = api_key

        if not self.server_url.endswith('/'):
            self.server_url += '/'
        
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    def request(self, view, payload=None, timeout=30, verify=False, method='post'):
            headers = {'Accept': 'application/json',
                       'Content-type': 'application/json',
                       'x-api-key': self.api_key}
            url = '{}{}'.format(self.server_url, view)

            sys_log_debug('[mwboh] Sending request url={}'.format(url))
            response = requests.request(method, url, headers=headers, data=payload, timeout=timeout, verify=verify)
            sys_log_debug('[mwboh] server response status_code={}'.format(response.status_code))

            if response.status_code != 200:
                sys_log_error('[mwboh] Error sending request to server: {}'.format(repr(response)))
                raise RequestError('Error sending request to server', response.status_code, response.text)

            json = None
            try:
                json = response.json()
            except ValueError:
                sys_log_exception('[mwboh] response from server is not a valid json: {}'.format(response.text))
                raise RequestError('Reponse from server is not JSON', response.status_code, response.text)

            return json


class RequestError(Exception):

    def __init__(self, message, status_code, data=None):
        self.message = message
        self.status_code = status_code
        self.data = data

    def __repr__(self):
        return 'RequestError(message="{}", status="{}" data="{}")'.format(self.message, self.status_code, self.data)
