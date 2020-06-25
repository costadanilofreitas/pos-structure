from requests import Request, Session, Response
from typing import Optional


class NfceRequest(object):
    def __init__(self, certificate_key_path, certificate_path, sefaz_certificate_path, check_situation_timeout):
        self.certificate_key_path = certificate_key_path
        self.certificate_path = certificate_path
        self.sefaz_certificate_path = sefaz_certificate_path
        self.check_situation_timeout = check_situation_timeout

    def envia_nfce(self, request, url, soap_action=None, timeout=None):
        # type: (str, str, Optional[str], Optional[int]) -> Response

        req = Request('POST', url, data=request)
        prepared_request = req.prepare()

        prepared_request.headers['Content-Type'] = 'application/soap+xml; charset=utf-8'
        if soap_action is not None:
            prepared_request.headers['SOAPAction'] = soap_action

        cert = (self.certificate_path, self.certificate_key_path)
        ca_cert = self.sefaz_certificate_path

        s = Session()
        resp = s.send(
            prepared_request,
            cert=cert,
            verify=ca_cert,
            timeout=timeout or self.check_situation_timeout
        )
        return resp
