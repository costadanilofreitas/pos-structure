from xml.etree import ElementTree

import signxml
from signxml import XMLSigner


class NfeSigner(object):
    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"

    def __init__(self, key_path, certificate_path):
        self.certificate_key = open(key_path, "rb").read().replace("\r\n", "\n")
        self.certificate_cert = open(certificate_path, "rb").read().replace("\r\n", "\n")

    def sign_xml(self, xml, tag_to_sign, parameter_to_sign):
        # type: (str, str, str) -> ElementTree.Element
        ElementTree.register_namespace('', NfeSigner.NAMESPACE_NFE)
        root = ElementTree.XML(xml)
        xml_parameter = root.find("{{{0}}}{1}".format(NfeSigner.NAMESPACE_NFE, tag_to_sign)).attrib[parameter_to_sign]
        signed_root = XMLSigner(
            method=signxml.methods.enveloped, signature_algorithm=u'rsa-sha1', digest_algorithm=u'sha1',
            c14n_algorithm=u'http://www.w3.org/TR/2001/REC-xml-c14n-20010315').sign(
            root, key=self.certificate_key, cert=self.certificate_cert, reference_uri=xml_parameter)
        return ElementTree.tostring(signed_root)

    def sign_cancel_xml(self, xml):
        # type: (str) -> ElementTree.Element
        ElementTree.register_namespace('', NfeSigner.NAMESPACE_NFE)
        root = ElementTree.XML(xml)
        element = root.find("{{{0}}}evento".format(NfeSigner.NAMESPACE_NFE))
        xml_attribute = root.find("{{{0}}}evento/{{{0}}}infEvento".format(NfeSigner.NAMESPACE_NFE)).attrib['Id']
        signed_element = XMLSigner(
            method=signxml.methods.enveloped, signature_algorithm=u'rsa-sha1', digest_algorithm=u'sha1',
            c14n_algorithm=u'http://www.w3.org/TR/2001/REC-xml-c14n-20010315').sign(
            element, key=self.certificate_key, cert=self.certificate_cert, reference_uri=xml_attribute)

        root.remove(element)
        root.append(signed_element)
        return ElementTree.tostring(root)

    def get_signature(self, nfe):
        # type: (unicode) -> unicode
        ElementTree.register_namespace('', NfeSigner.NAMESPACE_NFE)
        root = ElementTree.XML(nfe)
        nfe_id = root.find("{{{0}}}infNFe".format(NfeSigner.NAMESPACE_NFE)).attrib['Id']
        signed_root = signxml.XMLSigner(
            method=signxml.methods.enveloped,
            signature_algorithm=u'rsa-sha1',
            digest_algorithm=u'sha1',
            c14n_algorithm=u'http://www.w3.org/TR/2001/REC-xml-c14n-20010315') \
            .sign(root, key=self.certificate_key, cert=self.certificate_cert, reference_uri=nfe_id)

        return ElementTree.tostring(signed_root.find("Signature"))