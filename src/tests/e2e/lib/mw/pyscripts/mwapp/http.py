# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\http.py
import httplib
import urllib
import urlparse
import ssl

class RequestError(Exception):

    def __init__(self, status, reason, body):
        self.status = status
        self.reason = reason
        self.body = body

    def __str__(self):
        return 'Http Request Error: {0}-{1}'.format(self.status, self.reason)


class Response(object):
    """ Response(status, reason, body, headers) -> Response
    
        Simple class for holding HTTP response values
    
        @param status: {str} - HTTP status code
        @param reason: {str} - HTTP reason message
        @param body: {str} - HTTP response body
        @param headers: {dict} - HTTP response headers
        @return: Response instance.
    """

    def __init__(self, status, reason, body, headers):
        self.status = status
        self.reason = reason
        self.body = body
        self.headers = headers


def request(method, url, params = {}, data = {}, headers = {}, timeout = 10, depth = 0):
    """ request(method, url, params={}, data={}, headers={}, timeout=10)
    
        Generic wrapper function for making HTTP requests
    
        @param method: {str} - HTTP request method
        @param url: {str} - full request url
        @param params: {dict} - query params to be encoded and appended to the url
        @param data: {str} - post data string
        @param headers: {dict} - HTTP response headers
        @param timeout: {int} - Request timeout value in seconds
        @return: Response instance.
    """
    if depth >= 10:
        raise Exception('Entered redirect loop.')
    parts = urlparse.urlparse(url)
    query_string = urllib.urlencode(params)
    if parts.scheme == 'http':
        conn = httplib.HTTPConnection(parts.netloc, timeout=timeout)
    elif parts.scheme == 'https':
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            conn = httplib.HTTPSConnection(parts.netloc, timeout=timeout)
        else:
            ssl._create_default_https_context = _create_unverified_https_context
            conn = httplib.HTTPSConnection(parts.netloc, timeout=timeout, context=ssl._create_unverified_context())

    else:
        raise ValueError('Unsupported scheme {0}'.format(parts.scheme))
    if query_string:
        uri = '{0}?{1}'.format(parts.path, query_string)
    else:
        uri = parts.path
    conn.request(method.upper(), uri, body=data, headers=headers)
    response = conn.getresponse()
    if 300 < response.status <= 399:
        return request(method, response.getheader('Location'), params, data, headers, timeout, depth=depth + 1)
    rsp = Response(response.status, response.reason, response.read(), dict(response.getheaders()))
    conn.close()
    return rsp


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def post(url, data = None, **kwargs):
    return request('POST', url, data=data, **kwargs)


def put(url, data = None, **kwargs):
    return request('PUT', url, data=data, **kwargs)


def patch(url, data = None, **kwargs):
    return request('PATCH', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


def head(url, **kwargs):
    return request('HEAD', url, **kwargs)


def options(url, **kwargs):
    return request('OPTIONS', url, **kwargs)