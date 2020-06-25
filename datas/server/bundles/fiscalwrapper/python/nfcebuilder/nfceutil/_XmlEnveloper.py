class XmlEnveloper(object):
    NAMESPACE_SOAP = "http://www.w3.org/2003/05/soap-envelope"

    def __init__(self, c_uf):
        self.c_uf = str(c_uf)

    def envelop(self, xml, webservice_namespace, versao_ws):
        prefix = '<Envelope xmlns="{0}">'\
                     '<Header>'\
                         '<nfeCabecMsg xmlns="{1}">'\
                             '<cUF>{2}</cUF>'\
                             '<versaoDados>{3:.2f}</versaoDados>'\
                             '</nfeCabecMsg>'\
                      '</Header>'\
                      '<Body>'\
                          '<nfeDadosMsg xmlns="{1}">'\
            .format(XmlEnveloper.NAMESPACE_SOAP, webservice_namespace, self.c_uf, 3.1 if versao_ws in (1, 3) else 4)
        suffix = "</nfeDadosMsg></Body></Envelope>"
        return prefix + xml + suffix
