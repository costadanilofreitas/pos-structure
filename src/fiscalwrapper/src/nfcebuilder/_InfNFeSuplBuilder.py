import hashlib
from datetime import datetime

from pos_model import Order
from typing import Dict, Any

from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder


class InfNFeSuplBuilder(NfceXmlPartBuilder):

    def __init__(self, ambiente, cid_token, csc, qrcode_base_url, qrcode_check_url, versao_ws):
        self.environment_identifier = ambiente
        self.csc_identifier = cid_token
        self.csc = csc
        self.qrcode_base_url = qrcode_base_url
        self.qrcode_check_url = qrcode_check_url
        self.ws_version = versao_ws

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        qrcode_version = 1 if self.ws_version in (0, 1, 3) else 2
        access_key = context[ContextKeys.nfce_key]
        emission_date = context[ContextKeys.data_emissao]
        nf_value = context[ContextKeys.v_nf] # type: float
        icms_value = context[ContextKeys.total_icms] # type: float
        digest_value = context[ContextKeys.digest_value].encode("hex")

        if self.ws_version in (0, 1, 3):
            cdata = self._get_cdata_for_nfce_1_or_3(context, emission_date, digest_value, access_key, nf_value, icms_value)
        elif self.ws_version == 4:
            cdata = self._get_cdata_for_nfce_4(context, emission_date, digest_value, access_key, qrcode_version, nf_value)
        else:
            raise Exception("Version of NFCE not supported. ws_version: {}".format(self.ws_version))

        qrcode = u"<qrCode><![CDATA[{0}]]></qrCode>".format(cdata)
        if self.ws_version == 4:
            qrcode += u"<urlChave>{0}</urlChave>".format(self.qrcode_check_url)
        infnfe_supl = u"<infNFeSupl>{0}</infNFeSupl>".format(qrcode)

        return infnfe_supl

    def _get_cdata_for_nfce_1_or_3(self, context, emission_date, digest_value, access_key, nf_value, icms_value):
        # type: (Dict[unicode, Any], unicode, unicode, unicode, float, float) -> unicode

        hash_params = u"chNFe={0}&nVersao=100&tpAmb={1}".format(access_key, self.environment_identifier)
        hash_params = self._get_cpf_cnpj(context, hash_params)
        hash_params += u"&dhEmi={0}&vNF={1:>0.2f}&vICMS={2:>0.2f}&digVal={3}&cIdToken={4}" \
            .format(emission_date.encode("hex"), nf_value, icms_value, digest_value, self.csc_identifier)

        hash_qrcode = hashlib.sha1(hash_params + self.csc).hexdigest()
        hash_params += u"&cHashQRCode={0}".format(hash_qrcode)
        cdata = self.qrcode_base_url + hash_params

        return cdata

    def _get_cdata_for_nfce_4(self, context, emission_date, digest_value, access_key, qrcode_version, nf_value):
        # type: (Dict[unicode, Any], unicode, unicode, unicode, int, float) -> unicode

        if not context[ContextKeys.is_in_contingency]:
            hash_params = u"{0}|{1}|{2}|{3}".format(access_key, qrcode_version, self.environment_identifier, int(self.csc_identifier))

            hash_qrcode = hashlib.sha1(hash_params + self.csc).hexdigest()
            cdata = self._create_cdata_online(hash_qrcode, access_key, qrcode_version)
        else:
            nf_value = "%.02f" % nf_value
            emission_day = datetime.strptime(emission_date.split("T")[0], "%Y-%m-%d").day
            emission_day = str(emission_day).zfill(2)
            hash_params = u"{0}|{1}|{2}|{3}|{4}|{5}|{6}".format(access_key, qrcode_version, self.environment_identifier,
                                                                emission_day, nf_value, digest_value, int(self.csc_identifier))

            hash_qrcode = hashlib.sha1(hash_params + self.csc).hexdigest()
            cdata = self._create_cdata_offline(hash_qrcode, access_key, qrcode_version, emission_day, nf_value, digest_value)

        return cdata

    def _create_cdata_online(self, hash_qrcode, access_key, qrcode_version):
        # type: (unicode, unicode, int) -> unicode

        cdata = u"{url_sefaz}p={chave_de_acesso}|" \
                u"{versao_do_qr_code}|" \
                u"{tipo_de_ambiente}|" \
                u"{identificador_do_csc}|" \
                u"{codigo_hash}" \
            .format(url_sefaz=self.qrcode_base_url,
                    chave_de_acesso=access_key,
                    versao_do_qr_code=qrcode_version,
                    tipo_de_ambiente=self.environment_identifier,
                    identificador_do_csc=int(self.csc_identifier),
                    codigo_hash=hash_qrcode.upper())

        return cdata

    def _create_cdata_offline(self, hash_qrcode, access_key, qrcode_version, emission_day, nf_value, digest_value):
        # type: (unicode, unicode, int, unicode, unicode, unicode) -> unicode

        cdata = u"{url_sefaz}p={chave_de_acesso}|" \
                u"{versao_do_qr_code}|" \
                u"{tipo_de_ambiente}|" \
                u"{dia_emissao}|" \
                u"{valor_total_nfce}|" \
                u"{digest_value}|" \
                u"{identificador_do_csc}|" \
                u"{codigo_hash}" \
            .format(url_sefaz=self.qrcode_base_url,
                    chave_de_acesso=access_key,
                    versao_do_qr_code=qrcode_version,
                    tipo_de_ambiente=self.environment_identifier,
                    dia_emissao=emission_day,
                    valor_total_nfce=nf_value,
                    digest_value=digest_value,
                    identificador_do_csc=int(self.csc_identifier),
                    codigo_hash=hash_qrcode.upper())

        return cdata

    @staticmethod
    def _get_cpf_cnpj(context, hash_params):
        # type: (Dict[unicode, Any], unicode) -> unicode

        cpf_cnpj = None
        if ContextKeys.cpf_cnpj in context:
            cpf_cnpj = context[ContextKeys.cpf_cnpj]

        if cpf_cnpj is not None:
            hash_params += u"&cDest=" + cpf_cnpj

        return hash_params