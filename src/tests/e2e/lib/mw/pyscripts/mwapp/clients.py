# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\clients.py
import os
import json
import traceback
import http
MWAPP_API_BASE_PATH = '/mwapp/services'

class ServiceError(Exception):

    def __init__(self, message, rc = 0, stack = ''):
        self.rc = rc
        self.stack_trace = stack
        self.message = message

    def __str__(self):
        return '{0} ({1}). {2}'.format(self.message, self.rc, self.stack_trace)


class ServiceClient(object):
    """ ServiceClient(host_address, name, type=None) -> ServiceClient
    
        This class represents a client that can send messages to or call tasks for a "Service" component. The messages
        are routed through the MWApp web service channel.
    
        @param host: {str} - MWAPP server host (address:port)
        @param name: {str} - component name
        @param type: {str} - component type. If None the name will be used as the type
        @return: ServiceClient instance.
    """

    def __init__(self, host_address, name, type = None):
        self.host_address = host_address
        self.service_name = name
        self.service_type = type or name

    def send_message(self, **kwargs):
        """ send_message(**kwargs)
        
            This method posts a request to the MWApp web service as an "event" message
            to be handled by the specified "Service" component. The method will take an
            arbitrary input keyword arguments that will be serialized into a JSON string.
            The body of the response is assumed to be in JSON format.
        
            @param kwargs: {dict} - Message body.
            @raise ServiceError: If JSON serialization fails or the request returns with an error code or TK_SYS_NAK
            @return: {dict} - response body deserialized into a dictionary
        """
        body = json.dumps(kwargs) if kwargs else None
        params = {'token': 'TK_EVT_EVENT',
         'format': 'FM_STRING',
         'timeout': '-1',
         'isbase64': 'false'}
        headers = {'Content-type': 'application/json',
         'Accept': 'text/plain'}
        path = os.path.join(MWAPP_API_BASE_PATH, self.service_name, self.service_type)
        base_url = 'http://{0}{1}'.format(self.host_address, path)
        response = http.post(base_url, params=params, data=body, headers=headers)
        try:
            data = json.loads(response.body)
            result = data['data']
        except ValueError:
            raise ServiceError('Error decoding response body', -1, traceback.format_exc())

        if response.status >= 400 or response.headers['x-token-name'] == 'TK_SYS_NAK':
            raise ServiceError(data.get('msgerr', ''), data.get('rc', -1), data.get('stack', ''))
        return result

    def run_task(self, name, **params):
        """ run_task(**params)
        
            This method a is a generic wrapper used to run a task on a "Service" component.
        
            A task is a JSON object in the form:
                {"task": <name_of_task>,
                 "params": ["param1: <param_1>,
                            "param2": <param2>]
                }
        
            @param name: {str} - name of task
            @param retries: {int} - number of times to retry sending message. Optional kwarg that defaults to 2.
            @param params: {dict} - task parameters
            @raise ServiceError: If JSON serialization fails or the request returns with an error code or TK_SYS_NAK
            @return: {dict} - response body deserialized into a dictionary
        """
        retries = params.pop('retries', 2)
        for n in range(retries + 1):
            try:
                res = self.send_message(task=name, params=params)
                return res
            except ServiceError:
                if n < retries:
                    pass
                else:
                    raise