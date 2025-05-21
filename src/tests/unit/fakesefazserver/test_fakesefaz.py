import unittest

import requests

from tools.fakesefaz import FakeSefazServer, FixedResponseSefazHttpHandler


class FakeSefazIntegrationTest(unittest.TestCase):
    ServerPort = 8787

    def test_requestSent_fixedResponseReturned(self):
        server = None
        server_thread = None
        try:
            fixed_response = "<xml>FixedResponse</xml>".encode("utf-8")

            server = FakeSefazServer(FakeSefazIntegrationTest.ServerPort, aFixedResponseHandlerBuilder().with_fixed_response(fixed_response).build())
            server.startServing()

            response = requests.post("http://localhost:8787", timeout=10.0)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, fixed_response)
        finally:
            server.stopServing()

    def test_requestSent_requestPathRecoredAtServer(self):
        server = None
        try:
            server = FakeSefazServer(FakeSefazIntegrationTest.ServerPort, aFixedResponseHandlerBuilder().build())
            server.startServing()

            response = requests.post("http://localhost:8787/path/to/assert", timeout=10.0)

            self.assertTrue(server.has_received_request("/path/to/assert"))
        finally:
            server.stopServing()

    def test_requestSent_requestBodyRecordedAtServer(self):
        server = None
        try:
            server = FakeSefazServer(FakeSefazIntegrationTest.ServerPort, aFixedResponseHandlerBuilder().build())
            server.startServing()

            response = requests.post("http://localhost:8787/path/to/assert", data="data_to_record", timeout=10.0)

            self.assertTrue(server.received_request_body_contains("/path/to/assert", "data_to_record"))
        finally:
            server.stopServing()
            
    def test_validXMLCorrectlyValidatedInSefaz(self):
        server = None
        try:
            xml = """<inutNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="3.10"><infInut Id="ID43171357459404430465001000003950000003950"><tpAmb>2</tpAmb><xServ>INUTILIZAR</xServ><cUF>43</cUF><ano>17</ano><CNPJ>13574594044304</CNPJ><mod>65</mod><serie>1</serie><nNFIni>3950</nNFIni><nNFFin>3950</nNFFin><xJust>Pedido cancelado</xJust></infInut><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1" /><Reference URI="#ID43171357459404430465001000003950000003950"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" /><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" /><DigestValue>Re/8HoduY4vOin2qcJN5S0EQPRw=</DigestValue></Reference></SignedInfo><SignatureValue>c/Evhgzfx7Mm9c5O/Q/eB0UcSDycld3YNRK+rnEhGOBHbF5E95wB+jKDl9NygGBsctPe3TT1usER7TeQfsoOZsqWu+THlAam5HIe0tFVLl3be546yaBn2KsncT7DRO2syU84gKbuv7MFPtDdWQQvpN+HiFX1zVXIyHbkeMBnGrqvcn6It94q/x9ebW+BgHpxck+bA3O9w6DGWkQFYN31wcYt8RpQ+eRbDVnl7o0gqu+1XGc7bAnjxTDIoKnmAc4QrltyRaHBEW+nDwNmeqDE88r67kFs+jwQTUoOoAT4JS2vYQTEYg3feVNT0ESFTRnZ5Ckp1z5AThf5V0bG7hzdlw==</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIILzCCBhegAwIBAgIQSLmPrB9lX+JUGMok0G6C2TANBgkqhkiG9w0BAQsFADB4
MQswCQYDVQQGEwJCUjETMBEGA1UEChMKSUNQLUJyYXNpbDE2MDQGA1UECxMtU2Vj
cmV0YXJpYSBkYSBSZWNlaXRhIEZlZGVyYWwgZG8gQnJhc2lsIC0gUkZCMRwwGgYD
VQQDExNBQyBDZXJ0aXNpZ24gUkZCIEc1MB4XDTE3MDMxMzE3MDkwOFoXDTE4MDMx
MzE3MDkwOFowggETMQswCQYDVQQGEwJCUjETMBEGA1UECgwKSUNQLUJyYXNpbDEL
MAkGA1UECAwCU1AxEDAOBgNVBAcMB0JBUlVFUkkxNjA0BgNVBAsMLVNlY3JldGFy
aWEgZGEgUmVjZWl0YSBGZWRlcmFsIGRvIEJyYXNpbCAtIFJGQjEWMBQGA1UECwwN
UkZCIGUtQ05QSiBBMTE2MDQGA1UECwwtQXV0ZW50aWNhZG8gcG9yIEF1dG9yaWRh
ZGUgZGUgUmVnaXN0cm8gQ05CIFNQMUgwRgYDVQQDDD9CSyBCUkFTSUwgT1BFUkFD
QU8gRSBBU1NFU1NPUklBIEEgUkVTVEFVUkFOVEVTIFM6MTM1NzQ1OTQwMDAxOTYw
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCj7NGOqGlM3oqJwaupLvxO
YlCGey4m9L+PDEhA2fib8OJa3EA8AykYa+28E7xolMfgTyb94ocgv0CWe1Zyre21
b1oo1mlqQCI396/HM6d+oCY6ZV5hbLF6JYadfzP581cKOOr2NxC+v4GzBRXws1CP
RyhTmNFPsDqfUjBRPl4F2JQudLFsI8JCxoqvLmOpZr9lk2pKU+0m9wdvtJRWrh3j
5+j2CaxVftwGng7BHOb7gy2L7A08NEiu/7eEe2ukT9zwagqkFet54aLYzr9mvcsX
cCikrDmkNU8MYJvO2PjTTdRB1u0jyXEF/k2T+p05g9C0mMN2Y7mjIonyAgockCE7
AgMBAAGjggMWMIIDEjCBxQYDVR0RBIG9MIG6oD0GBWBMAQMEoDQEMjA4MTExOTY4
NDIyNzQxMTc1MDAwMDAwMDAwMDAwMDAwMDAwMDAwMjczNjYyNFNTUEJBoCEGBWBM
AQMCoBgEFklVUkkgREUgQVJBVUpPIE1JUkFOREGgGQYFYEwBAwOgEAQOMTM1NzQ1
OTQwMDAxOTagFwYFYEwBAwegDgQMMDAwMDAwMDAwMDAwgSJlZHVhcmRvLmNhcnZh
bGhvQGJ1cmdlcmtpbmcuY29tLmJyMAkGA1UdEwQCMAAwHwYDVR0jBBgwFoAUU31/
nb7RYdAgutqf44mnE3NYzUIwfwYDVR0gBHgwdjB0BgZgTAECAQwwajBoBggrBgEF
BQcCARZcaHR0cDovL2ljcC1icmFzaWwuY2VydGlzaWduLmNvbS5ici9yZXBvc2l0
b3Jpby9kcGMvQUNfQ2VydGlzaWduX1JGQi9EUENfQUNfQ2VydGlzaWduX1JGQi5w
ZGYwgbwGA1UdHwSBtDCBsTBXoFWgU4ZRaHR0cDovL2ljcC1icmFzaWwuY2VydGlz
aWduLmNvbS5ici9yZXBvc2l0b3Jpby9sY3IvQUNDZXJ0aXNpZ25SRkJHNS9MYXRl
c3RDUkwuY3JsMFagVKBShlBodHRwOi8vaWNwLWJyYXNpbC5vdXRyYWxjci5jb20u
YnIvcmVwb3NpdG9yaW8vbGNyL0FDQ2VydGlzaWduUkZCRzUvTGF0ZXN0Q1JMLmNy
bDAOBgNVHQ8BAf8EBAMCBeAwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwME
MIGsBggrBgEFBQcBAQSBnzCBnDBfBggrBgEFBQcwAoZTaHR0cDovL2ljcC1icmFz
aWwuY2VydGlzaWduLmNvbS5ici9yZXBvc2l0b3Jpby9jZXJ0aWZpY2Fkb3MvQUNf
Q2VydGlzaWduX1JGQl9HNS5wN2MwOQYIKwYBBQUHMAGGLWh0dHA6Ly9vY3NwLWFj
LWNlcnRpc2lnbi1yZmIuY2VydGlzaWduLmNvbS5icjANBgkqhkiG9w0BAQsFAAOC
AgEAWbnnApNknMC5i41VoxJnfqJWtZxQvdgUb3IJjAlK/CpYnbXW4X21wfZ2lxS4
011nvvfYnk3ZhyTvx9W7/ibQUwiXlDMP1b16fdzdDq55lV97EnrNWr1pB8yuViZ9
05jB/WZtySqQMlOTpqUc1WdEnlmtXBmYvdoOKrkFYryhul4I+h/ftCFL6Y9rrMu0
NXI+lXpju8hqP7jcPAz32ApXsWfoUS3wbHDadbIQ54gMBR38xxQK9t0Gfk+J/RUC
19hoNkfZ5z+a4vqI7lXprxQ7I3CPdgurT5zrjMWsTmgX/jWxBFRvk6dhtEMahOM7
bMbI4OhKbUNvftwSqDfTKiwCHbWwMVBXkD3Wj3dWGFng/5X9NWk8txU/zuroNJxA
1sYf24umssm+u2Dgmrj3n3rUJNs0JB1yazsor/1fLA+Hx3EBDM498pWVRi7WK4wq
bl9W0JhxCf2BpYG709fDzbD7Vmrd/n7fOPZc1FSuHvJIc+RMu085yzsYLMutTKJG
NjgdfKa+BibeDnocvp3g24uG1S43FJGEzN/js0ri4WRQKxnxYorWjAgFi0y+nlcR
AN/jaAhnww/avEowYG6+WQGd8cNNzEWOyqB1wUE9amuIxTH6161F/KapXGKrfK8E
toHI26Qk4kY9u+takNfSlxO3m81IdyyO8Lkkj1VdFNF3fh4=
</X509Certificate></X509Data></KeyInfo></Signature></inutNFe>"""
            
            server = FakeSefazServer(FakeSefazIntegrationTest.ServerPort, aFixedResponseHandlerBuilder().build())
            server.startServing()

            response = requests.post("http://localhost:8787/path/to/assert", data=xml, timeout=10.0)

            self.assertTrue(server.received_requests_are_valid_xmls())
        finally:
            server.stopServing()

    def test_invalidXMLCorrectlyInvalidatedInSefaz(self):
        server = None
        try:
            xml = """<inutNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="3.10"><infInut Id="ID431713574594044304650010000039500000039"><tpAmb>2</tpAmb><xServ>INUTILIZAR</xServ><cUF>43</cUF><ano>17</ano><CNPJ>13574594044304</CNPJ><mod>65</mod><serie>1</serie><nNFIni>3950</nNFIni><nNFFin>3950</nNFFin><xJust>Pedido cancelado</xJust></infInut><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1" /><Reference URI="#ID43171357459404430465001000003950000003950"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" /><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" /><DigestValue>Re/8HoduY4vOin2qcJN5S0EQPRw=</DigestValue></Reference></SignedInfo><SignatureValue>c/Evhgzfx7Mm9c5O/Q/eB0UcSDycld3YNRK+rnEhGOBHbF5E95wB+jKDl9NygGBsctPe3TT1usER7TeQfsoOZsqWu+THlAam5HIe0tFVLl3be546yaBn2KsncT7DRO2syU84gKbuv7MFPtDdWQQvpN+HiFX1zVXIyHbkeMBnGrqvcn6It94q/x9ebW+BgHpxck+bA3O9w6DGWkQFYN31wcYt8RpQ+eRbDVnl7o0gqu+1XGc7bAnjxTDIoKnmAc4QrltyRaHBEW+nDwNmeqDE88r67kFs+jwQTUoOoAT4JS2vYQTEYg3feVNT0ESFTRnZ5Ckp1z5AThf5V0bG7hzdlw==</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIILzCCBhegAwIBAgIQSLmPrB9lX+JUGMok0G6C2TANBgkqhkiG9w0BAQsFADB4
MQswCQYDVQQGEwJCUjETMBEGA1UEChMKSUNQLUJyYXNpbDE2MDQGA1UECxMtU2Vj
cmV0YXJpYSBkYSBSZWNlaXRhIEZlZGVyYWwgZG8gQnJhc2lsIC0gUkZCMRwwGgYD
VQQDExNBQyBDZXJ0aXNpZ24gUkZCIEc1MB4XDTE3MDMxMzE3MDkwOFoXDTE4MDMx
MzE3MDkwOFowggETMQswCQYDVQQGEwJCUjETMBEGA1UECgwKSUNQLUJyYXNpbDEL
MAkGA1UECAwCU1AxEDAOBgNVBAcMB0JBUlVFUkkxNjA0BgNVBAsMLVNlY3JldGFy
aWEgZGEgUmVjZWl0YSBGZWRlcmFsIGRvIEJyYXNpbCAtIFJGQjEWMBQGA1UECwwN
UkZCIGUtQ05QSiBBMTE2MDQGA1UECwwtQXV0ZW50aWNhZG8gcG9yIEF1dG9yaWRh
ZGUgZGUgUmVnaXN0cm8gQ05CIFNQMUgwRgYDVQQDDD9CSyBCUkFTSUwgT1BFUkFD
QU8gRSBBU1NFU1NPUklBIEEgUkVTVEFVUkFOVEVTIFM6MTM1NzQ1OTQwMDAxOTYw
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCj7NGOqGlM3oqJwaupLvxO
YlCGey4m9L+PDEhA2fib8OJa3EA8AykYa+28E7xolMfgTyb94ocgv0CWe1Zyre21
b1oo1mlqQCI396/HM6d+oCY6ZV5hbLF6JYadfzP581cKOOr2NxC+v4GzBRXws1CP
RyhTmNFPsDqfUjBRPl4F2JQudLFsI8JCxoqvLmOpZr9lk2pKU+0m9wdvtJRWrh3j
5+j2CaxVftwGng7BHOb7gy2L7A08NEiu/7eEe2ukT9zwagqkFet54aLYzr9mvcsX
cCikrDmkNU8MYJvO2PjTTdRB1u0jyXEF/k2T+p05g9C0mMN2Y7mjIonyAgockCE7
AgMBAAGjggMWMIIDEjCBxQYDVR0RBIG9MIG6oD0GBWBMAQMEoDQEMjA4MTExOTY4
NDIyNzQxMTc1MDAwMDAwMDAwMDAwMDAwMDAwMDAwMjczNjYyNFNTUEJBoCEGBWBM
AQMCoBgEFklVUkkgREUgQVJBVUpPIE1JUkFOREGgGQYFYEwBAwOgEAQOMTM1NzQ1
OTQwMDAxOTagFwYFYEwBAwegDgQMMDAwMDAwMDAwMDAwgSJlZHVhcmRvLmNhcnZh
bGhvQGJ1cmdlcmtpbmcuY29tLmJyMAkGA1UdEwQCMAAwHwYDVR0jBBgwFoAUU31/
nb7RYdAgutqf44mnE3NYzUIwfwYDVR0gBHgwdjB0BgZgTAECAQwwajBoBggrBgEF
BQcCARZcaHR0cDovL2ljcC1icmFzaWwuY2VydGlzaWduLmNvbS5ici9yZXBvc2l0
b3Jpby9kcGMvQUNfQ2VydGlzaWduX1JGQi9EUENfQUNfQ2VydGlzaWduX1JGQi5w
ZGYwgbwGA1UdHwSBtDCBsTBXoFWgU4ZRaHR0cDovL2ljcC1icmFzaWwuY2VydGlz
aWduLmNvbS5ici9yZXBvc2l0b3Jpby9sY3IvQUNDZXJ0aXNpZ25SRkJHNS9MYXRl
c3RDUkwuY3JsMFagVKBShlBodHRwOi8vaWNwLWJyYXNpbC5vdXRyYWxjci5jb20u
YnIvcmVwb3NpdG9yaW8vbGNyL0FDQ2VydGlzaWduUkZCRzUvTGF0ZXN0Q1JMLmNy
bDAOBgNVHQ8BAf8EBAMCBeAwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwME
MIGsBggrBgEFBQcBAQSBnzCBnDBfBggrBgEFBQcwAoZTaHR0cDovL2ljcC1icmFz
aWwuY2VydGlzaWduLmNvbS5ici9yZXBvc2l0b3Jpby9jZXJ0aWZpY2Fkb3MvQUNf
Q2VydGlzaWduX1JGQl9HNS5wN2MwOQYIKwYBBQUHMAGGLWh0dHA6Ly9vY3NwLWFj
LWNlcnRpc2lnbi1yZmIuY2VydGlzaWduLmNvbS5icjANBgkqhkiG9w0BAQsFAAOC
AgEAWbnnApNknMC5i41VoxJnfqJWtZxQvdgUb3IJjAlK/CpYnbXW4X21wfZ2lxS4
011nvvfYnk3ZhyTvx9W7/ibQUwiXlDMP1b16fdzdDq55lV97EnrNWr1pB8yuViZ9
05jB/WZtySqQMlOTpqUc1WdEnlmtXBmYvdoOKrkFYryhul4I+h/ftCFL6Y9rrMu0
NXI+lXpju8hqP7jcPAz32ApXsWfoUS3wbHDadbIQ54gMBR38xxQK9t0Gfk+J/RUC
19hoNkfZ5z+a4vqI7lXprxQ7I3CPdgurT5zrjMWsTmgX/jWxBFRvk6dhtEMahOM7
bMbI4OhKbUNvftwSqDfTKiwCHbWwMVBXkD3Wj3dWGFng/5X9NWk8txU/zuroNJxA
1sYf24umssm+u2Dgmrj3n3rUJNs0JB1yazsor/1fLA+Hx3EBDM498pWVRi7WK4wq
bl9W0JhxCf2BpYG709fDzbD7Vmrd/n7fOPZc1FSuHvJIc+RMu085yzsYLMutTKJG
NjgdfKa+BibeDnocvp3g24uG1S43FJGEzN/js0ri4WRQKxnxYorWjAgFi0y+nlcR
AN/jaAhnww/avEowYG6+WQGd8cNNzEWOyqB1wUE9amuIxTH6161F/KapXGKrfK8E
toHI26Qk4kY9u+takNfSlxO3m81IdyyO8Lkkj1VdFNF3fh4=
</X509Certificate></X509Data></KeyInfo></Signature></inutNFe>"""

            server = FakeSefazServer(FakeSefazIntegrationTest.ServerPort, aFixedResponseHandlerBuilder().build())
            server.startServing()

            response = requests.post("http://localhost:8787/path/to/assert", data=xml, timeout=10.0)

            self.assertFalse(server.received_requests_are_valid_xmls())
        finally:
            server.stopServing()


def aFixedResponseHandlerBuilder():
    return FixedResponseHandlerBuilder()


class FixedResponseHandlerBuilder(object):
    def __init__(self):
        self.fixed_response = ""

    def with_fixed_response(self, fixed_response):
        # type: (unicode) -> FixedResponseBuilder
        self.fixed_response = fixed_response
        return self

    def build(self):
        FixedResponseSefazHttpHandler.Response = self.fixed_response
        return FixedResponseSefazHttpHandler

