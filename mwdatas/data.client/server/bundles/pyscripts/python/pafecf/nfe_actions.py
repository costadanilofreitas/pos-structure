# -*- coding: utf-8 -*-
# Python module responsible to implement Brazilian NF-e actions.
# This module should be loaded by the "pyscripts" component
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

# Python standard modules
import sys
import os
import random
import subprocess
import datetime
import urlparse
from xml.etree import cElementTree as etree
from cStringIO import StringIO
from xml.sax import saxutils
from decimal import Decimal as D
# Our modules
import pyscripts
import persistence
import fiscalprinter
from sysactions import get_storewide_config, remove_xml_prolog, action, get_model, \
    check_operator_logged, check_current_order, show_keyboard, show_form, \
    show_info_message, show_listbox, get_posot, get_pricelist, change_screen, \
    close_asynch_dialog, show_messagebox, show_confirmation, get_current_order
from systools import sys_log_exception, sys_log_warning, sys_log_debug
from posot import OrderTakerException
from pafecf import PAF_ECF

ZERO = D("0.00")
TENDER_CASH = "0"

# Message-bus context
mbcontext = pyscripts.mbcontext


class NFException(Exception):
    pass


class NFEDuplicadaxception(NFException):
    pass


def _get_additional_info(order, info, additional_info=""):
    info += "="
    if order:
        additional_info = order.findtext("AdditionalInfo")
    l = (additional_info or "").split('|')
    for item in l:
        if item.startswith(info):
            return item[len(info):].encode("UTF-8")
    return ""


def dv_nfe_id(nfe_id):
    """Calcula o digito verificador de um ID de NF-e.
    @param nfe_id ID da NF-e (com ou sem o DV) - 44 ou 43 digitos, respectivamente
    @return digito verificador
    """
    nfe_id = str(nfe_id)
    if len(nfe_id) == 44:
        nfe_id = nfe_id[:-1]
    if len(nfe_id) != 43:
        raise ValueError("Invalid nfe_id length. Expected 43 or 44. Received %d" % len(nfe_id))
    # Reverse the id
    rev = nfe_id[::-1]
    multiplier = 2
    sum = 0
    for c in rev:
        if multiplier > 9:
            multiplier = 2
        sum += (int(c) * multiplier)
        multiplier += 1
    mod = (sum % 11)
    if mod in (0, 1):
        return "0"
    return str(11 - mod)


def validate_cpf_cnpj(value, force_cnpj=False):
    def calcdv(numb):
        result = int()
        seq = reversed(((range(9, id_type[1], -1) * 2)[:len(numb)]))
        for digit, base in zip(numb, seq):
            result += int(digit) * int(base)
        dv = result % 11
        return (dv < 10) and dv or 0
    if len(value) not in (14, 11):
        return (False, None)
    id_type = (len(value) > 11 or force_cnpj) and ['CNPJ', 1] or ['CPF', -1]
    numb, xdv = value[:-2], value[-2:]
    dv1 = calcdv(numb)
    dv2 = calcdv(numb + str(dv1))
    return (('%d%d' % (dv1, dv2) == xdv and True or False), id_type[0])


def add_signature_template(out, nfe):
    w = out.write
    w('<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">')
    w('<SignedInfo>')
    w('<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>')
    w('<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>')
    w('<Reference URI="#NFe%s">' % nfe["nfe_id"])
    w('<Transforms>')
    w('<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>')
    w('<Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>')
    w('</Transforms>')
    w('<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>')
    w('<DigestValue></DigestValue>')
    w('</Reference>')
    w('</SignedInfo>')
    w('<SignatureValue></SignatureValue>')
    w('<KeyInfo>')
    w('<X509Data>')
    w('<X509Certificate></X509Certificate>')
    w('</X509Data>')
    w('</KeyInfo>')
    w('</Signature>')


def get_nfe_info(posid, order):
    import nfe_tables
    nfe = {}
    orderinfo = order.findtext("AdditionalInfo")
    nfe["order"] = order
    # Data from the order's "AdditionalInfo" ...
    nfe["nfe_number"] = int(_get_additional_info(None, "NFE_NUMBER", orderinfo))
    nfe["nfe_code"] = int(_get_additional_info(None, "NFE_CODE", orderinfo))
    nfe["nfe_ambiente"] = _get_additional_info(None, "NFE_AMBIENTE", orderinfo)
    nfe["dest_CNPJ"] = _get_additional_info(None, "NFE_CNPJ", orderinfo)
    nfe["dest_CPF"] = _get_additional_info(None, "NFE_CPF", orderinfo)
    nfe["dest_nome"] = _get_additional_info(None, "NFE_NOME", orderinfo)
    nfe["dest_logradouro"] = _get_additional_info(None, "NFE_LOGRADOURO", orderinfo)
    nfe["dest_numeroendereco"] = _get_additional_info(None, "NFE_NUMERO_END", orderinfo)
    nfe["dest_complemento"] = _get_additional_info(None, "NFE_COMPLEMENTO", orderinfo)
    nfe["dest_bairro"] = _get_additional_info(None, "NFE_BAIRRO", orderinfo)
    nfe["dest_municipio"] = _get_additional_info(None, "NFE_MUNICIPIO", orderinfo)
    nfe["dest_munibge"] = int(_get_additional_info(None, "NFE_MUNICIPIO_IBGE", orderinfo))
    nfe["dest_uf"] = _get_additional_info(None, "NFE_UF", orderinfo)
    created_at = str(order.get("createdAt"))
    nfe["nfe_aamm"] = int(created_at[2:4] + created_at[5:7])  # Ano e Mês de emissão da NF-e
    # Fixed data...
    nfe["nfe_model"] = 55  # Utilizar o código 55 para identificação da NF-e, emitida em substituição ao modelo 1 ou 1A.
    nfe["nfe_serie"] = 0  # Informar a série do documento fiscal (informar zero se inexistente).
    nfe["nfe_tipo_emissao"] = 1  # 1– Normal; 2– Contingência FS; 3– Contingência SCAN; 4– Contingência DPEC; 5– Contingência FS-DA
    # Data from the encrypted files...
    prn = fiscalprinter.fp(posid, mbcontext)
    user_cnpj, user_IE, user_IM, user_companyname, SW_MD5 = prn.readEncrypted("User_FederalRegister", "User_StateRegister", "User_MunicipalRegister", "User_CompanyName", "SW_MD5")
    if not user_IE.strip() or user_IE.upper().startswith("ISEN"):
        user_IE = "ISENTO"
    nfe["user_cnpj"] = int(user_cnpj.strip())
    nfe["user_IE"] = user_IE.replace("-", "").replace(".", "").strip()
    nfe["user_IM"] = user_IM.strip()
    nfe["user_companyname"] = user_companyname.strip()
    nfe["SW_MD5"] = SW_MD5
    # Data from configuration...
    nfe["user_nome_fantasia"] = get_storewide_config("Store.NomeFantasia")
    nfe["user_logradouro"] = get_storewide_config("Store.Logradouro")
    nfe["user_numeroendereco"] = get_storewide_config("Store.NumeroEndereco")
    nfe["user_bairro"] = get_storewide_config("Store.Bairro")
    nfe["user_municipio"] = get_storewide_config("Store.Municipio")
    nfe["user_CEP"] = int(get_storewide_config("Store.CEP").replace("-", ""))
    nfe["simples_nacional"] = int(get_storewide_config("Store.SimplesNacional", "0"))
    nfe["uf"] = get_storewide_config("Store.UnidadeFederacao").upper()
    nfe["uf_code"] = nfe_tables.UF_CODES[nfe["uf"]]
    nfe["user_munibge"] = int(get_storewide_config("Store.MunicipioIBGE"))
    nfe["PIS"] = D(get_storewide_config("Store.AliquotaPIS"))
    nfe["COFINS"] = D(get_storewide_config("Store.AliquotaCOFINS"))
    build_nfe_id(nfe)
    return nfe


def build_nfe_id(nfe):
    template = "%(uf_code)02d" + "%(nfe_aamm)04d" + "%(user_cnpj)014d" + "%(nfe_model)02d" +\
        "%(nfe_serie)03d" + "%(nfe_number)09d" + "%(nfe_tipo_emissao)1d" + "%(nfe_code)08d"
    nfe_id = template % nfe
    nfe_id += dv_nfe_id(nfe_id)  # Digito verificador
    if len(nfe_id) != 44:
        raise Exception("Erro gerando ID da NFe - ID gerado deveria ter 44 digitos: [%s]" % nfe_id)
    nfe["nfe_id"] = nfe_id
    return nfe_id


def add_nfe_details(out, nfe):
    w = out.write
    w('<ide>')
    w('<cUF>%d</cUF>' % nfe["uf_code"])
    w('<cNF>%d</cNF>' % nfe["nfe_code"])
    w('<natOp>Venda a vista</natOp>')
    w('<indPag>0</indPag>')  # 0 – pagamento à vista; 1 – pagamento à prazo; 2 - outros
    w('<mod>%d</mod>' % nfe["nfe_model"])
    w('<serie>%d</serie>' % nfe["nfe_serie"])
    w('<nNF>%d</nNF>' % nfe["nfe_number"])
    w('<dEmi>%s</dEmi>' % str(nfe["order"].get("createdAt")[:10]))
    w('<tpNF>1</tpNF>')  # 0-entrada / 1-saída
    w('<cMunFG>%d</cMunFG>' % nfe["user_munibge"])
    w('<tpImp>1</tpImp>')  # Formato de Impressão do DANFE - 1-Retrato/ 2-Paisagem
    w('<tpEmis>1</tpEmis>')  # 1 – Normal; 2 – Contingência FS; 3 – Contingência SCAN; 4 – Contingência DPEC; 5 – Contingência FS-DA
    w('<cDV>%s</cDV>' % nfe["nfe_id"][-1])
    w('<tpAmb>%d</tpAmb>' % (1 if nfe["nfe_ambiente"] == "producao" else 2))  # 1-Produção/ 2-Homologação
    w('<finNFe>1</finNFe>')  # 1- NF-e normal/ 2-NF-e complementar / 3 – NF-e de ajuste
    w('<procEmi>0</procEmi>')  # 0 - emissão de NF-e com aplicativo do contribuinte;
    w('<verProc>%s</verProc>' % saxutils.escape("MW:APP " + PAF_ECF.get_software_version()))
    w('</ide>')
    w('<emit>')
    w('<CNPJ>%014d</CNPJ>' % nfe["user_cnpj"])
    w('<xNome>%s</xNome>' % saxutils.escape(nfe["user_companyname"]))
    w('<xFant>%s</xFant>' % saxutils.escape(nfe["user_nome_fantasia"]))
    w('<enderEmit>')
    w('<xLgr>%s</xLgr>' % saxutils.escape(nfe["user_logradouro"]))
    w('<nro>%s</nro>' % saxutils.escape(nfe["user_numeroendereco"]))
    w('<xBairro>%s</xBairro>' % saxutils.escape(nfe["user_bairro"]))
    w('<cMun>%d</cMun>' % nfe["user_munibge"])
    w('<xMun>%s</xMun>' % saxutils.escape(nfe["user_municipio"]))
    w('<UF>%s</UF>' % saxutils.escape(nfe["uf"]))
    w('<CEP>%08d</CEP>' % nfe["user_CEP"])
    w('</enderEmit>')
    w('<IE>%s</IE>' % saxutils.escape(nfe["user_IE"]))
    w('<CRT>%d</CRT>' % (1 if nfe["simples_nacional"] else 3))  # 1 – Simples Nacional; 2 – Simples Nacional – excesso de sublimite de receita bruta; 3 – Regime Normal. (v2.0)
    w('</emit>')
    w('<dest>')
    if nfe.get("dest_CNPJ"):
        w('<CNPJ>%s</CNPJ>' % saxutils.escape(nfe["dest_CNPJ"]))
    else:
        w('<CPF>%s</CPF>' % saxutils.escape(nfe["dest_CPF"]))
    if nfe["nfe_ambiente"] == "homologacao":
        nome = "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
    else:
        nome = nfe["dest_nome"]
    w('<xNome>%s</xNome>' % saxutils.escape(nome))
    w('<enderDest>')
    w('<xLgr>%s</xLgr>' % saxutils.escape(nfe["dest_logradouro"]))
    w('<nro>%s</nro>' % saxutils.escape(nfe["dest_numeroendereco"]))
    if nfe.get("dest_complemento"):
        w('<xCpl>%s</xCpl>' % saxutils.escape(nfe["dest_complemento"]))
    w('<xBairro>%s</xBairro>' % saxutils.escape(nfe["dest_bairro"]))
    w('<cMun>%d</cMun>' % nfe["dest_munibge"])
    w('<xMun>%s</xMun>' % saxutils.escape(nfe["dest_municipio"]))
    w('<UF>%s</UF>' % saxutils.escape(nfe["dest_uf"]))
    w('</enderDest>')
    w('<IE></IE>')
    w('</dest>')


def add_nfe_products(out, nfe):
    w = out.write
    nitem = 0
    # List of product-codes on this order
    pcodes = ','.join(set([str(line.get("partCode")) for line in nfe["order"].findall("SaleLine") if int(line.get("level")) == 0]))
    # Retrieve information from those products from the database
    drv = persistence.Driver()
    conn = None
    try:
        conn = drv.open(mbcontext, dbname=str(nfe["order"].get("posId")))
        cursor = conn.select("SELECT * FROM fiscalinfo.FiscalProductDB WHERE ProductCode IN (%s)" % pcodes)
    finally:
        if conn:
            conn.close()
    proddb = {}
    for row in cursor:
        proddb[int(row.get_entry("ProductCode"))] = row
    # Consolidated amounts
    tot_vBC, tot_vICMS, tot_vICMSST, tot_vBCST, tot_vProd, tot_vPIS, tot_vCOFINS = ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO
    # Build the XML
    order = nfe["order"]
    for line in order.findall("SaleLine"):
        if int(line.get("level")) != 0:
            continue
        nitem += 1
        pcode = int(line.get("partCode"))
        prod = proddb[pcode]
        vProd = D(line.get("itemPrice"))
        tot_vProd += vProd
        w('<det nItem="%d">' % nitem)
        w('<prod>')
        w('<cProd>%d</cProd>' % pcode)
        w('<cEAN></cEAN>')
        w('<xProd>%s</xProd>' % saxutils.escape(line.get("productName").encode("UTF-8")))
        # TODO - NMC: http://www.mdic.gov.br/portalmdic/sitio/interna/interna.php?area=5&menu=3361
        w('<NCM>21</NCM>')
        # TODO - CFOP: é possível que este número precise ser ajustado dinamicamente
        # http://www.sefaz.pe.gov.br/flexpub/versao1/filesdirectory/sessions398.htm
        w('<CFOP>5101</CFOP>')
        w('<uCom>%s</uCom>' % saxutils.escape(line.get("measureUnit").encode("UTF-8")))
        w('<qCom>%s</qCom>' % saxutils.escape(line.get("qty").encode("UTF-8")))
        w('<vUnCom>%s</vUnCom>' % saxutils.escape(line.get("unitPrice").encode("UTF-8")))
        w('<vProd>%s</vProd>' % vProd)
        w('<cEANTrib></cEANTrib>')
        w('<uTrib>%s</uTrib>' % saxutils.escape(line.get("measureUnit").encode("UTF-8")))
        w('<qTrib>%s</qTrib>' % saxutils.escape(line.get("qty").encode("UTF-8")))
        w('<vUnTrib>%s</vUnTrib>' % saxutils.escape(line.get("unitPrice").encode("UTF-8")))
        w('<indTot>1</indTot>')  # 1 – o valor do item (vProd) compõe o valor total da NF-e (vProd)
        w('</prod>')
        w('<imposto>')
        w('<ICMS>')
        taxidx = prod.get_entry("TaxFiscalIndex")
        taxrate = D(prod.get_entry("TaxRate")) / D("100")
        if taxidx[0] == "I":
            CST = "40"  # Isenta
        elif taxidx[0] == "N":
            CST = "41"  # Não tributada
        elif taxidx[0] == "F":
            CST = "30"  # Isenta ou não tributada e com cobrança do ICMS por substituição tributária
        else:
            CST = "00"  # Tributada integralmente
        tag_icms = CST if CST != "41" else "40"
        w('<ICMS%s>' % tag_icms)
        w('<orig>0</orig>')  # Origem da mecadoria. 0: Nacional
        w('<CST>%s</CST>' % CST)
        if CST == "30":
            vBCST = D(line.get("itemPrice"))
            pICMSST = D(prod.get_entry("TaxRate"))
            vICMSST = (vBCST * taxrate)
            tot_vBCST += vBCST
            tot_vICMSST += vICMSST
            w('<modBCST>5</modBCST>')  # Modalidade de determinação da BC do ICMS ST. 5: Pauta (valor)
            w('<vBCST>%s</vBCST>' % vBCST)
            w('<pICMSST>%.2f</pICMSST>' % pICMSST)
            w('<vICMSST>%.2f</vICMSST>' % vICMSST)
        elif CST == "00":
            vBC = D(line.get("itemPrice"))
            pICMS = D(prod.get_entry("TaxRate"))
            vICMS = (vBC * taxrate)
            tot_vBC += vBC
            tot_vICMS += vICMS
            w('<modBC>3</modBC>')  # Modalidade de determinação da BC do ICMS. 3: valor da operação
            w('<vBC>%s</vBC>' % vBC)
            w('<pICMS>%.2f</pICMS>' % pICMS)
            w('<vICMS>%.2f</vICMS>' % vICMS)
            vBC += D(line.get("itemPrice"))
        w('</ICMS%s>' % tag_icms)
        w('</ICMS>')
        vPIS = (D(line.get("itemPrice")) * (nfe["PIS"] / D("100")))
        vCOFINS = (D(line.get("itemPrice")) * (nfe["COFINS"] / D("100")))
        tot_vPIS += vPIS
        tot_vCOFINS += vCOFINS
        w('<PIS>')
        w('<PISAliq>')
        w('<CST>01</CST>')  # 01 – Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo));
        w('<vBC>%s</vBC>' % str(line.get("itemPrice")))
        w('<pPIS>%.2f</pPIS>' % nfe["PIS"])
        w('<vPIS>%.2f</vPIS>' % vPIS)
        w('</PISAliq>')
        w('</PIS>')
        w('<COFINS>')
        w('<COFINSAliq>')
        w('<CST>01</CST>')  # 01 – Operação Tributável (base de cálculo = valor da operação alíquota normal (cumulativo/não cumulativo));
        w('<vBC>%s</vBC>' % str(line.get("itemPrice")))
        w('<pCOFINS>%.2f</pCOFINS>' % nfe["COFINS"])
        w('<vCOFINS>%.2f</vCOFINS>' % vCOFINS)
        w('</COFINSAliq>')
        w('</COFINS>')
        w('</imposto>')
        w('</det>')
    w('<total>')
    w('<ICMSTot>')
    w('<vBC>%.2f</vBC>' % tot_vBC)
    w('<vICMS>%.2f</vICMS>' % tot_vICMS)
    w('<vBCST>%.2f</vBCST>' % tot_vBCST)
    w('<vST>%.2f</vST>' % tot_vICMSST)
    w('<vProd>%.2f</vProd>' % tot_vProd)
    w('<vFrete>0</vFrete>')
    w('<vSeg>0</vSeg>')
    w('<vDesc>0</vDesc>')
    w('<vII>0</vII>')
    w('<vIPI>0</vIPI>')
    w('<vPIS>%.2f</vPIS>' % tot_vPIS)
    w('<vCOFINS>%.2f</vCOFINS>' % tot_vCOFINS)
    w('<vOutro>0</vOutro>')
    w('<vNF>%s</vNF>' % str(order.get("totalGross")))
    w('</ICMSTot>')
    w('</total>')
    w('<transp>')
    w('<modFrete>9</modFrete>')  # Sem frete
    w('</transp>')


def gera_xml_nfe(posid, order):
    if isinstance(order, str):
        order = etree.XML(order)
    nfe = get_nfe_info(posid, order)

    out = StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>')
    out.write('<NFe xmlns="http://www.portalfiscal.inf.br/nfe">')
    out.write('<infNFe Id="NFe%s" versao="2.00">' % nfe["nfe_id"])
    add_nfe_details(out, nfe)
    add_nfe_products(out, nfe)
    out.write('<infAdic>')
    out.write('<infAdFisco>%s</infAdFisco>' % nfe["SW_MD5"])
    out.write('</infAdic>')
    out.write('</infNFe>')
    add_signature_template(out, nfe)
    out.write('</NFe>')
    return out.getvalue(), nfe


def assina_nfe(unsigned, signed):
    exe = get_storewide_config("NFe.XmlsecExe")
    if not exe:
        if sys.platform == "win32":
            if os.path.exists("/xmlsec/xmlsec.exe"):
                exe = "/xmlsec/xmlsec.exe"
            else:
                exe = "xmlsec.exe"
        else:
            exe = "xmlsec"
    try:
        # Read the parameters
        pfx = get_storewide_config("NFe.CertificateFile", defval="nfe.pfx")
        pwd = get_storewide_config("NFe.CertificatePass", defval="none")
        pwd_args = ["--pwd", pwd] if (pwd.lower() != "none") else []  # Note that there is "no password" (none) and blank password ""
        # Call "xmlsec" to sign the NF-e
        exitcode = subprocess.call([exe, "--sign", "--output", signed, "--pkcs12", pfx] + pwd_args + ["--id-attr:Id", "infNFe", unsigned], shell=True)
        if (exitcode != 0):
            return None
        # Read the signed XML
        with open(signed, "rb") as f:
            data = f.read()
        # Remove line-feeds added by xmlsec
        data = data.replace("\r\n", "").replace("\n", "")
        # Remove the extra <X509Certificate>s added by xmlsec
        # we must keep only the LAST certificate - not the whole hierarchy
        while data.count("<X509Certificate>") > 1:
            start, end = data.index("<X509Certificate>"), data.index("</X509Certificate>")
            data = data[:start] + data[end + 18:]
        # Save the modified signed XML
        with open(signed, "wb") as f:
            f.write(data)
        # Validate the signature after we modify the XML
        exitcode = subprocess.call([exe, "--verify", "--pkcs12", pfx] + pwd_args + ["--id-attr:Id", "infNFe", signed], shell=True)
        if (exitcode != 0):
            sys_log_warning("The XML signature did not validate!")
            return None
        # Success!
        return data
    except:
        sys_log_exception("Erro assinando NF-e")
    return None


def gera_xml_envio(nfe_xml):
    now = datetime.datetime.now()
    id_lote = now.strftime("%Y%m%d%H%M%S") + now.strftime("%f")[0]
    if len(id_lote) > 15:
        raise NFException("Erro gerando número do lote de envio")
    out = StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>')
    out.write('<enviNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="2.00">')
    out.write('<idLote>%s</idLote>' % id_lote)
    out.write(remove_xml_prolog(nfe_xml))
    out.write('</enviNFe>')
    return out.getvalue(), id_lote


@action
def emitirNFe(posid, *args):
    model = get_model(posid)
    check_operator_logged(posid, model=model)
    check_current_order(posid, model=model, need_order=False)
    import nfe_tables
    # Determina o numero da ultima NF-e emitida
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext)
        cursor = conn.select("SELECT MAX(Number) FROM fiscalinfo.NFe")
        nfe_number = int(cursor.get_row(0).get_entry(0) or 0) + 1 if cursor.rows() else 1
        del cursor
    finally:
        if conn:
            conn.close()

    info = {}
    nfe_number = show_keyboard(posid, "Digite o número da NF-e:", defvalue=str(nfe_number), title="Emissão de NF-e", mask="INTEGER", numpad=True)
    if not nfe_number:
        return
    info["NFE_AMBIENTE"] = get_storewide_config("NFe.Ambiente", "homologacao")
    info["NFE_NUMBER"] = nfe_number
    info["NFE_CODE"] = str(random.randint(10000000, 99999999))
    # TODO - Get from configuration
    info["NFE_AMBIENTE"] = "homologacao"
    cpf_cnpj, nome = "", ""
    uf = get_storewide_config("Store.UnidadeFederacao", "").upper()
    while True:
        data = show_form(posid, (("CPF / CNPJ", cpf_cnpj), ("Nome", nome), ("UF", uf)), "Dados do destinatário da NF-e")
        if not data:
            return
        cpf_cnpj, nome, uf = data
        cpf_cnpj = cpf_cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
        nome = nome.strip()
        uf = uf.strip().upper()
        isvalid, idtype = validate_cpf_cnpj(cpf_cnpj)
        if not isvalid:
            idtype = idtype or "CPF / CNPJ"
            show_info_message(posid, "%s inválido. Por favor, digite novamente" % idtype, msgtype="warning")
            continue
        if not nome:
            show_info_message(posid, "Por favor, digite o nome do destinatário da NF-e!", msgtype="warning")
            continue
        if nfe_tables.UF_CODES.get(uf) is None:
            show_info_message(posid, "UF inválido. Por favor, digite novamente", msgtype="warning")
            continue
        info["NFE_%s" % idtype] = cpf_cnpj
        info["NFE_NOME"] = nome
        info["NFE_UF"] = uf
        break
    municipios = nfe_tables.MUNICIPIOS[nfe_tables.UF_CODES[uf]]
    def_ibge = get_storewide_config("Store.MunicipioIBGE")
    options = [mun[1] for mun in municipios]
    defvalue = ""
    if def_ibge:
        def_ibge = int(def_ibge)
        for i, mun in enumerate(municipios):
            if mun[0] == def_ibge:
                defvalue = str(i)
    index = show_listbox(posid, options, message="Selecione o município do destinatário", defvalue=defvalue)
    if index is None:
        return
    ibge, mun = municipios[index]
    info["NFE_MUNICIPIO"] = mun
    info["NFE_MUNICIPIO_IBGE"] = str(ibge)
    logradouro, num, compl, bairro = "", "", "", ""
    while True:
        data = show_form(posid, (("Logradouro", logradouro), ("Número", num), ("Complemento", compl), ("Bairro", bairro)), "Dados do destinatário da NF-e")
        if not data:
            return
        logradouro, num, compl, bairro = data
        logradouro = logradouro.strip()
        num = num.strip()
        compl = compl.strip()
        bairro = bairro.strip()
        if not logradouro:
            show_info_message(posid, "Por favor, digite o logradouro do destinatário da NF-e!", msgtype="warning")
            continue
        if not num:
            show_info_message(posid, "Por favor, digite o número do endereço do destinatário da NF-e!", msgtype="warning")
            continue
        if not bairro:
            show_info_message(posid, "Por favor, digite o bairro do destinatário da NF-e!", msgtype="warning")
            continue
        info["NFE_LOGRADOURO"] = logradouro
        info["NFE_NUMERO_END"] = num
        if compl:
            info["NFE_COMPLEMENTO"] = compl
        info["NFE_BAIRRO"] = bairro
        break
    try:
        posot = get_posot(model)
        posot.additionalInfo = '|'.join(["%s=%s" % (key, val) for key, val in info.iteritems()])
        posot.createOrder(posid, pricelist=get_pricelist(model), orderSubType="NONFISCAL")
        show_info_message(posid, "Entre com os items da NF-e!", msgtype="success", timeout=-1)
        change_screen(posid, "main")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


def conectar_soap(nfe, servico):
    import nfe_tables
    import simplessl
    url = nfe_tables.WEB_SERVICES[nfe["nfe_ambiente"]][nfe["uf"]][servico]
    if url.lower().endswith("?wsdl"):
        url = url[:-5]
    info = urlparse.urlsplit(url)
    host = info.hostname
    port = info.port or 443
    sock = simplessl.SimpleSSL(timeout=30.0, ignore_ssl_err=True)
    # This is our certificate AND private key - concatenated in PEM format
    cert_pem = nfe_tables.NFE_CERTIFICATE_PEM
    sock.setcertificate(cert_pem, cert_pem)
    sock.connect(host, port)
    sock._url = info
    return sock


def gera_xml_soap(nfe, xml_request, service_name):
    import nfe_tables
    xml_request = remove_xml_prolog(xml_request)
    out = StringIO()
    out.write('<?xml version="1.0" encoding="utf-8"?>')
    out.write('<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope" xmlns:tns="http://www.portalfiscal.inf.br/nfe/wsdl/%s">' % service_name)
    out.write('<soap12:Header>')
    out.write('<tns:nfeCabecMsg>')
    out.write('<tns:versaoDados>2.00</tns:versaoDados>')
    out.write('<tns:cUF>%d</tns:cUF>' % nfe_tables.UF_CODES[nfe["uf"]])
    out.write('</tns:nfeCabecMsg>')
    out.write('</soap12:Header>')
    out.write('<soap12:Body>')
    out.write('<tns:nfeDadosMsg>%s</tns:nfeDadosMsg>' % (xml_request))
    out.write('</soap12:Body>')
    out.write('</soap12:Envelope>')
    return out.getvalue()


def executar_soap_nfeRecepcaoLote2(sock, nfe, xml_request):
    soap_xml = gera_xml_soap(nfe, xml_request, "NfeRecepcao2")
    out = StringIO()
    out.write('POST %s HTTP/1.1\r\n' % sock._url.path)
    out.write('Accept-Encoding: identity\r\n')
    out.write('SOAPAction: "http://www.portalfiscal.inf.br/nfe/wsdl/NfeRecepcao2/nfeRecepcaoLote2"\r\n')
    out.write('Host: %s\r\n' % sock._url.hostname)
    out.write('User-Agent: Python-urllib/2.6\r\n')
    out.write('Connection: close\r\n')
    out.write('Content-Type: application/soap+xml; charset=utf-8; action="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRecepcao2/nfeRecepcaoLote2"\r\n')
    out.write('Content-Length: %d\r\n' % len(soap_xml))
    out.write('\r\n')
    out.write(soap_xml)
    sock.write(out.getvalue())
    resp = sock.read()
    index = resp.index('\r\n\r\n')
    return resp[index + 4:].strip()


def executar_soap_NfeRetRecepcao2(sock, nfe, xml_request):
    soap_xml = gera_xml_soap(nfe, xml_request, "NfeRetRecepcao2")
    out = StringIO()
    out.write('POST %s HTTP/1.1\r\n' % sock._url.path)
    out.write('Accept-Encoding: identity\r\n')
    out.write('SOAPAction: "http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetRecepcao2/nfeRetRecepcao2"\r\n')
    out.write('Host: %s\r\n' % sock._url.hostname)
    out.write('User-Agent: Python-urllib/2.6\r\n')
    out.write('Connection: close\r\n')
    out.write('Content-Type: application/soap+xml; charset=utf-8; action="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetRecepcao2/nfeRetRecepcao2"\r\n')
    out.write('Content-Length: %d\r\n' % len(soap_xml))
    out.write('\r\n')
    out.write(soap_xml)
    sock.write(out.getvalue())
    resp = sock.read()
    index = resp.index('\r\n\r\n')
    return resp[index + 4:].strip()


def envia_lote(posid, envio_xml, nfe):
    while True:
        dlgid = 0
        soap = None
        # Conecta
        try:
            dlgid = show_messagebox(posid, message="Conectando no servidor...", icon="info", buttons="", asynch=True)
            soap = conectar_soap(nfe, "NfeRecepcao")
        except:
            sys_log_exception("Error connecting to server")
            close_asynch_dialog(posid, dlgid)
            if not show_confirmation(posid, message="Não foi possível conectar no servidor.\\\\Deseja tentar novamente?"):
                return None
            continue
        close_asynch_dialog(posid, dlgid)
        # Envia
        try:
            dlgid = show_messagebox(posid, message="Enviando NF-e...", icon="info", buttons="", asynch=True)
            # recibo = soap.service.nfeRecepcaoLote2(envio_xml.decode("UTF-8"))
            try:
                recibo_xml = executar_soap_nfeRecepcaoLote2(soap, nfe, envio_xml)
            except:
                sys_log_debug("Error parsing response XML: %s" % (recibo_xml))
                raise
            recibo = etree.XML(recibo_xml).find("{http://www.w3.org/2003/05/soap-envelope}Body/{http://www.portalfiscal.inf.br/nfe/wsdl/NfeRecepcao2}nfeRecepcaoLote2Result/{http://www.portalfiscal.inf.br/nfe}retEnviNFe")
            sys_log_debug("Retorno NF-e: %s" % (recibo,))
            cStat = int(recibo.findtext("{http://www.portalfiscal.inf.br/nfe}cStat"))
            xMotivo = recibo.findtext("{http://www.portalfiscal.inf.br/nfe}xMotivo")
            if cStat != 103:
                close_asynch_dialog(posid, dlgid)
                msg = "O envio desta NF-e foi REJEITADO.\\\\Código de erro: %d\\Motivo: %s\\\\MW:APP %s" % (cStat, xMotivo.encode("UTF-8"), PAF_ECF.get_software_version())
                show_messagebox(posid, message=msg, icon="error")
                return None
            cod_recibo = str(recibo.find("{http://www.portalfiscal.inf.br/nfe}infRec").findtext("{http://www.portalfiscal.inf.br/nfe}nRec"))
            ret = recibo_xml, cod_recibo
        except:
            sys_log_exception("Error sending NF-e")
            close_asynch_dialog(posid, dlgid)
            if not show_confirmation(posid, message="Não foi possível enviar a NF-e.\\\\Deseja tentar novamente?"):
                return None
            continue
        # Sucesso!
        close_asynch_dialog(posid, dlgid)
        break
    return ret


def gera_xml_verificacao(cod_recibo, nfe):
    out = StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>')
    out.write('<consReciNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="2.00">')
    out.write('<tpAmb>%s</tpAmb>' % (1 if nfe["nfe_ambiente"] == "producao" else 2))
    out.write('<nRec>%s</nRec>' % cod_recibo)
    out.write('</consReciNFe>')
    return out.getvalue()


def verifica_lote(posid, consulta_xml, cod_recibo, nfe):
    msg_base = "NF-e enviada! Aguardando processamento pela SEFAZ\\\\"
    retorno = None
    while True:
        dlgid = 0
        soap = None
        # Conecta
        try:
            dlgid = show_messagebox(posid, message=msg_base + "Conectando no servidor...", icon="info", buttons="", asynch=True)
            soap = conectar_soap(nfe, "NfeRetRecepcao")
        except:
            sys_log_exception("Error connecting to server")
            close_asynch_dialog(posid, dlgid)
            if not show_confirmation(posid, message=msg_base + "Não foi possível conectar no servidor.\\\\Deseja tentar novamente?"):
                return retorno, False
            continue
        close_asynch_dialog(posid, dlgid)
        # Verifica o lote
        try:
            dlgid = show_messagebox(posid, message=msg_base + "Verificando processamento...", icon="info", buttons="", asynch=True)
            retorno = executar_soap_NfeRetRecepcao2(soap, nfe, consulta_xml)
            sys_log_debug("Retorno consulta lote NF-e: %s" % (retorno,))
            x = etree.XML(retorno)
            retConsReciNFe = x.find("{http://www.w3.org/2003/05/soap-envelope}Body/{http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetRecepcao2}nfeRetRecepcao2Result/{http://www.portalfiscal.inf.br/nfe}retConsReciNFe")
            cStat = int(retConsReciNFe.findtext("{http://www.portalfiscal.inf.br/nfe}cStat"))
            xMotivo = retConsReciNFe.findtext("{http://www.portalfiscal.inf.br/nfe}xMotivo").encode("UTF-8")
            close_asynch_dialog(posid, dlgid)
            if cStat == 105:  # Lote em processamento
                show_messagebox(posid, message=msg_base + "Lote ainda sendo processado pela SEFAZ\\\\Aguarde...", icon="info", buttons="", timeout=5000)
                continue
            if cStat != 104:
                show_messagebox(posid, message="A NF-e foi REJEITADA pela SEFAZ.\\Código de erro: %d\\Motivo: %s" % (cStat, xMotivo), icon="error")
                return retorno, False
            infProt = retConsReciNFe.find("{http://www.portalfiscal.inf.br/nfe}protNFe/{http://www.portalfiscal.inf.br/nfe}infProt")
            cStat = int(infProt.findtext("{http://www.portalfiscal.inf.br/nfe}cStat"))
            xMotivo = infProt.findtext("{http://www.portalfiscal.inf.br/nfe}xMotivo").encode("UTF-8")
            if cStat != 100:
                # 539 - Duplicidade com chave diferente
                # 204 - Duplicidade com mesma chave
                if cStat in (539, 204):
                    raise NFEDuplicadaxception(xMotivo)
                show_messagebox(posid, message="A NF-e foi REJEITADA pela SEFAZ.\\Código de erro: %d\\Motivo: %s" % (cStat, xMotivo), icon="error")
                return retorno, False
            # Succeso!!!
            message = "NF-e enviada com sucesso!"
            cMsg = retConsReciNFe.findtext("{http://www.portalfiscal.inf.br/nfe}cMsg") or u""
            xMsg = retConsReciNFe.findtext("{http://www.portalfiscal.inf.br/nfe}xMsg") or u""
            if cMsg or xMsg:
                message += "\\\\Mensagem da SEFAZ:\\%s (Cod: %s)" % (xMsg.encode("UTF-8"), cMsg.encode("UTF-8"))
            show_messagebox(posid, message=message, icon="success", asynch=True)
        except NFException:
            raise
        except:
            sys_log_exception("Error checking NF-e batch")
            close_asynch_dialog(posid, dlgid)
            if not show_confirmation(posid, message=msg_base + "Não foi possível verificar o processamento.\\\\Deseja tentar novamente?"):
                return retorno, False
            continue
        # Sucesso!
        close_asynch_dialog(posid, dlgid)
        return retorno, True


def doTotal(posid):
    model = get_model(posid)
    posot = get_posot(model)
    order = get_current_order(model)
    if D(order.get("totalGross")) <= ZERO:
        show_messagebox(posid, message="O valor da NF-e deve ser maior que zero!", icon="warning")
        return
    root = get_storewide_config("NFe.RootFolder", defval="../nfe")
    try:
        if not os.path.exists(root):
            os.makedirs(root)
        try:
            nfe_xml, nfe = gera_xml_nfe(posid, order)
        except:
            sys_log_exception("Erro gerando NF-e")
            show_messagebox(posid, message="Erro gerando XML da NF-e!\\Por favor, chame o suporte.", icon="error")
            return
        tmp_name = os.path.join(root, "tmp.xml")
        nfe_name = os.path.join(root, "%s-nfe.xml" % nfe["nfe_id"])
        with open(tmp_name, "wb") as f:
            f.write(nfe_xml)
        # Assina a NF-e
        nfe_xml = assina_nfe(tmp_name, nfe_name)
        if not nfe_xml:
            show_messagebox(posid, message="Erro assinando a NF-e!\\Por favor, verifique seu certificado digital.", icon="error")
            return
        # Gera XML de envio
        envio_xml, id_lote = gera_xml_envio(nfe_xml)
        envio_name = os.path.join(root, "%s-env-lot.xml" % id_lote)
        with open(envio_name, "wb") as f:
            f.write(envio_xml)
        # Envia o XML
        recibo = envia_lote(posid, envio_xml, nfe)
        if recibo is None:
            return
        recibo_xml, cod_recibo = recibo
        recibo_name = os.path.join(root, "%s-rec.xml" % id_lote)
        with open(recibo_name, "wb") as f:
            f.write(recibo_xml)
        # Aguarda o processamento do lote
        consulta_xml = gera_xml_verificacao(cod_recibo, nfe)
        consulta_name = os.path.join(root, "%s-ped-rec.xml" % cod_recibo)
        with open(consulta_name, "wb") as f:
            f.write(consulta_xml)
        res_lote, success = verifica_lote(posid, consulta_xml, cod_recibo, nfe)
        if res_lote is not None:
            prorec_name = os.path.join(root, "%s-pro-rec.xml" % cod_recibo)
            with open(prorec_name, "wb") as f:
                f.write(res_lote)
        if success:
            # Fecha a NF-e
            posot.doTotal(posid)
            info = order.findtext("AdditionalInfo").encode("UTF-8") + "|NFE_ID=%s" % nfe["nfe_id"]
            posot.updateOrderProperties(posid=posid, additionalinfo=info)
            posot.doTender(posid, TENDER_CASH, "")
            change_screen(posid, "main")
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    except NFEDuplicadaxception, ex:
        while True:
            message = "Já foi emitida uma NF-e com o número %d!\\\\Mensagem da SEFAZ: %s" % (nfe["nfe_number"], str(ex))
            if show_confirmation(posid, title="NF-e duplicada", icon="warning", message=message, buttons="Digitar outro número|Cancelar emissão", ):
                # Digitar outro número
                nfe_number = show_keyboard(posid, "Digite o novo número da NF-e:", title="Emissão de NF-e", mask="INTEGER", numpad=True)
                if not nfe_number:
                    continue
                nfe_number = int(nfe_number)
                info = order.findtext("AdditionalInfo").encode("UTF-8").replace("NFE_NUMBER=%d" % nfe["nfe_number"], "NFE_NUMBER=%d" % nfe_number)
                posot.updateOrderProperties(posid=posid, additionalinfo=info)
                if show_confirmation(posid, message="O número da NF-e foi alterado para %d.\\\\Deseja tentar emiti-la novamente?" % (nfe_number)):
                    return doTotal(posid)
                return
            else:
                # Cancelar emissão
                posot.voidOrder(posid)
                show_info_message(posid, "Emissão de NF-e cancelada!", msgtype="warning")
                change_screen(posid, "main")
                return
    except NFException, ex:
        show_messagebox(posid, message=str(ex), icon="error")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
