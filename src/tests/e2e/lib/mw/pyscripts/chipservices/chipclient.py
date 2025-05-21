# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\chipservices\chipclient.py
import os
import json
from hashlib import md5
from mwapp import http
import systools

class HTTPError(Exception):

    def __init__(self, code, reason):
        self.code = code
        self.reason = reason

    def __str__(self):
        return '{0} ({1}).'.format(self.message, self.code)


class ChipError(Exception):

    def __init__(self, error, http_status_code):
        self.code = error.get('code', -1)
        self.messages = error.get('messages', [])
        self.url = error.get('url', '')
        self.status_code = http_status_code

    def __str__(self):
        return 'HTTP {0}: {1} ({2}).'.format(self.status_code, self.messages, self.code)


class ChipClient(object):
    """  ChipClient(name, base_url) -> ChipClient
    
        This class is a client implementation for the CHIP services API. It aims
        to wrap some of the conventions followed into an easy to use library for
        accessing CHIP resources.
    
        @param base_url: {str} - base URL for CHIP services (up to resource endpoints)
        @return: ChipClient instance.
    """

    def __init__(self, base_url, service):
        self.base_url = os.path.join(base_url, service)
        self.service = service
        self.default_headers = {'Content-Type': 'application/json'}

    def request(self, resource, method, data = {}, headers = {}, params = {}):
        """ request
        
            @param resource: {str} - name of resource endpoint (URN)
            @param method: {str} - http method verb
            @param data: {dict} - dictionary converted into JSON used as request body
            @param headers: {dict} - dictionary holding header key/value pairs for the request
            @param params: {dict} - dictionary holding query parameters
            @return: {dict} - resource data dictionary
        """
        url = os.path.join(self.base_url, resource)
        headers.update(self.default_headers)
        r = http.request(method, url, params=params, data=data, headers=headers)
        systools.sys_log_debug('CHIP {0} request to {1}: params={2}, data={3}, headers={4}'.format(method, url, params, data, headers))
        if r.body:
            payload = json.loads(r.body)
        else:
            payload = {}
        if 400 <= r.status <= 499:
            raise ChipError(payload.get('error', {}), r.status)
        elif 500 <= r.status <= 599:
            raise HTTPError(r.status, r.reason)
        correlation_id = payload.get('correlationId')
        request = payload.get('request', {})
        data = payload.get('data', {})
        systools.sys_log_debug('CHIP response {0}: request={1}, data={2}'.format(correlation_id, request, data))
        return data

    def get(self, resource, filters = {}):
        obj = self.request(resource, 'GET', params=filters)
        return obj

    def post(self, resource, filters = {}, data = {}):
        obj = self.request(resource, 'POST', params=filters, data=json.dumps(data))
        return obj

    def put(self, resource, filters = {}, data = {}):
        obj = self.request(resource, 'PUT', params=filters, data=data)
        return obj

    def patch(self, resource, filters = {}, data = {}):
        obj = self.request(resource, 'PATCH', params=filters, data=data)
        return obj

    def delete(self, resource, filters = {}):
        obj = self.request(resource, 'DELETE', params=filters)
        return obj

    def options(self, resource):
        obj = self.request(resource, 'OPTIONS')
        return obj

    @staticmethod
    def format_date(datetime_obj):
        return datetime_obj.strftime('%Y%m%d')


class ChipObject(object):
    """  ChipObject(object_dict) -> ChipObject
    
        This class represents a CHIP object and contains helper
        functions for accessing the object data.
    
        @param object_dict: {dict} - chip object dictionary from Chip Services
        @return: ChipObject instance.
    """

    def __init__(self, object_dict):
        self.object_dict = object_dict

    def get_payload(self, check_hash = True, encoding = 'UTF-8'):
        """ get_payload
        
            @param check_hash: {bool} - compare the computed hash value to the stored hash value for the object payload
            @param encoding: {str} - character encoding for payload
            @return: {str} - payload contents
        """
        valid_hash = self.object_dict.get('hash')
        payload = self.object_dict.get('payload')
        if payload:
            contents = payload.encode(encoding)
        else:
            raise ValueError('Invalid payload ({0})'.format(payload))
        if check_hash and valid_hash:
            valid_hash = valid_hash.lower()
            new_hash = md5(contents).hexdigest().lower()
            if not valid_hash == new_hash:
                raise ValueError('Hash mismatch: checked={0}, valid={1}'.format(new_hash, valid_hash))
        return contents


class ChipRepository(ChipClient):
    """  ChipRepository(ChipClient) -> ChipRepository
    
        This is a wrapper class for accessing the "repo" API from Chip Services.
        It provides easy access to CHIP objects.
    
        @param base_url: {str} - chip object dictionary from Chip Services
        @return: ChipRepository instance.
    """

    def __init__(self, base_url):
        super(ChipRepository, self).__init__(base_url=base_url, service='repo')

    def get_dimensions(self):
        """ get_dimensions
        
            @return: {dict} - dictionary containing the CHIP dimensions data.
        """
        data = self.get('dimensions')
        return data

    def get_object(self, object_type, cafe_nbr = None, effective_date = None, version = None):
        """ get_object
        
            @param object_type: {str} - type of object to retrieve. Matches Chip object_type_cd values
            @param cafe_nbr: {int} - cafe number
            @param effective_date: {datetime.datetime} - date payload is effective for
            @param version: {str} - major.minor version number
            @return: {ChipObject} - Chip Object that matches provided object_type
        """
        cafe_path = 'cafes/{0}'.format(cafe_nbr) if cafe_nbr else ''
        resource_path = os.path.join(cafe_path, 'cbos', object_type)
        filters = {}
        if effective_date:
            filters.update({'effectivedate': self.format_date(effective_date)})
        if version:
            filters.update({'version': version})
        data = self.get(resource_path, filters)
        return ChipObject(data)