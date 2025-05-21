# -*- coding: utf-8 -*-
# Module name: pafecf_reports.py
# Module Description: Format Brazilian PAF-ECF reports
#
# Copyright (C) 2010-2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

# flake8: noqa
# Python standard modules
import os
import time
import decimal
import re
import calendar
import datetime
from xml.etree import cElementTree as etree
from collections import defaultdict
from decimal import Decimal as D

# Our modules
from systools import sys_log_warning, sys_log_exception
from reports import dbd, mbcontext, Report
from fiscalprinter import fpcmds, fp
import hashlib
import signxml
from signxml import XMLSigner
from pafecf import PAF_ECF
import base64

ZERO = D("0.00")


def readEncrypted(posid, *keys):
    f = fp(posid, mbcontext)
    return f.readEncrypted(*keys)


class Record(object):

    """Helper class used to generate PAF-ECF fiscal records
    Each record is composed by a list of "fields" and each field is described as a 3-elements tuple (name,size,format)
    The 'name' is used only for debugging and error messages
    The 'size' is used to indicate how many bytes the fields uses
    The 'format' indicates how the field should be formatted, and can be one of:
      - "X":  Format as a left-aligned, space-filled ASCII text
      - "XX": Format as a left-aligned, space-filled, upper-case ASCII text
      - "N":  Format as a right-aligned, zero-filled integer number
      - "NN": Format as a right-aligned, zero-filled decimal number with two decimal places and without the separator (1.23 -> "000123" and 1 -> "000100")
      - "N3": Format as a right-aligned, zero-filled decimal number with three decimal places and without the separator (1.23 -> "0001230" and 1 -> "0001000")
      - "D":  Format as a YYYYMMDD date
      - "H":  Format as a HHMMSS time
    """
    ascii = Report().ascii

    def __init__(self, name, field_descrs):
        self.name = name
        self.field_descrs = field_descrs
        self.size = len(name)
        self.spec = name
        for name, size, format in field_descrs:
            self.size += size
            if format in ("X", "XX"):
                self.spec += "%%-%d.%ds" % (size, size)
            elif format in ("N", "NN", "N3"):
                self.spec += "%%0%dd" % size
            elif format == "D":
                self.spec += "%8.8s"
            elif format == "H":
                self.spec += "%6.6s"
            else:
                raise Exception("Invalid field format specifier: %s for field: %s" % (format, name))

    def __call__(self, *args):
        if len(args) != len(self.field_descrs):
            raise Exception("Invalid number of fields for record '%s'. Received: %d Expected: %d" % (self.name, len(args), len(self.field_descrs)))
        fields = list(args)
        index = 0
        for field in fields:
            name, size, format = self.field_descrs[index]
            if format == "X":
                if not isinstance(field, (str, unicode)):
                    field = str(field)
                fields[index] = self.ascii(field)
            elif format == "XX":
                if not isinstance(field, (str, unicode)):
                    field = str(field)
                fields[index] = self.ascii(field).upper()
            elif format == "N":
                try:
                    field = int(float(field))
                except:
                    raise Exception("Invalid integer [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = field
                if len(str(field)) > size:
                    raise Exception("Field [%s] of record [%s] exceeds the maximum size: %d. Value: %d" % (name, self.name, size, field))
            elif format == "NN":
                try:
                    field = _decimal_to_fixed_int(field)
                except:
                    raise Exception("Invalid decimal [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = field
                if len(str(field)) > size:
                    raise Exception("Field [%s] of record [%s] exceeds the maximum size: %d. Value: %d" % (name, self.name, size, field))
            elif format == "N3":
                try:
                    field = _decimal_to_fixed_int3(field)
                except:
                    raise Exception("Invalid decimal [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = field
                if len(str(field)) > size:
                    raise Exception("Field [%s] of record [%s] exceeds the maximum size: %d. Value: %d" % (name, self.name, size, field))
            elif format == "D":
                try:
                    int(field)
                except:
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
                if len(str(field)) != 8:
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
            elif format == "H":
                try:
                    int(field)
                except:
                    raise Exception("Invalid time [%s] (HHMMSS) for field [%s] of recod [%s]" % (field, name, self.name))
                if len(str(field)) != 6:
                    raise Exception("Invalid time [%s] (HHMMSS) for field [%s] of recod [%s]" % (field, name, self.name))
            else:
                raise Exception("Invalid field format specifier: %s" % format)
            index += 1
        return self.spec % tuple(fields)


class SpedRecord(object):
    # http://www.fazenda.gov.br/confaz/confaz/atos/atos_cotepe/2008/AC009_08.htm

    """Helper class used to generate SPED fiscal records
    Each record is composed by a list of "fields" and each field is described as a 3-elements tuple (name,size,format)
    The 'name' is used only for debugging and error messages
    The 'size' is used to indicate how many bytes (maximum) the fields uses
    The 'format' indicates how the field should be formatted, and can be one of:
      - "X":   Format as a ASCII text
      - "I":   Format as non-filled integer number
      - "N":   Format as a right-aligned, zero-filled integer number
      - "NN":  Format as non-filled decimal number with two decimal places (using comma as decimal separator)
      - "NN?": Format as OPTINAL non-filled decimal number with two decimal places (using comma as decimal separator) - BLANK ALLOWED
      - "N3":  Format as non-filled decimal number with three decimal places (using comma as decimal separator)
      - "N*":  Format as a right-aligned, zero-filled integer number if there is data, otherwise empty
      - "D":   Format as a DDMMYYYY date (input as YYYYMMDD)
      - "D?":  Format as OPTIONAL a DDMMYYYY date (input as YYYYMMDD) - BLANK ALLOWED
      - "H":   Format as a HHMMSS time
    """
    ascii = Report().ascii

    def __init__(self, name, field_descrs):
        self.name = name
        self.field_descrs = field_descrs
        self.size = len(name)
        self.spec = "|" + name + "|"
        for name, size, format in field_descrs:
            self.size += size
            if format == "X":
                self.spec += "%s|"
            elif format == "I":
                self.spec += "%d|"
            elif format == "N":
                self.spec += "%%0%dd|" % size
            elif format == "N*":
                self.spec += "%s|"
            elif format == "NN":
                self.spec += "%s|"
            elif format == "NN?":
                self.spec += "%s|"
            elif format == "N3":
                self.spec += "%s|"
            elif format == "D":
                self.spec += "%8.8s|"
            elif format == "D?":
                self.spec += "%s|"
            elif format == "H":
                self.spec += "%6.6s|"
            else:
                raise Exception("Invalid field format specifier: %s for field: %s" % (format, name))

    def __call__(self, *args):
        if len(args) != len(self.field_descrs):
            raise Exception("Invalid number of fields for record '%s'. Received: %d Expected: %d" % (self.name, len(args), len(self.field_descrs)))
        fields = list(args)
        index = 0
        for field in fields:
            name, size, format = self.field_descrs[index]
            if format == "X":
                if not isinstance(field, (str, unicode)):
                    field = str(field)
                fields[index] = self.ascii(field)
            elif format == "I":
                try:
                    field = int(field)
                except:
                    raise Exception("Invalid integer [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = field
            elif format == "N":
                try:
                    field = int(field)
                except:
                    raise Exception("Invalid integer [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = field
                if len(str(field)) > size:
                    raise Exception("Field [%s] of record [%s] exceeds the maximum size: %d. Value: %d" % (name, self.name, size, field))
            elif format == "N*":
                if field != "":
                    try:
                        field = int(field)
                    except:
                        raise Exception("Invalid integer [%s] for field [%s] of record [%s]" % (field, name, self.name))
                    fields[index] = "%0*d" % (size, field)
                    if len(str(field)) > size:
                        raise Exception("Field [%s] of record [%s] exceeds the maximum size: %d. Value: %d" % (name, self.name, size, field))
            elif format == "NN":
                try:
                    field = D(field)
                except:
                    raise Exception("Invalid decimal [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = ("%.2f" % field).replace(".", ",")
            elif format == "NN?":
                try:
                    field = D(field) if field else ""
                except:
                    raise Exception("Invalid decimal [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = ("%.2f" % field).replace(".", ",") if field else ""
            elif format == "N3":
                try:
                    field = D(field)
                except:
                    raise Exception("Invalid decimal [%s] for field [%s] of record [%s]" % (field, name, self.name))
                fields[index] = ("%.3f" % field).replace(".", ",")
            elif format == "D":
                try:
                    int(field)
                except:
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
                field = str(field)
                if len(field) != 8:
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
                # Convert to DDMMYYYY
                fields[index] = field[6:8] + field[4:6] + field[:4]
            elif format == "D?":
                try:
                    int(field or 1)
                except:
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
                field = str(field or "")
                if len(field) not in (8, 0):
                    raise Exception("Invalid date [%s] (YYYYMMDD) for field [%s] of record [%s]" % (field, name, self.name))
                # Convert to DDMMYYYY
                if field:
                    fields[index] = field[6:8] + field[4:6] + field[:4]
            elif format == "H":
                try:
                    int(field)
                except:
                    raise Exception("Invalid time [%s] (HHMMSS) for field [%s] of recod [%s]" % (field, name, self.name))
                if len(field) != 6:
                    raise Exception("Invalid time [%s] (HHMMSS) for field [%s] of recod [%s]" % (field, name, self.name))
            else:
                raise Exception("Invalid field format specifier: %s" % format)
            index += 1
        return self.spec % tuple(fields)


class records:

    """Namespace for all pre-defined fiscal records"""
    # [ATO COTEPE/ICMS N° 6, DE 14 DE ABRIL DE 2008] - http://www.fazenda.gov.br/confaz/confaz/atos/atos_cotepe/2008/ac006_08.htm
    E1 = Record("E1", (
        ("CNPJ",           14,     "N"),
        ("I.E.",           14,     "X"),
        ("I.M.",           14,     "X"),
        ("Razao social",   50,     "X"),
        ("Serial ECF",     20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Tipo de ECF",     7,     "X"),
        ("Marca do ECF",   20,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("Data estoque",    8,     "D"),
        ("Hora estoque",    6,     "H"),
    ))
    # NOQA
    E2 = Record("E2", (
        ("CNPJ",           14,     "N"),
        ("Codigo.",        14,     "X"),
        ("Descr",          50,     "X"),
        ("Unidade",        6,      "X"),
        ("Sinal Qtd",      1,      "X"),
        ("Qtd",            9,      "N3"),
    ))
    E3 = Record("E3", (
        ("No. Fabricacao", 20, "X"),
        ("MF Adicional", 1, "X"),
        ("Tipo de ECF", 7, "X"),
        ("Marca do ECF", 20, "X"),
        ("Modelo do ECF", 20, "X"),
        ("Data estoque", 8, "D"),
        ("Hora estoque", 6, "H")
    ))
    E9 = Record("E9", (
        ("CNPJ",           14,     "N"),
        ("I.E.",           14,     "X"),
        ("Total",           6,     "N"),
    ))
    P1 = Record("P1", (
        ("CNPJ",           14,     "N"),
        ("I.E.",           14,     "X"),
        ("I.M.",           14,     "X"),
        ("Razao social",   50,     "X"),
    ))
    P2 = Record("P2", (
        ("CNPJ",           14,     "N"),
        ("Codigo.",        14,     "X"),
        ("Descr",          50,     "X"),
        ("Unidade",        6,      "X"),
        ("IAT",            1,      "X"),
        ("IPPT",           1,      "X"),
        ("Sit. Tribut.",   1,      "X"),
        ("Aliquota",       4,      "NN"),
        ("Val Unitario",   12,     "NN"),
    ))
    P9 = Record("P9", (
        ("CNPJ",           14,     "N"),
        ("I.E.",           14,     "X"),
        ("Total",           6,     "N"),
    ))
    R01 = Record("R01", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Tipo de ECF",     7,     "X"),
        ("Marca do ECF",   20,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("Versao do SB",   10,     "X"),
        ("Data SB",         8,     "D"),
        ("Horario SB",      6,     "H"),
        ("No. Seq.",        3,     "N"),
        ("CNPJ usr",       14,     "N"),
        ("I.E. usr",       14,     "X"),
        ("CNPJ",           14,     "N"),
        ("I.E.",           14,     "X"),
        ("I.M.",           14,     "X"),
        ("Denominacao",    40,     "X"),
        ("Nome PAF",       40,     "X"),
        ("Versao PAF",     10,     "X"),
        ("MD5",            32,     "X"),
        ("Data inicial",    8,     "D"),
        ("Data final",      8,     "D"),
        ("Versao ER",       4,     "X"),
    ))
    R02 = Record("R02", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("CRZ",             6,     "N"),
        ("COO",             9,     "N"),
        ("CRO",             6,     "N"),
        ("Data movimento",  8,     "D"),
        ("Data emissao",    8,     "D"),
        ("Hora emissao",    6,     "H"),
        ("Venda bruta",    14,     "NN"),
        ("Desc ISSQN",      1,     "X"),
    ))
    R03 = Record("R03", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("CRZ",             6,     "N"),
        ("Totaliz parcial", 7,     "X"),
        ("Val acumulado",   13,    "N"),  # Please note that this is declared as "N" and not "NN" - this field is already stored as an integer
    ))
    R04 = Record("R04", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("CCF,CVC ou CBP",  9,     "N"),
        ("COO",             9,     "N"),
        ("Data emissao",    8,     "D"),
        ("Subtotal",       14,     "NN"),
        ("Desconto",       13,     "NN"),
        ("Tipo Desconto",   1,     "X"),
        ("Acrescimo",      13,     "NN"),
        ("Tipo Acrescimo",  1,     "X"),
        ("Valor total",    14,     "NN"),
        ("Indicador Canc",  1,     "X"),
        ("Canc Acrescimo", 13,     "NN"),
        ("Ordem Desc/Acr",  1,     "X"),
        ("Nome Cliente",   40,     "X"),
        ("CPF/CNPJ",       14,     "N"),
    ))
    R05 = Record("R05", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("COO",             9,     "N"),
        ("CCF,CVC ou CBP",  9,     "N"),
        ("Numero do item",  3,     "N"),
        ("Codigo",         14,     "X"),
        ("Descricao",     100,     "X"),
        ("Quantidade",      7,     "N3"),
        ("Unidade",         3,     "X"),
        ("Valor unitario",  8,     "N3"),
        ("Desconto",        8,     "NN"),
        ("Acrescimo",       8,     "NN"),
        ("Valor total",    14,     "NN"),
        ("Totaliz parcial", 7,     "X"),
        ("Indicador Canc",  1,     "X"),
        ("Qtd Cancelada",   7,     "N3"),
        ("Val Cancelado",  13,     "NN"),
        ("Canc Acrescimo", 13,     "NN"),
        ("IAT",             1,     "X"),
        ("IPPT",            1,     "X"),
        ("Casas dec qtd",   1,     "N"),
        ("Casas dec val",   1,     "N"),
    ))
    R06 = Record("R06", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("COO",             9,     "N"),
        ("GNF",             6,     "N"),
        ("GRG",             6,     "N"),
        ("CDC",             4,     "N"),
        ("Denominacao",     2,     "X"),
        ("Data final",      8,     "D"),
        ("Hora final",      6,     "H"),
    ))
    R07 = Record("R07", (
        ("No. Fabricacao", 20,     "X"),
        ("MF Adicional",    1,     "X"),
        ("Modelo do ECF",  20,     "X"),
        ("No. Usuario",     2,     "N"),
        ("COO",             9,     "N"),
        ("CCF",             9,     "N"),
        ("GNF",             6,     "N"),
        ("Meio de pagto",  15,     "X"),
        ("Valor pago",     13,     "NN"),
        ("Indic estorno",   1,     "X"),
        ("Valor estorno",  13,     "NN"),
    ))
    # ANEXO X - REQUISITO IX
    N1 = Record("N1", (
        ("CNPJ",           14,     "N"),
        ("Insc. Estadual", 14,     "XX"),
        ("Insc. Municip.", 14,     "XX"),
        ("Razao Social",   50,     "XX"),
    ))
    N2 = Record("N2", (
        ("Nr. do Laudo",   10,     "XX"),
        ("Nome PAF-ECF",   50,     "XX"),
        ("Versao PAF-ECF", 10,     "XX"),
    ))
    N3 = Record("N3", (
        ("Nome arquivo",   50,     "XX"),
        ("Codigo MD5",     32,     "XX"),
    ))
    N9 = Record("N9", (
        ("CNPJ",           14,     "N"),
        ("Insc. Estadual", 14,     "XX"),
        ("Total N3",        6,     "N"),
    ))
    # [Manual de Orientação do Convênio 57/95] - http://www.fazenda.gov.br/confaz/Confaz/Convenios/ICMS/1995/CV057_95_Manual_de_Orientacao.htm
    T10 = Record("10", (
        ("CGC/MF (CNPJ)",  14,     "N"),   # CGC/MF do estabelecimento informante
        ("I.E.",           14,     "X"),   # Inscrição estadual do estabelecimento informante
        ("Razao social",   35,     "X"),   # Nome comercial (razão social / denominação) do contribuinte
        ("Municipio",      30,     "X"),   # Município onde está domiciliado o estabelecimento informante
        ("Un. da federac.", 2,     "X"),   # Unidade da Federação referente ao Município
        ("Fax",            10,     "N"),   # Número do fax do estabelecimento informante
        ("Data inicial",    8,     "D"),   # A data do início do período referente às informações prestadas
        ("Data final",      8,     "D"),   # A data do fim do período referente às informações prestadas
        ("Cod. Convenio",   1,     "X"),   # Código da identificação da estrutura do arquivo magnético entregue, conforme tabela abaixo
        ("Cod. Natureza",   1,     "X"),   # Código da identificação da natureza das operações informadas, conforme tabela abaixo
        ("Cod. Finalidade", 1,     "X"),   # Código do finalidade utilizado no arquivo magnético, conforme tabela abaixo
    ))
    T11 = Record("11", (
        ("Logradouro",     34,     "X"),
        ("Numero",          5,     "N"),
        ("Complemento",    22,     "X"),
        ("Bairro",         15,     "X"),
        ("CEP",             8,     "N"),
        ("Contato",        28,     "X"),
        ("Telefone",       12,     "N"),
    ))
    T60M = Record("60M", (
        ("Data",            8,     "D"),   # Data de emissão dos documentos fiscais
        ("Serial ECF",     20,     "X"),   # Número de série de fabricação do equipamento
        ("POS id",          3,     "N"),   # Número atribuído pelo estabelecimento ao equipamento
        ("Modelo Doc [2D]", 2,     "X"),   # Código do modelo do documento fiscal - "2D", quando se tratar de Cupom Fiscal (emitido por ECF)
        ("COO Inicio",      6,     "N"),   # Número do primeiro documento fiscal emitido no dia (Número do Contador de Ordem de Operação - COO)
        ("COO Fim",         6,     "N"),   # Número do último documento fiscal emitido no dia (Número do Contador de Ordem de Operação - COO)
        ("CRZ",             6,     "N"),   # Número do Contador de Redução Z (CRZ)
        ("CRO",             3,     "N"),   # Valor acumulado no Contador de Reinício de Operação (CRO)
        ("Venda bruta",    16,     "NN"),  # Valor acumulado no totalizador de Venda Bruta
        ("GT",             16,     "NN"),  # Valor acumulado no Totalizador Geral
        ("Brancos",        37,     "X"),   # -- espaços em branco
    ))
    T60A = Record("60A", (
        ("Data",            8,     "D"),   # Data de emissão dos documentos fiscais
        ("Serial ECF",     20,     "X"),   # Número de série de fabricação do equipamento
        ("Id. Aliquota",    4,     "X"),   # Identificador da Situação Tributária / Alíquota do ICMS
        ("Valor acum.",    12,     "N"),   # Valor acumulado no final do dia no totalizador parcial da situação tributária / alíquota indicada no campo 05 (com 2 decimais)
        ("Brancos",        79,     "X"),   # -- espaços em branco
    ))
    T61 = Record("61", (
        ("Brancos",         14,    "X"),   # -- espaços em branco
        ("Brancos",         14,    "X"),   # -- espaços em branco
        ("Data",            8,     "D"),   # Data de emissão dos documentos fiscais
        ("Modelo [02]",     2,     "N"),   # Modelo do(s) documento(s) fiscal(is)
        ("Série",           3,     "X"),   # Série do(s) documento(s) fiscal(is)
        ("Subsérie",        2,     "X"),   # Série do(s) documento(s) fiscal(is)
        ("Num Inicial",     6,     "N"),   # Número do primeiro documento fiscal emitido no dia do mesmo modelo, série e subsérie
        ("Num Final",       6,     "N"),   # Número do último documento fiscal emitido no dia do mesmo modelo, série e subsérie
        ("Valor total",    13,     "NN"),  # Valor total do(s) documento(s) fiscal(is)/Movimento diário (com 2 decimais)
        ("Base calculo",   13,     "NN"),  # Base de cálculo do(s) documento(s) fiscal(is)/Total diário (com 2 decimais)
        ("Valor ICMS",     12,     "NN"),  # Valor do Montante do Imposto/Total diário (com 2 decimais)
        ("Isentos",        13,     "NN"),  # Valor amparado por isenção ou não-incidência/Total diário (com 2 decimais)
        ("Outros",         13,     "NN"),  # Valor que não confira débito ou crédito de ICMS/Total diário (com 2 decimais)
        ("Alíquota",        4,     "NN"),  # Alíquota do ICMS (com 2 decimais)
        ("Brancos",         1,     "X"),   # -- espaços em branco
    ))
    T60D = Record("60D", (
        ("Data",            8,     "D"),   # 03 -Data de emissão dos documentos fiscais
        ("Serial ECF",     20,     "X"),   # 04 -Número de série de fabricação do equipamento
        ("Cod. Produto",   14,     "X"),   # 05 -Código do produto ou serviço utilizado pelo contribuinte
        ("Quantidade",     13,     "N"),   # 06 -Quantidade comercializada da mercadoria/produto
        ("Valor acum.",    16,     "NN"),  # 07 -Valor acumulado liquido da mercadoria/produto
        ("Base Calc.",     16,     "NN"),  # 08 -Base de Cálculo do ICMS de substituição tributária (com 2 decimais)
        ("Id. Aliquota",    4,     "X"),   # 09 -Identificador da Situação Tributária / Alíquota do ICMS
        ("Valor ICMS",     13,     "NN"),  # 10 -Valor do Montante do Imposto/Total diário (com 2 decimais)
        ("Brancos",        19,     "X"),   # 11 -- espaços em branco
    ))
    T75 = Record("75", (
        ("Data inicial",    8,     "D"),   # Data inicial do período de validade das informações
        ("Data final",      8,     "D"),   # Data final do período de validade das informações
        ("Cod. Produto",   14,     "X"),   # Código do produto ou serviço utilizado pelo contribuinte
        ("Cod.  NCM",       8,     "X"),   # Codificação da Nomenclatura Comum do Mercosul
        ("Descricao",      53,     "X"),   # Descrição do produto ou serviço
        ("Unidade",         6,     "X"),   # Unidade de medida de comercialização do produto ( un, kg, mt, m3, sc, frd, kWh, etc..)
        ("Aliquota IPI",    5,     "NN"),  # Alíquota do IPI do produto (com 2 decimais)
        ("Aliquota ICMS",   4,     "NN"),  # Alíquota do ICMS aplicável a mercadoria ou serviço nas operações ou prestações internas ou naquelas que se tiverem iniciado no exterior (com 2 decimais)
        ("Red. Base Calc.", 5,     "NN"),  # % de Redução na base de cálculo do ICMS, nas operações internas (com 2 decimais)
        ("Base Calc.",     13,     "NN"),  # Base de Cálculo do ICMS de substituição tributária (com 2 decimais)
    ))
    T90 = Record("90", (
        ("CGC/MF (CNPJ)",  14,     "N"),   # CGC/MF do estabelecimento informante
        ("I.E.",           14,     "X"),   # Inscrição estadual do estabelecimento informante
        ("Tipo [60]",       2,     "X"),   # Tipo de registro que será totalizado pelo próximo campo
        ("Total",           8,     "N"),   # Total de registros do tipo informado no campo anterior
        ("Tipo [61]",       2,     "X"),   # Tipo de registro que será totalizado pelo próximo campo
        ("Total",           8,     "N"),   # Total de registros do tipo informado no campo anterior
        ("Tipo [75]",       2,     "X"),   # Tipo de registro que será totalizado pelo próximo campo
        ("Total",           8,     "N"),   # Total de registros do tipo informado no campo anterior
        ("Tipo [99]",       2,     "X"),   # Tipo (TOTAL GERAL)
        ("Total",           8,     "N"),   # Total de registros (TOTAL GERAL)
        ("Brancos",        55,     "X"),   # -- espaços em branco (pois só totalizamos o registro tipo 60, 61 e 75)
        ("Numero T90 [1]",  1,     "N"),   # Número de registros tipo 90
    ))
    # SPED
    R0000 = SpedRecord("0000", (   # Abertura do arquivo digital e identificação da entidade
        ("COD_VER",         3,    "N*"),   # 02 -Codigo da versão do leiaute conforme a tabela indicada no Ato Cotepe
        ("COD_FIN",         1,     "N"),   # 03 -Codigo da finalidade do arquivo 0 - Remessa do arquivo Original; 1 - Remessa do arquivo substituto
        ("DT_INI",          8,     "D"),   # 04 -Data inicial das informações contidas no arquivo (ddmmaaaa)
        ("DT_FIM",          8,     "D"),   # 05 -Data final das informações contidas no arquivo (ddmmaaaa)
        ("NOME",          100,     "X"),   # 06 -Nome empresarial da entidade
        ("CNPJ",           14,    "N*"),   # 07 -Numero de inscrição da entidade no CNPJ
        ("CPF",            11,     "X"),   # 08 -Numero de inscrição da entidade no CPF
        ("UF",              2,     "X"),   # 09 -Sigla da unidade da federação da entidade
        ("IE",             14,     "X"),   # 10 -Inscrição estadual da entidade
        ("COD_MUN",         7,    "N*"),   # 11 -Codigo do município do domicĩlio fiscal da entidade, conforme a tabela IBGE
        ("IM",            255,     "X"),   # 12 -Inscrição Municiap da entidade
        ("SUFRAMA",         9,     "X"),   # 13 -Inscrição da entidade na Suframa
        ("IND_PERFIL",      1,     "X"),   # 14 -Perfil da apresentação do arquivo fiscal; A:Perfil A; B:Pefil B; C:Perfil C
        ("IND_ATIV",        1,     "N"),   # 15 -Indicador de tipo de atividade: 0:Industrial ou equip. a industrial; 1:Outros.
    ))
    R0001 = SpedRecord("0001", (  # Abertura do bloco O
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    R0005 = SpedRecord("0005", (  # Dados complementares da entidade
        ("FANTASIA",       60,      "X"),  # 02 -Nome de fantasia associado ao nome empresarial
        ("CEP",             8,     "N*"),  # 03 -Código de endereçamento postal
        ("END",            60,      "X"),  # 04 -Logradouro e endereo do imóvel
        ("NUM",           255,      "I"),  # 05 -Número do Imóvel
        ("COMPL",          60,      "X"),  # 06 -Dados complementares do endereço
        ("BAIRRO",         60,      "X"),  # 07 -Bairro em que o imóvel está situado
        ("FONE",           10,      "X"),  # 08 -Número do telefone
        ("FAX",            10,      "X"),  # 09 -Número do fax
        ("EMAIL",         255,      "X"),  # 10 -Endereço eletrônico
    ))
    R0190 = SpedRecord("0190", (  # Unidades de Medida
        ("UNID",            6,      "X"),  # 02 -Código da unidade de medida
        ("SUB_SER",       255,      "X"),  # 03 -Descrição da unidade de medida
    ))
    R0200 = SpedRecord("0200", (  # Tabela de identificação do item (Produto e serviços)
        ("COD_ITEM",       60,      "X"),  # 02 -Código do item
        ("DESCR_ITEM",    255,      "X"),  # 03 -Descrição do item
        ("COD_BARRA",     255,      "X"),  # 04 -Representação alfanumérico do código de barra do produto, se houver
        ("COD_ANT_ITEM",   60,      "X"),  # 05 -Código anterior do item com relação à última informação apresentada
        ("UNID_INV",        6,      "X"),  # 06 -Unidade de medida utilizada na qualificação de estoques
        ("TIPO_ITEM",       2,      "N"),  # 07 -Tipo do item - Atividades Industriais, Comerciais e Serviços [tabela abaixo]
        ("COD_NCM",         8,      "X"),  # 08 -Código da Nomeclatura Comum do Mercosul
        ("EX_IPI",          3,      "X"),  # 09 -Código EX, conforme a TIPI
        ("COD_GEN",         2,     "N*"),  # 10 -Código do gênero do item, conforme a Tabela 4.2.1
        ("COD_LST",         4,      "N"),  # 11 -Código do serviço conforme lista do anexo I da Lei Complementar Federan n.116/03
        ("ALIQ_ICMS",       6,      "X"),  # 12 -Alíquota de ICMS aplicável ao item nas operações internas (2 casas decimais;incluir a virgula)
    ))
    # Tabela para registro 08 - Tipo do item
    # 00-Mercadoria para Revenda;   01-Matéria prima;    02-Embalagem;                03-Produto em Processo;
    # 04-Produto acabado;           05-Subproduto;       06-Produto intermediário;    07-Material de Uso e Consumo;
    # 08-Ativo imobilizado;         09-Serviços;         10-Outros insumos;           99-Outras;
    R0990 = SpedRecord("0990", (  # Encerramento do bloco O
        ("QTD_LIN_0",      255,     "I"),  # 02 -Quantidade total de linhas do Bloco 0
    ))
    R1001 = SpedRecord("1001", (  # Abertura do bloco 1
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    R1990 = SpedRecord("1990", (  # Encerramento do bloco 1
        ("QTD_LIN_1",      255,      "I"),  # 02 -Quantidade total de linhas do Bloco E
    ))
    RC001 = SpedRecord("C001", (  # Abertura do bloco C
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RC350 = SpedRecord("C350", (  # Nota Manual
        ("SER",             3,      "X"),  # 02 -Série do documento fiscal
        ("SUB_SER",         3,      "X"),  # 03 -Subsérie do documento fiscal
        ("NUM_DOC",       255,      "I"),  # 04 -Número do documento fiscal
        ("DT_DOC",          8,      "D"),  # 05 -Data da emissão do documento fiscal
        ("CNPJ_CPF",       14,      "X"),  # 06 -CPF ou CNPJ do destinatário
        ("VL_MERC",       255,     "NN"),  # 07 -Valor das mercadorias constantes no documento fiscal
        ("VL_DOC",        255,     "NN"),  # 08 -Valor total do documento fiscal
        ("VL_DESC",       255,     "NN"),  # 09 -Valor total do desconto
        ("VL_PIS",        255,     "NN"),  # 10 -Valor total do PIS
        ("VL_CONFINS",    255,     "NN"),  # 11 -Valor total da COFINS
        ("COD_CTA",       255,      "X"),  # 12 -Código da conta analítica contábil debitada/creditada
    ))
    RC370 = SpedRecord("C370", (  # Itens do documento (Nota fiscal manual)
        ("NUM_ITEM",        3,      "I"),  # 02 -Número sequencial do item no documento fiscal
        ("COD_ITEM",       60,      "X"),  # 03 -Código do item(campo 02 do registro 0200)
        ("QTD",           255,      "X"),  # 04 -Quantidade do item (3 casas decimais)
        ("UNID",            6,      "X"),  # 05 -Unidade do item (campo 02 do registro 0190
        ("VL_ITEM",       255,     "NN"),  # 06 -Valor total do item
        ("VL_DESC",       255,     "NN"),  # 07 -Valor total do desconto no item
    ))
    RC390 = SpedRecord("C390", (  # Itens do documento (Nota fiscal manual)
        ("CST_ICMS",        3,     "N*"),  # 02 -Código da Situação Tributária, conforme a Tabela indicada no item 4.3.1
        ("CFOP",            4,     "N*"),  # 03 -Código Fiscal de Operação e Prestação
        ("ALIQ_ICMS",       6,     "NN"),  # 04 -Alíquota do ICMS
        ("VL_OPR",        255,     "NN"),  # 05 -Valor acumulado da base de cálculo do ICMS, referente à combinação de CST_ICMS, CFOP, e alíquota do ICMS
        ("VL_BC_ICMS",    255,     "NN"),  # 06 -Valor acumulado da base de cálculo do ICMS, referente à combinação de CST_ICMS, CFOP, e alíquota do ICMS.
        ("VL_ICMS",       255,     "NN"),  # 07 -Valor acumulado do ICMS, referente à combinação de CST_ICMS, CFOP e alíquota do ICMS.
        ("VL_RED_BC",     255,     "NN"),  # 08 -Valor não tributado em função da redução da base de cálculo do ICMS, referente à combinação de CST_ICMS, CFOP, e alíquota do ICMS.
        ("COD_OBS",         6,      "X"),  # 09 -Código da observação do lançamento fiscal (campo 02 do Registro 0460)
    ))
    RC400 = SpedRecord("C400", (  # EQUIPAMENTO ECF
        ("COD_MOD",         2,      "X"),  # 02 - Código do modelo do documento fiscal, conforme a Tabela 4.1.1
        ("ECF_MOD",        20,      "X"),  # 03 - Modelo do equipamento
        ("ECF_FAB",        20,      "X"),  # 04 - Número de série de fabricação do ECF
        ("ECF_CX",          3,      "N"),  # 05 -Código do modelo do documento fiscal, conforme a Tabela 4.1.1
    ))
    RC405 = SpedRecord("C405", (  # REDUÇÃO Z
        ("DT_DOC",          8,      "D"),  # 02 - Data do movimento a que se refere a Redução Z
        ("CRO",             3,      "N"),  # 03 - Posição do Contador de Reinício de Operação
        ("CRZ",             6,      "N"),  # 04 - Posição do Contador de Redução Z
        ("NUM_COO_FIN",     6,      "N"),  # 05 - Número do Contador de Ordem de Operação do último documento emitido no dia. (Número do COO na Redução Z)
        ("GT_FIN",        255,     "NN"),  # 06 - Valor do Grande Total final
        ("VL_BRT",        255,     "NN"),  # 07 - Valor da venda bruta
    ))
    RC420 = SpedRecord("C420", (  # REGISTRO DOS TOTALIZADORES PARCIAIS DA REDUÇÃO Z
        ("COD_TOT_PAR",     7,      "X"),  # 02 - Código do totalizador, conforme Tabela 4.4.6
        ("VLR_ACUM_TOT",  255,     "NN"),  # 03 - Valor acumulado no totalizador, relativo à respectiva Redução Z
        ("NR_TOT",          2,      "X"),  # 04 - Número do totalizador quando ocorrer mais de uma situação com a mesma carga tributária efetiva
        ("DESCR_NR_TOT",  255,      "X"),  # 05 - Descrição da situação tributária relativa ao totalizador parcial, quando houver mais de um com a mesma carga tributária efetiva
    ))
    RC425 = SpedRecord("C425", (  # RESUMO DE ITENS DO MOVIMENTO DIÁRIO
        ("COD_ITEM",       60,      "X"),  # 02 - Código do item (campo 02 do Registro 0200)
        ("QTD",           255,     "N3"),  # 03 - Quantidade acumulada do item
        ("UNID",            6,      "X"),  # 04 - Unidade do item (Campo 02 do registro 0190)
        ("VL_ITEM",       255,     "NN"),  # 05 - Valor acumulado do item
        ("VL_PIS",        255,     "NN"),  # 06 - Valor do PIS
        ("VL_COFINS",     255,     "NN"),  # 07 - Valor da COFINS
    ))
    RC460 = SpedRecord("C460", (  # DOCUMENTO FISCAL EMITIDO POR ECF
        ("COD_MOD",         2,      "X"),  # 02 - Código do modelo do documento fiscal, conforme a Tabela 4.1.1
        ("COD_SIT",         2,     "N*"),  # 03 - Código da situação do documento fiscal, conforme a Tabela 4.1.2
        ("NUM_DOC",         6,      "N"),  # 04 - Número do documento fiscal (COO)
        ("DT_DOC",          8,     "D?"),  # 05 - Data da emissão do documento fiscal
        ("VL_DOC",        255,    "NN?"),  # 06 - Valor total do documento fiscal
        ("VL_PIS",        255,    "NN?"),  # 07 - Valor do PIS
        ("VL_COFINS",     255,    "NN?"),  # 08 - Valor da COFINS
        ("CPF_CNPJ",       14,      "X"),  # 09 - CPF ou CNPJ do adquirente
        ("NOM_ADQ",        60,      "X"),  # 10 - Nome do adquirente
    ))
    RC470 = SpedRecord("C470", (  # ITENS DO DOCUMENTO FISCAL EMITIDO POR ECF
        ("COD_ITEM",       60,      "X"),  # 02 - Código do item (campo 02 do Registro 0200)
        ("QTD",           255,     "N3"),  # 03 - Quantidade do item
        ("QTD_CANC",      255,     "N3"),  # 04 - Quantidade cancelada, no caso de cancelamento parcial de item
        ("UNID",            6,      "X"),  # 05 - Unidade do item (Campo 02 do registro 0190)
        ("VL_ITEM",       255,     "NN"),  # 06 - Valor do item
        ("CST_ICMS",        3,     "N*"),  # 07 - Código da Situação Tributária, conforme a Tabela indicada no item 4.3.1.
        ("CFOP",            4,     "N*"),  # 08 - Código Fiscal de Operação e Prestação
        ("ALIQ_ICMS",       6,     "NN"),  # 09 - Alíquota do ICMS - Carga tributária efetiva em percentual
        ("VL_PIS",        255,     "NN"),  # 10 - Valor do PIS
        ("VL_COFINS",     255,     "NN"),  # 11 - Valor da COFINS
    ))
    RC490 = SpedRecord("C490", (  # REGISTRO ANALÍTICO DO MOVIMENTO DIÁRIO
        ("CST_ICMS",        3,     "N*"),  # 02 - Código da Situação Tributária, conforme a Tabela indicada no item 4.3.1.
        ("CFOP",            4,     "N*"),  # 03 - Código Fiscal de Operação e Prestação
        ("ALIQ_ICMS",       6,     "NN"),  # 04 - Alíquota do ICMS
        ("VL_OPR",        255,     "NN"),  # 05 - Valor da operação correspondente à combinação de CST_ICMS, CFOP, e alíquota do ICMS, incluídas as despesas acessórias e acréscimos
        ("VL_BC_ICMS",    255,     "NN"),  # 06 - Valor acumulado da base de cálculo do ICMS, referente à combinação de CST_ICMS, CFOP, e alíquota do ICMS
        ("VL_ICMS",       255,     "NN"),  # 07 - Valor acumulado do ICMS, referente à combinação de CST_ICMS, CFOP e alíquota do ICMS.
        ("COD_OBS",         6,      "X"),  # 08 - Código da observação do lançamento fiscal (campo 02 do Registro 0460)
    ))
    RC990 = SpedRecord("C990", (  # Encerramento do bloco C
        ("QTD_LIN_C",      255,     "I"),  # 02 -Quantidade total de linhas do Bloco C
    ))
    RD001 = SpedRecord("D001", (  # Abertura do bloco D
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RD990 = SpedRecord("D990", (  # Encerramento do bloco D
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RE001 = SpedRecord("E001", (  # Abertura do bloco E
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RE100 = SpedRecord("E100", (  # PERÍODO DA APURAÇÃO DO ICMS
        ("DT_INI",          8,      "D"),  # 02 - Data inicial a que a apuração se refere
        ("DT_FIN",          8,      "D"),  # 03 - Data final a que a apuração se refere
    ))
    RE110 = SpedRecord("E110", (  # APURAÇÃO DO ICMS - OPERAÇÕES PRÓPRIAS
        ("VL_TOT_DEBITOS",             255,      "NN"),  # 02 - Valor total dos débitos por "Saídas e prestações com débito do imposto"
        ("VL_AJ_DEBITOS",              255,      "NN"),  # 03 - Valor total dos ajustes a débito decorrentes do documento fiscal.
        ("VL_TOT_AJ_DEBITOS",          255,      "NN"),  # 04 - Valor total de "Ajustes a débito"
        ("VL_ESTORNOS_CRED",           255,      "NN"),  # 05 - Valor total de Ajustes “Estornos de créditos”
        ("VL_TOT_CREDITOS",            255,      "NN"),  # 06 - Valor total dos créditos por "Entradas e aquisições com crédito do imposto"
        ("VL_AJ_CREDITOS",             255,      "NN"),  # 07 - Valor total dos ajustes a crédito decorrentes do documento fiscal.
        ("VL_TOT_AJ_CREDITOS",         255,      "NN"),  # 08 - Valor total de "Ajustes a crédito"
        ("VL_ESTORNOS_DEB",            255,      "NN"),  # 09 - Valor total de Ajustes “Estornos de Débitos”
        ("VL_SLD_CREDOR_ANT",          255,      "NN"),  # 10 - Valor total de "Saldo credor do período anterior"
        ("VL_SLD_APURADO",             255,      "NN"),  # 11 - Valor do saldo devedor apurado
        ("VL_TOT_DED",                 255,      "NN"),  # 12 - Valor total de "Deduções"
        ("VL_ICMS_RECOLHER",           255,      "NN"),  # 13 - Valor total de "ICMS a recolher (11-12)
        ("VL_SLD_CREDOR_TRANSPORTAR",  255,      "NN"),  # 14 - Valor total de "Saldo credor a transportar para o período seguinte”
        ("DEB_ESP",                    255,      "NN"),  # 15 -Valores recolhidos ou a recolher, extra-apuração.
    ))
    RE116 = SpedRecord("E116", (  # OBRIGAÇÕES DO ICMS A RECOLHER - OPERAÇÕES PRÓPRIAS
        ("COD_OR",          3,      "X"),  # 02 - Código da obrigação a recolher, conforme a Tabela 5.4
        ("VL_OR",         255,     "NN"),  # 03 - Valor da obrigação a recolher
        ("DT_VCTO",         8,      "D"),  # 04 - Data de vencimento da obrigação
        ("COD_REC",       255,      "X"),  # 05 - Código de receita referente à obrigação, próprio da unidade da federação, conforme legislação estadual
        ("NUM_PROC",       15,      "X"),  # 06 - Número do processo ou auto de infração ao qual a obrigação está vinculada, se houver
        ("IND_PROC",        1,      "X"),  # 07 - Indicador da origem do processo. 0- Sefaz; 1- Justiça Federal; 2- Justiça Estadual; 9- Outros
        ("PROC",          255,      "X"),  # 08 - Descrição resumida do processo que embasou o lançamento
        ("TXT_COMPL",     255,      "X"),  # 09 - Descrição complementar das obrigações a recolher
        ("MES_REF",         6,     "N*"),  # 10 - Informe o mês de referência no formato "mmaaaa"
    ))

    RE990 = SpedRecord("E990", (  # Encerramento do bloco H
        ("QTD_LIN_E",      255,      "I"),  # 02 -Quantidade total de linhas do Bloco E
    ))
    RG001 = SpedRecord("G001", (  # Abertura do bloco G
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RG990 = SpedRecord("G990", (  # Encerramento do bloco G
        ("QTD_LIN_G",      255,      "I"),  # 02 -Quantidade total de linhas do Bloco G
    ))
    RH001 = SpedRecord("H001", (  # Abertura do bloco H
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    RH005 = SpedRecord("H005", (  # Inventário
        ("DT_INV",          8,      "D"),  # 02 -Data do inventário
        ("VL_INV",        255,     "NN"),  # 03 - Valor total do estoque
    ))
    RH010 = SpedRecord("H010", (  # Inventário
        ("COD_ITEM",       60,      "X"),  # 02 -Código do item (campo 02 do Registro 0200)
        ("UNID",            6,      "X"),  # 03 -Unidade do item
        ("QTD",           255,      "X"),  # 04 -Quantidade do item (c/ 3 casas decimais)
        ("VL_UNIT",       255,      "X"),  # 05 -Valor unitário do item com (2 casa decimais)
        ("VL_ITEM",       255,      "X"),  # 06 -Valor do item (c/ 2 casa decimais)
        ("IND_PROP",        1,      "X"),  # 07 -Indicador de propriedade/posse do item: [tabela abaixo]
        ("COD_PART",       60,      "X"),  # 08 -Código do participante (campo 02 do Registro 0150)
        ("TXT_COMPL",     255,      "X"),  # 09 -Descrição complementar
        ("COD_CTA",       255,      "X"),  # 10 -Código da conta analítica contábil debidata/creditada]
    ))
    # Tabela indicador de propriedade/posse [campo 07]
    # 0 - Item de propriedade do informante e em seu poder;
    # 1 - Item de propriedade do informante e em posse de terceiros;
    # 2 - Item de propriedade de terceiros em posse do informante;
    RH990 = SpedRecord("H990", (  # Encerramento do bloco H
        ("QTD_LIN_H",      255,      "I"),  # 02 -Quantidade total de linhas do Bloco H
    ))
    R9001 = SpedRecord("9001", (  # Abertura do bloco 9
        ("IND_MOV",         1,      "N"),  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
    ))
    R9900 = SpedRecord("9900", (  # Registro do arquivo
        ("REG_BLC",       255,      "X"),  # 02 -Registro que será totalizado no próximo campo
        ("QTD_REG_BLC",   255,      "I"),  # 03 -Total de registro do tipo informado no campo anterior
    ))
    R9990 = SpedRecord("9990", (  # Encerramento do bloco 9
        ("QTD_LIN_9",      255,      "I"),  # 02 -Quantidade total de linhas do Bloco 9
    ))
    R9999 = SpedRecord("9999", (  # Encerramento do arquivo digital
        ("QTD_LIN",        255,      "I"),  # 02 -Quantidade de linhas do arquivo digital
    ))
    U1 = Record("U1", (
        ("CNPJ", 14, "N"),
        ("I.E.", 14, "X"),
        ("I.M.", 14, "X"),
        ("Razao social", 50, "X")
    ))
    A2 = Record("A2", (
        ("DT_DOC", 8, "D"),
        ("TENDER_DESCR", 25, "X"),
        ("TENDER_TYPE", 1, "X"),
        ("AMOUNT", 12, "N")
    ))
    Z1 = Record("Z1", (
        ("CNPJ", 14, "N"),
        ("I.E.", 14, "X"),
        ("I.M.", 14, "X"),
        ("Razao social", 50, "X")
    ))
    Z2 = Record("Z2", (
        ("CNPJ", 14, "N"),
        ("I.E.", 14, "X"),
        ("I.M.", 14, "X"),
        ("Razao social", 50, "X")
    ))
    Z3 = Record("Z3", (
        ("Numero do Laudo", 10, "X"),
        ("SW Name", 50, "X"),
        ("SW Version", 10, "X")
    ))
    Z4 = Record("Z4", (
        ("Numero do CPF-CNPJ", 14, "N"),
        ("Totalizacao Mensal", 14, "N"),
        ("Data Inicial", 8, "D"),
        ("Data Final", 8, "D"),
        ("Data Geracao", 8, "D"),
        ("Hora Geracao", 6, "H"),
    ))
    Z9 = Record("Z9", (
        ("CNPJ", 14, "N"),
        ("I.E.", 14, "X"),
        ("Numero Registros", 6, "N")
    ))


def inventoryReport(posid, period, filters, serial, *args):
    '''
    ANEXO IV - DADOS TÉCNICOS PARA GERAÇÃO DO ARQUIVO ELETRÔNICO DO ESTOQUE (ITEM 8 DO REQUISITO VII)

    6 - MONTAGEM DO ARQUIVO ELETRÔNICO:
    +------------------+------------------------------------+-----------------------------------------+--------+
    | Tipo de Registro | Nome do Registro                   | Denominação dos Campos de Classificação | A/D*   |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | E1               | Identificação do estabelecimento   | 1º registro (único)                     | ------ |
    |                  | usuário do PAF-ECF                 |                                         |        |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | E2               | Relação das mercadorias em estoque | Tipo de registro                        |        |
    |                  |                                    | Código da mercadoria ou produto         | A      |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | E9               | Totalização de registros           | Penúltimo registro (único)              | ------ |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | EAD              | Assinatura digital                 | Último registro (único)                 | ------ |
    +------------------+------------------------------------+-----------------------------------------+--------+
    * A indicação "A/D" significa ascendente/descendente


    7.1 REGISTRO TIPO E1 - IDENTIFICAÇÃO DO ESTABELECIMENTO USUÁRIO DO PAF-ECF:
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteudo                | Tamanho | Posicao   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo de registro     | "E1"                    | 02      |   1 |   3 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ                 | CNPJ do estabelecimento | 14      |   3 |  16 |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 |Inscrição Estadual    | Inscrição Estadual do   | 14      |  17 |  30 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 |Inscrição Municipal   | Inscrição Municial do   | 14      |  31 |  44 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 05 |Razao Social do       | Razao Social do         | 50      |  45 |  94 |    X    |
    |    |estabelecimento       | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

    7.2 - REGISTRO TIPO E2 - RELAÇÃO DAS MERCADORIAS EM ESTOQUE:
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo de registro     | "E2"                    | 02      |   1 |   2 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ                 | CNPJ do estabelecimento | 14      |   3 | 16  |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 | Código               | Código da mercadoria    | 14      |  17 |  30 |    X    |
    |    |                      | ou produto              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 | Descrição            | Descrição da mercadoria | 50      |  31 |  80 |    X    |
    |    |                      | ou produto              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 05 | Unidade              | Unidade de medida       |         |     |     |         |
    |    |                      | cadastrada na tabela    | 06      |  81 |  86 |    X    |
    |    |                      | a que se refere o       |         |     |     |         |
    |    |                      | requisito XI            |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 06 | Quantidade em        | Quantidade da mercadoria|         |     |     |         |
    |    | estoque              | ou produto constante no | 09      |  87 |  95 |    N    |
    |    |                      | estoque, com duas casas |         |     |     |         |
    |    |                      | decimais.               |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 07 | Data do estoque      | Data referente à posição|         |     |     |         |
    |    |                      | do estoque informada no | 08      |  96 | 103 |    D    |
    |    |                      | campo 06                |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

    7.3. REGISTRO TIPO E9 - TOTALIZAÇÃO DO ARQUIVO
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo                 | "E9"                    | 02      |  01 |  02 |    N    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ/MF              | CNPJ do estabelecimento | 14      |  03 |  16 |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 | Inscrição Estadual   | Inscrição Estadual do   | 14      |  17 |  30 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 | Total de registros   | Qtd de registros tipo   | 06      |  31 |  36 |    N    |
    |    | tipo E2              | E2 informados no arquivo|         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

     7.4 - REGISTRO TIPO EAD - ASSINATURA DIGITAL
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo do registro     | "EAD"                   | 03      |  01 |  03 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | Assinatura Digital   | Assinatura do Hash      | 256     |  04 | 259 |    X    |
    +----+----------------------+-------------------------+:---------+-----+-----+---------+

    '''
    report = Report()
    try:
        companyName, federalRegister, stateRegister, municipalRegister = readEncrypted(posid, "User_CompanyName",
                                                                                               "User_FederalRegister", "User_StateRegister", "User_MunicipalRegister")
    except:
        companyName, federalRegister, stateRegister, municipalRegister = ("BK BRASIL OPERACAO E ASSESSORIA A RESTAURANTES S/A", 11111111111111, "222222222", "333333333")

    # open a database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))

        sql_where = ""
        if len(filters) > 0:
            for filter in filters.split('|'):
                filter = filter.strip()
                if not sql_where:
                    sql_where = "WHERE "
                else:
                    sql_where += " OR "
                try:
                    filter = int(filter)
                    sql_where += "SKU=%d" % filter
                except:
                    sql_where += "Descr LIKE '%" + conn.escape(filter) + "%'"

        table = "EstoqueHistorico"
        sql = '''
        SELECT
            SKU,Descr,Unidade,Qty,
            CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
        FROM fiscalinfo.%(table)s EH
        LEFT JOIN fiscalinfo.FiscalD D ON D.TB='%(table)s' AND D.R=EH._ROWID_ AND (D.OP='A' OR
            D.C IN ('SKU','Descr','Unidade','Qty','Tampered'))
        %(sql_where)s
        GROUP BY EH._ROWID_
        ORDER BY SKU
        ''' % locals()
        qtyItems = 0
        for row in conn.select(sql):
            code, name, unit, qty, tampered = map(row.get_entry, ("SKU", "Descr", "Unidade", "Qty", "Tampered"))
            signal = "+"
            if qty.startswith("-"):
                signal = "-"
                qty = qty[1:]
            if int(tampered):
                unit = "%-6s" % unit
                unit = unit.replace(" ", "?")
            report.write(records.E2(
                federalRegister,
                code,
                name,
                unit,
                signal,
                qty
            ))
            report.write("\r\n")
            qtyItems += 1

        cursor = conn.select("""
                SELECT
                    FP.*,
                    CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
                FROM fiscalinfo.FiscalPrinters FP
                LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalPrinters' AND D.R=FP._ROWID_
                    AND D.C IN ('FPSerialNo', 'CreatedAt', 'AdditionalMem','ECFType','ECFBrand','ECFModel','ECFSwVersion','ECFSwDate','ECFSwTime','ECFPosId')
                WHERE FP.PosId=%(posid)s AND FP.FPSerialNo='%(serial)s'
                GROUP BY FP._ROWID_
                """ % locals())
        row = cursor.get_row(0)
        if row:
            data_hora = row.get_entry("CreatedAt").replace("-", "").replace(" ", "").replace(":", "")
            report.write(records.E3(
                row.get_entry("FPSerialNo"),  # [02] Nº Fabricação
                row.get_entry("AdditionalMem"),  # [03] MF adicional
                row.get_entry("ECFType"),  # [05] Tipo de ECF
                row.get_entry("ECFBrand"),  # [06] Marca do ECF
                get_ecf_model(row),  # [07] Modelo do ECF
                data_hora[:8],
                data_hora[8:]
            ))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[inventoryReport] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def get_ecf_model(row):
    model = row.get_entry("ECFModel")
    tampered = int(row.get_entry("Tampered"))
    if not tampered:
        try:
            tampered = int(row.get_entry("Tampered2"))
        except:
            pass
    if tampered:
        # This row has been tampered! Hack the ECF model to notify authorities
        model = "%-20s" % model
        model = model.replace(" ", "?")
    return model


def paf_sintegra(posid, period_begin, period_end, *args):
    # "Vendas do Período" - Convênio 57/95 - SINTEGRA
    #
    # Req. VII item 19:
    # “Vendas do Período” para gerar arquivo eletrônico das operações de saída e das prestações praticadas, conforme
    # leiaute estabelecido no Manual de Orientação do Convênio 57/95, devendo conter ainda os registros tipo 10, 11, 75 e 90

    totItems = {'60': 0, '61': 0, '75': 0}

    report = Report()
    companyName, federalRegister, stateRegister, municipalRegister, reportPath, serial = readEncrypted(posid, "User_CompanyName",
                                                                                                       "User_FederalRegister", "User_StateRegister", "User_MunicipalRegister", "FiscalOutputPath", "ECF_Serial")
    if not reportPath:
        reportPath = "./"

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period_begin, period_end))

        def onlydigits(string):
            return re.sub(r"[^\d]", "", string)

        fax, municipio, unidadefed, logradouro, numero, complemento, bairro, cep, contato, telefone = ("0", "N/A", "??", "??", "0", "", "??", "12345000", "??", "0")
        cursor = conn.select("SELECT KeyPath,KeyValue FROM storecfg.Configuration WHERE KeyPath LIKE 'Store.%';")
        for row in cursor:
            k, v = row.get_entry("KeyPath"), row.get_entry("KeyValue")
            if k == "Store.Fax":
                fax = v
            elif k == "Store.Municipio":
                municipio = v
            elif k == "Store.UnidadeFederacao":
                unidadefed = v
            elif k == "Store.Logradouro":
                logradouro = v
            elif k == "Store.NumeroEndereco":
                numero = v
            elif k == "Store.Complemento":
                complemento = v
            elif k == "Store.Bairro":
                bairro = v
            elif k == "Store.CEP":
                cep = v
            elif k == "Store.Contato":
                contato = v
            elif k == "Store.Telefone":
                telefone = v

        codigo_convenio = 3  # Estrutura conforme Convênio ICMS 57/95, com as alterações promovidas pelo Convênio ICMS 76/03.
        codigo_natureza = 3  # Totalidade das operações do informante
        codigo_finalidade = 1  # Normal

        regex_tax_rate = re.compile("\d\dT(\d\d\d\d)")

        def get_totalizer(taxcode):
            match = regex_tax_rate.match(taxcode)
            if match:
                return match.group(1)
            elif taxcode == "Can-T":
                return "CANC"
            elif taxcode == "DT":
                return "DESC"
            elif taxcode[1] == "S":
                return ""  # ISSQN not yet supported!
            elif taxcode[0] in ("F", "I", "N"):
                return taxcode[0]
            return ""

        report.write(records.T10(
            federalRegister,    # CGC/MF do estabelecimento informante
            stateRegister,      # Inscrição estadual do estabelecimento informante
            companyName,        # Nome comercial (razão social / denominação) do contribuinte
            municipio,          # Município onde está domiciliado o estabelecimento informante
            unidadefed,         # Unidade da Federação referente ao Município
            onlydigits(fax),    # Número do fax do estabelecimento informante
            period_begin,       # A data do início do período referente às informações prestadas
            period_end,         # A data do fim do período referente às informações prestadas
            codigo_convenio,    # Código da identificação da estrutura do arquivo magnético entregue
            codigo_natureza,    # Código da identificação da natureza das operações informadas
            codigo_finalidade   # Código do finalidade utilizado no arquivo magnético
        ))
        report.write("\r\n")
        report.write(records.T11(
            logradouro,
            numero,
            complemento,
            bairro,
            onlydigits(cep),
            contato,
            onlydigits(telefone)
        ))
        report.write("\r\n")

        # Registro Tipo 60 - Mestre (60M): Identifica o equipamento emissor de cupom fiscal no contribuinte
        cursor = conn.select("""SELECT *
            FROM fiscalinfo.ZTapes
            WHERE PosId=%(posid)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
            ORDER BY FPSerialNo,ECFModel,ECFUser,CRZ,CRO
        """ % locals())
        first_zperiod = 0
        last_zperiod = 0
        for row in cursor:
            serial = row.get_entry("FPSerialNo")
            period = int(row.get_entry("Period"))
            CRZ = int(row.get_entry("CRZ"))
            if not first_zperiod:
                first_zperiod = period
            last_zperiod = period
            data = map(row.get_entry, (
                "AdditionalMem",  # [03] MF adicional
                "ECFModel",       # [04] Modelo do ECF
                "CRZ",            # [06] CRZ - No do Contador de Reducao Z             |      06 |  47 |  52 |    N    |
                "LastCOO",        # [07] COO - No do Contador de Ordem de Operacao     |      06 |  53 |  58 |    N    |
                "CRO",            # [08] CRO - No do Contador de Reinicio de Operacao  |      06 |  59 |  64 |    N    |
                "FPDate",         # [10] Data de emissao da Reducao Z                  |      08 |  73 |  80 |    D    |
                "FPTime",         # [11] Hora de emissao da Reducao Z                  |      06 |  81 |  86 |    H    |
                "DGT",            # [12] Venda Bruta Diaria                            |      14 |  87 | 100 |    N    |
                "ISSQN"           # [13] Parametro desc. ISSQN                         |      01 | 101 | 101 |    X    |
            ))
            totItems['60'] += 1
            report.write(records.T60M(
                row.get_entry("FPBusinessDate"),  # Data de emissão dos documentos fiscais
                row.get_entry("FPSerialNo"),     # Número de série de fabricação do equipamento
                row.get_entry("ECFUser"),        # Número atribuído pelo estabelecimento ao equipamento
                "2D",                            # Código do modelo do documento fiscal - "2D", quando se tratar de Cupom Fiscal (emitido por ECF)
                row.get_entry("FirstCOO"),       # Número do primeiro documento fiscal emitido no dia (Número do Contador de Ordem de Operação - COO)
                row.get_entry("LastCOO"),        # Número do último documento fiscal emitido no dia (Número do Contador de Ordem de Operação - COO)
                row.get_entry("CRZ"),            # Número do Contador de Redução Z (CRZ)
                row.get_entry("CRO"),            # Valor acumulado no Contador de Reinício de Operação (CRO)
                row.get_entry("DGT"),            # Valor acumulado no totalizador de Venda Bruta
                row.get_entry("GT"),             # Valor acumulado no Totalizador Geral
                ""                               # -- espaços em branco
            ))
            report.write("\r\n")

            cursor = conn.select("""SELECT *
                FROM fiscalinfo.ZTapeTotalizers
                WHERE PosId=%(posid)s AND FPSerialNo='%(serial)s' AND CRZ=%(CRZ)s
            """ % locals())
            for row in cursor:
                totalizer = get_totalizer(row.get_entry("Totalizer"))
                if not totalizer:
                    continue
                amount = row.get_entry("Amount")
                totItems['60'] += 1
                report.write(records.T60A(
                    period,                  # Data de emissão dos documentos fiscais
                    serial,                  # Número de série de fabricação do equipamento
                    totalizer,               # Identificador da Situação Tributária / Alíquota do ICMS
                    amount,                  # Valor acumulado no final do dia no totalizador parcial da situação tributária / alíquota indicada no campo 05 (com 2 decimais)
                    ""                       # -- espaços em branco
                ))
                report.write("\r\n")
            # 16.4 - Registro Tipo 60 - Resumo Diário (60D): Registro de mercadoria/produto ou serviço constante em documento fiscal emitido por Terminal Ponto de Venda (PDV) ou equipamento Emissor de Cupom Fiscal (ECF).
            cursor = conn.select("""
            SELECT
                FO.Period AS BusinessPeriod,
                FOI.PartCode AS ProductCode,
                tdsum(FOI.OrderedQty) AS Qty,
                tdsum(tdmul(FOI.UnitPrice, FOI.OrderedQty)) AS TotalAmount,
                FOI.TaxCode AS TaxCode
            FROM fiscalinfo.FiscalOrderItems FOI
                JOIN fiscalinfo.FiscalOrders FO ON FO.OrderId=FOI.OrderId
            WHERE FO.Period=%(period)s
                AND FO.StateId=5
                AND FOI.Level=0
                AND FOI.OrderedQty>0
                AND FO.FPSerialNo='%(serial)s'
            GROUP BY ProductCode, BusinessPeriod
            """ % locals())
            for row in cursor:
                date, pcode, qty, totAmount, taxCode = map(row.get_entry, ("BusinessPeriod", "ProductCode", "Qty", "TotalAmount", "TaxCode"))
                taxCode = get_totalizer(taxCode)
                try:
                    int(taxCode)  # will raise exception if non-taxable
                    taxRate = D(taxCode) / D("10000")  # E.g.: "0320" -> "0.032"
                except:
                    taxRate = ZERO
                taxAmt = D(totAmount) * taxRate
                report.write(records.T60D(
                    date,           # Data de emissão dos documentos fiscais
                    serial,         # 04 -Número de série de fabricação do equipamento
                    pcode,          # 05 -Código do produto ou serviço utilizado pelo contribuinte
                    qty,            # 06 -Quantidade comercializada da mercadoria/produto
                    totAmount,      # 07 -Valor acumulado liquido da mercadoria/produto
                    totAmount,      # 08 -Base de Cálculo do ICMS de substituição tributária (com 2 decimais)
                    taxCode,        # 09 -Identificador da Situação Tributária / Alíquota do ICMS
                    taxAmt,         # 10 -Valor do Montante do Imposto/Total diário (com 2 decimais)
                    ""
                ))
                report.write("\r\n")
                totItems['60'] += 1

        #
        # NOTAS MANUAIS
        #
        cursor = conn.select("""
        SELECT
            NM.Data AS Data,
            NM.Serie AS Serie,
            NM.Subserie AS Subserie,
            MIN(NM.Numero) AS NumeroInicial,
            MAX(NM.Numero) AS NumeroFinal,
            tdsum(O.TotalGross) AS ValorTotal,
            tdsub(tdsum(O.TotalGross),tdsum(O.TotalNet),2) AS TaxAmount,
            COALESCE((SELECT KeyValue FROM storecfg.Configuration WHERE KeyPath='Store.AliquotaICMS'),'0.00') AS TaxRate
        FROM fiscalinfo.NotasManuais NM
        JOIN orderdb.Orders O ON O.OrderId=NM.OrderId
        WHERE NM.Data BETWEEN %s AND %s
        GROUP BY NM.Data, NM.Serie, NM.Subserie
        ORDER BY NM.Data
        """ % (period_begin, period_end))
        for row in cursor:
            data, serie, subserie, num_inicial, num_final, totAmount, taxAmount, taxRate = map(row.get_entry, ("Data", "Serie", "Subserie", "NumeroInicial", "NumeroFinal", "ValorTotal", "TaxAmount", "TaxRate"))
            base_calculo = totAmount
            totItems['61'] += 1
            report.write(records.T61(
                "",             # -- espaços em branco
                "",             # -- espaços em branco
                data,           # Data de emissão dos documentos fiscais
                2,              # Modelo do(s) documento(s) fiscal(is)
                serie,          # Série do(s) documento(s) fiscal(is)
                subserie,       # Série do(s) documento(s) fiscal(is)
                num_inicial,    # Número do primeiro documento fiscal emitido no dia do mesmo modelo, série e subsérie
                num_final,      # Número do último documento fiscal emitido no dia do mesmo modelo, série e subsérie
                totAmount,      # Valor total do(s) documento(s) fiscal(is)/Movimento diário (com 2 decimais)
                base_calculo,   # Base de cálculo do(s) documento(s) fiscal(is)/Total diário (com 2 decimais)
                taxAmount,      # Valor do Montante do Imposto/Total diário (com 2 decimais)
                0,              # Valor amparado por isenção ou não-incidência/Total diário (com 2 decimais)
                0,              # Valor que não confira débito ou crédito de ICMS/Total diário (com 2 decimais)
                taxRate,        # Alíquota do ICMS (com 2 decimais)
                ""              # -- espaços em branco
            ))
            report.write("\r\n")

        # T75
        # get the data
        cursor = conn.select("""
        SELECT
                OI.PartCode AS ProductCode,
                P.ProductName AS ProductName,
                PKP.MeasureUnit AS MeasureUnit,
                COALESCE(PCP.CustomParamValue,'') AS NCM,
                COALESCE(TR.TaxRate,'0.00') AS TaxRate
            FROM orderdb.Orders O
            JOIN orderdb.OrderItem OI
                ON OI.OrderId = O.OrderId
            JOIN productdb.Product P
                ON P.ProductCode = OI.PartCode
            JOIN productdb.ProductKernelParams PKP
                ON PKP.ProductCode = OI.PartCode
            LEFT JOIN productdb.ProductCustomParams PCP
                ON PCP.ProductCode = OI.PartCode AND PCP.CustomParamId = 'NCM'
            JOIN taxcalc.ProductTaxCategory PTC
                ON PTC.ItemId = OI.ItemId||'.'||OI.PartCode
            LEFT JOIN taxcalc.TaxRule TR
                ON TR.TaxCgyId = PTC.TaxCgyId AND TR.TaxId IN (1,2,3)
            WHERE O.BusinessPeriod BETWEEN %(first_zperiod)s AND %(last_zperiod)s
            GROUP BY ProductCode
            ORDER BY ProductCode;
        """ % locals())
        for row in cursor:
            totItems['75'] += 1
            productCode, productName, measureUnit, NCM, taxRate = map(row.get_entry, ("ProductCode", "ProductName", "MeasureUnit", "NCM", "TaxRate"))
            report.write(records.T75(
                period_begin,       # Data inicial do período de validade das informações
                period_end,         # Data final do período de validade das informações
                productCode,        # Código do produto ou serviço utilizado pelo contribuinte
                NCM,                # Codificação da Nomenclatura Comum do Mercosul
                productName,        # Descrição do produto ou serviço
                measureUnit,        # Unidade de medida de comercialização do produto ( un, kg, mt, m3, sc, frd, kWh, etc..)
                0,                  # Alíquota do IPI do produto (com 2 decimais)
                taxRate,            # Alíquota do ICMS aplicável a mercadoria ou serviço nas operações ou prestações internas ou naquelas que se tiverem iniciado no exterior (com 2 decimais)
                0,                  # % de Redução na base de cálculo do ICMS, nas operações internas (com 2 decimais)
                0                   # Base de Cálculo do ICMS de substituição tributária (com 2 decimais)
            ))
            report.write("\r\n")

        # generate 90 detail
        totRecords = report.getvalue().count("\r\n") + 1
        report.write(records.T90(
            federalRegister,    # CGC/MF do estabelecimento informante
            stateRegister,      # Inscrição estadual do estabelecimento informante
            "60",               # Tipo de registro que será totalizado pelo próximo campo
            totItems['60'],     # Total de registros do tipo informado no campo anterior
            "61",               # Tipo de registro que será totalizado pelo próximo campo
            totItems['61'],     # Total de registros do tipo informado no campo anterior
            "75",               # Tipo de registro que será totalizado pelo próximo campo
            totItems['75'],     # Total de registros do tipo informado no campo anterior
            "99",               # Tipo de registro (TOTAL GERAL)
            totRecords,         # Total de registros (TOTAL GERAL)
            "",                 # -- espaços em branco (pois só totalizamos o registro tipo 75)
            1                   # Número de registros tipo 90
        ))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[paf_sintegra] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def paf_sped(posid, period_begin, period_end, *args):
    # "Vendas do Período" - Ato COTEPE/ICMS 09/08 - SPED - http://www.fazenda.gov.br/confaz/confaz/atos/atos_cotepe/2008/ac009_08.htm
    #
    # Req. VII item 19:
    # “Vendas do Período” para gerar arquivo eletrônico das operações de saída e das prestações praticadas,
    # conforme leiaute estabelecido...  # e outro arquivo eletrônico contendo os registros do
    # Ato COTEPE/ICMS 09/08, neste caso contendo ainda a tabela de blocos 0, H e 9,
    # com possibilidade de seleção por período de data, devendo, os arquivos, serem assinados digitalmente...
    #
    # Formato do arquivo - Hierarquico
    #    0000 - Abertura do arquivo
    #    .    0001 - Abre bloco 0
    #    .    .    0005 - informa dados adicionais - do declarante
    #    .    .    0190 - identificação das unidades de medida
    #    .    .    0200 - identificação do item produto/serviço (diversos)      # TABELA DE PRODUTOS
    #    .    0990 - Encerra bloco 0
    #    .    C001 - Abre bloco C
    #    .    .    C350 - Nota Fiscal de venda a consumidor (diversos)          # NOTA MANUAL
    #    .    .    .   C370 - Itens do documento  (diversos)                    # NOTA MANUAL
    #    .    .    .   C390 - Registro Analítico  (diversos)                    # NOTA MANUAL
    #    .    C990 - Encerra bloco H
    #    .    H001 - Abre bloco H
    #    .    .    H010 - Inventário (diversos)                                 # ESTOQUE
    #    .    H990 - Encerra bloco H
    #    .    9001 - Abre bloco 9
    #    .    .    9900 - Totalizador de campos  (diversos)                     # Totalizador dos campos
    #    .    9990 - Encerra bloco 9
    #    9999 - Fechamento do arquivo
    # quantidade de linhas
    lq = defaultdict(int)  # Line Quantity
    report = Report()
    companyName, federalRegister, stateRegister, municipalRegister, reportPath, serial = readEncrypted(posid, "User_CompanyName",
                                                                                                       "User_FederalRegister", "User_StateRegister", "User_MunicipalRegister", "FiscalOutputPath", "ECF_Serial")
    if not reportPath:
        reportPath = "./"

    def fromutf(string):
        return unicode(string, "UTF-8")

    def onlydigits(string):
        return re.sub(r"[^\d]", "", string)

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period_begin, period_end))
        CFOP = "5929"  # <- Lançamento efetuado em decorrência de emissão de documento fiscal relativo a operação ou prestação também registrada em equipamento Emissor de Cupom Fiscal - ECF

        def getCST_ICMS(taxCode):
            if taxCode[0] == "N":
                return "041"  # Nao tributado
            if taxCode[0] == "F":
                return "030"  # Substituição
            if taxCode[0] == "I":
                return "040"  # Isento
            return "000"  # Tributado integralmente
        # Codigo de situacao tributária: Nacional - Com redução de base de cálculo
        CST_ICMS = "020"
        fileTotalTax = ZERO  # This will be consolidated thru the C block

        fax, municipio, unidadefed, logradouro, numero, complemento, bairro, cep, contato, telefone, municipio_ibge, suframa, cpf, fantasia, email = ("0", "N/A", "??", "??", "0", "", "??", "0", "??", "0", "??", "", "", "", "")
        rate_pis, rate_cofins = (ZERO, ZERO)
        cursor = conn.select("SELECT KeyPath,KeyValue FROM storecfg.Configuration WHERE KeyPath LIKE 'Store.%';")
        for row in cursor:
            k, v = row.get_entry("KeyPath"), fromutf(row.get_entry("KeyValue"))
            if k == "Store.Fax":
                fax = v
            elif k == "Store.Municipio":
                municipio = v
            elif k == "Store.UnidadeFederacao":
                unidadefed = v
            elif k == "Store.Logradouro":
                logradouro = v
            elif k == "Store.NumeroEndereco":
                numero = v
            elif k == "Store.Complemento":
                complemento = v
            elif k == "Store.Bairro":
                bairro = v
            elif k == "Store.CEP":
                cep = v
            elif k == "Store.Contato":
                contato = v
            elif k == "Store.Telefone":
                telefone = v
            elif k == "Store.MunicipioIBGE":
                municipio_ibge = v
            elif k == "Store.InscricaoSuframa":
                suframa = v
            elif k == "Store.CPF":
                cpf = v
            elif k == "Store.NomeFantasia":
                fantasia = v
            elif k == "Store.EMail":
                email = v
            elif k == "Store.AliquotaPIS":
                rate_pis = D(v)
            elif k == "Store.AliquotaCOFINS":
                rate_cofins = D(v)

        if federalRegister:
            cpf = ""
        #    0000 - Abertura do arquivo
        lq['0000'] += 1
        report.write(records.R0000(   # 01 -Campo fixo "0000"
            "004",                   # 02 -Codigo da versão do leiaute conforme a tabela indicada no Ato Cotepe
            "0",                     # 03 -Codigo da finalidade do arquivo 0 - Remessa do arquivo Original; 1 - Remessa do arquivo substituto
            period_begin,            # 04 -Data inicial das informações contidas no arquivo
            period_end,              # 05 -Data final das informações contidas no arquivo
            companyName,             # 06 -Nome empresarial da entidade
            federalRegister,         # 07 -Numero de inscrição da entidade no CNPJ
            cpf,                     # 08 -Numero de inscrição da entidade no CPF
            unidadefed,              # 09 -Sigla da unidade da federação da entidade
            stateRegister,           # 10 -Inscrição estadual da entidade
            municipio_ibge,          # 11 -Codigo do município do domicílio fiscal da entidade, conforme a tabela IBGE
            municipalRegister,       # 12 -Inscrição Municiap da entidade
            suframa,                 # 13 -Inscrição da entidade na Suframa
            "A",                     # 14 -Perfil da apresentação do arquivo fiscal; A:Perfil A; B:Pefil B; C:Perfil C
            "1",                     # 15 -Indicador de tipo de atividade: 0:Industrial ou equip. a industrial; 1:Outros.
        ))
        report.write("\r\n")
        #    .    0001 - Abre bloco 0
        lq['0001'] += 1
        lq['T0'] += 1
        report.write(records.R0001("0"))  # Bloco com dados informados
        report.write("\r\n")
        #    .    .    0005 - informa dados adicionais - do declarante
        lq['0005'] += 1
        lq['T0'] += 1
        report.write(records.R0005(      # 01 -Texto fixo contendo "0005"
            fantasia,                   # 02 -Nome de fantasia associado ao nome empresarial
            onlydigits(cep),            # 03 -Código de endereçamento postal
            logradouro,                 # 04 -Logradouro e endereo do imóvel
            numero,                     # 05 -Número do Imóvel
            complemento,                # 06 -Dados complementares do endereço
            bairro,                     # 07 -Bairro em que o imóvel está situado
            onlydigits(telefone)[-10:],  # 08 -Número do telefone
            onlydigits(fax)[-10:],      # 09 -Número do fax
            email,                      # 10 -Endereço eletrônico
        ))
        report.write("\r\n")
        lq['0100'] += 1
        lq['T0'] += 1
        report.write("|0100|NOME DO CONTABILISTA|96147456490|CRC|41707681000100|01202000|ENDERECO|1||BAIRRO|0055555555|0055555555|contabilista@email.com|3550308|\r\n")
        #    .    .    0190 - identificação das unidades de medida
        lq['0190'] += 1
        lq['T0'] += 1
        report.write(records.R0190("UN", "Unidade"))
        report.write("\r\n")
        lq['0190'] += 1
        lq['T0'] += 1
        report.write(records.R0190("KG", "Quilograma"))
        report.write("\r\n")
        lq['0190'] += 1
        lq['T0'] += 1
        report.write(records.R0190("LT", "Litro"))
        report.write("\r\n")
        lq['0190'] += 1
        lq['T0'] += 1
        report.write(records.R0190("PC", "Peca"))
        report.write("\r\n")

        cursor = conn.select("""
            SELECT
              SKU AS productCode,
              Descr AS producName,
              "18,00" AS taxRule,
              Unidade AS measureUnit,
              Qty AS qty,
              ValorUnitario AS unitPrice
            FROM
              fiscalinfo.Estoque
            UNION ALL
            SELECT
                price.ProductCode AS productCode,
                Product.ProductName AS productName,
                tdScale(TaxRule.TaxRate,2,0) AS taxRule,
                PKP.MeasureUnit as measureUnit,
                1 as qty,
                price.DefaultUnitPrice as unitPrice
            FROM
                Price
            JOIN taxcalc.ProductTaxCategory ProductTaxCategory
                ON ProductTaxCategory.ItemId=price.Context || "." || price.ProductCode
            JOIN taxcalc.TaxCategory TaxCategory
                ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN taxcalc.TaxRule TaxRule
                ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN Product
                ON price.ProductCode=Product.ProductCode
            JOIN productdb.ProductKernelParams PKP
                ON PKP.ProductCode=Product.ProductCode
            WHERE Product.ProductCode IN (SELECT ProductCode FROM Insumos)
            GROUP BY productCode
            ORDER BY productCode
           """)
        for row in cursor:
            productCode, productName, taxRule, unitPrice, measureUnit = map(fromutf, map(row.get_entry, ("productCode", "producName", "taxRule", "unitPrice", "measureUnit")))
            #    .    .    0200 - identificação do item produto/serviço (diversos)      # TABELA DE PRODUTOS
            taxRule = taxRule.replace('.', ',')
            lq['0200'] += 1
            lq['T0'] += 1
            report.write(records.R0200(   # 01 -Texto fixo contendo "0200"
                productCode,              # 02 -Código do item
                productName,              # 03 -Descrição do item
                "",                       # 04 -Representação alfanumérico do código de barra do produto, se houver
                "",                       # 05 -Código anterior do item com relação à última informação apresentada
                measureUnit,              # 06 -Unidade de medida utilizada na qualificação de estoques
                "04",  # Produto Acabado   # 07 -Tipo do item - Atividades Industriais, Comerciais e Serviços [tabela abaixo]
                "",                       # 08 -Código da Nomeclatura Comum do Mercosul
                "",                       # 09 -Código EX, conforme a TIPI
                "",                       # 10 -Código do gênero do item, conforme a Tabela 4.2.1
                "0",                      # 11 -Código do serviço conforme lista do anexo I da Lei Complementar Federan n.116/03
                taxRule,                  # 12 -Alíquota de ICMS aplicável ao item nas operações internas (2 casas decimais;incluir a virgula)
            ))
            report.write("\r\n")
        lq['0990'] += 1
        lq['T0'] += 1
        report.write(records.R0990(lq['T0'] + 1))  # 02 -Quantidade total de linhas do Bloco 0
        report.write("\r\n")

        # Bloco C
        cursor = conn.select("""
            SELECT 1 FROM fiscalinfo.NotasManuais NM WHERE NM.PosId=%(posid)s AND NM.Period BETWEEN %(period_begin)s AND %(period_end)s
            UNION ALL
            SELECT 1 FROM fiscalinfo.ZTapes WHERE PosId=%(posid)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
            LIMIT 1
        """ % locals())
        has_data = cursor.rows() > 0
        #    .    C001 - Abre bloco C
        lq['C001'] += 1
        lq['TC'] += 1
        report.write(records.RC001("0" if has_data else "1"))  # Bloco com dados informados
        report.write("\r\n")
        # NOTAS MANUAIS
        cursor = conn.select("""
        SELECT
            NM.Serie AS Serie,
            NM.Subserie AS Subserie,
            NM.Numero AS Numero,
            NM.Data AS Data,
            NM.CPF AS CPF,
            O.TotalGross AS TotalGross,
            NM.OrderId AS OrderId
        FROM fiscalinfo.NotasManuais NM
        JOIN orderdb.Orders O ON O.OrderId=NM.OrderId
        WHERE NM.PosId=%(posid)s AND NM.Period BETWEEN %(period_begin)s AND %(period_end)s
        """ % locals())
        for row in cursor:
            #    .    C350 - NOTA FISCAL DE VENDA A CONSUMIDOR
            totalAmount = row.get_entry("TotalGross")
            PIS = rate_pis / D("100") * D(totalAmount)
            COFINS = rate_cofins / D("100") * D(totalAmount)
            lq['TC'] += 1
            lq['C350'] += 1
            report.write(records.RC350(
                row.get_entry("Serie"),
                row.get_entry("Subserie"),
                row.get_entry("Numero"),
                row.get_entry("Data"),
                row.get_entry("CPF").replace(".", "").replace("-", ""),
                totalAmount,
                totalAmount,
                "0",
                PIS,
                COFINS,
                ""
            ))
            report.write("\r\n")
            order_id = int(row.get_entry("OrderId"))
            cursor2 = conn.select("""
            SELECT
                OI.PartCode AS ProductCode,
                OI.OrderedQty AS Qty,
                COALESCE(PKP.MeasureUnit,'UN') AS MeasureUnit,
                tdmul(OI.OrderedQty,PR.DefaultUnitPrice) AS Amount
            FROM orderdb.OrderItem OI
            JOIN productdb.ProductKernelParams PKP ON PKP.ProductCode=OI.PartCode
            JOIN productdb.Price PR ON PR.PriceKey=OI.PriceKey
            WHERE OI.OrderId=%(order_id)s AND OI.Level=0
            """ % locals())
            item_number = 1
            for row2 in cursor2:
                #    .    C370 - ITENS DO DOCUMENTO
                lq['TC'] += 1
                lq['C370'] += 1
                report.write(records.RC370(
                    item_number,
                    row2.get_entry("ProductCode"),
                    row2.get_entry("Qty"),
                    row2.get_entry("MeasureUnit"),
                    row2.get_entry("Amount"),
                    "0"
                ))
                report.write("\r\n")
                item_number += 1
            #    .    C390 - REGISTRO ANALÍTICO DAS NOTAS FISCAIS DE VENDA A CONSUMIDOR
            lq['TC'] += 1
            lq['C390'] += 1
            report.write(records.RC390(
                CST_ICMS,
                CFOP,
                "0.00",
                totalAmount,
                totalAmount,
                "0.00",
                "0.00",
                ""
            ))
            report.write("\r\n")

        regex_tax_rate = re.compile("^\d\dT(\d\d\d\d)$")
        #    .    C400 - EQUIPAMENTO ECF
        #    ..     C405 - REDUÇÃO Z
        cursor = conn.select("""SELECT *
            FROM fiscalinfo.ZTapes
            WHERE PosId=%(posid)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
            ORDER BY FPSerialNo,ECFModel,ECFUser,CRZ,CRO
        """ % locals())
        registered_ecfs = set()
        first_zperiod = 0
        last_zperiod = 0
        for row in cursor:
            serial = row.get_entry("FPSerialNo")
            period = int(row.get_entry("Period"))
            CRZ = int(row.get_entry("CRZ"))
            if not first_zperiod:
                first_zperiod = period
            last_zperiod = period
            if serial not in registered_ecfs:
                registered_ecfs.add(serial)
                #    .    C400 - EQUIPAMENTO ECF
                lq['TC'] += 1
                lq['C400'] += 1
                report.write(records.RC400(
                    "2D",                          # Código do modelo do documento fiscal, conforme a Tabela 4.1.1
                    row.get_entry("ECFModel"),     # Modelo do equipamento
                    row.get_entry("FPSerialNo"),   # Número de série de fabricação do ECF
                    row.get_entry("ECFPosId")      # Número do caixa atribuído ao ECF
                ))
                report.write("\r\n")
            #    ..     C405 - REDUÇÃO Z
            data = map(row.get_entry, (
                "FPBusinessDate",  # Data do movimento a que se refere a Redução Z
                "CRO",             # Posição do Contador de Reinício de Operação
                "CRZ",             # Posição do Contador de Redução Z
                "LastCOO",         # Número do Contador de Ordem de Operação do último documento emitido no dia. (Número do COO na Redução Z)
                "GT",              # Valor do Grande Total final
                "DGT",             # Valor da venda bruta
            ))
            lq['TC'] += 1
            lq['C405'] += 1
            report.write(records.RC405(*data))
            report.write("\r\n")
            if D(row.get_entry("DGT")) == ZERO:
                # Redução Z sem movimentação não deve gerar registros filhos!
                continue
            C490_consolidated = defaultdict(lambda: {"CST_ICMS": None, "CFOP": None, "ALIQ_ICMS": None, "VL_OPR": ZERO, "VL_BC_ICMS": ZERO, "VL_ICMS": ZERO})

            def add_C490(CST_ICMS, CFOP, ALIQ_ICMS, VL_OPR, VL_BC_ICMS, VL_ICMS):
                '''Add amounts to C490'''
                key = (str(CST_ICMS), str(CFOP), str(ALIQ_ICMS))
                if D(ALIQ_ICMS) == ZERO:
                    VL_OPR, VL_BC_ICMS, VL_ICMS = ZERO, ZERO, ZERO
                x = C490_consolidated[key]
                x["CST_ICMS"] = CST_ICMS
                x["CFOP"] = CFOP
                x["ALIQ_ICMS"] = ALIQ_ICMS
                x["VL_OPR"] += D(VL_OPR)
                x["VL_BC_ICMS"] += D(VL_BC_ICMS)
                x["VL_ICMS"] += D(VL_ICMS)
            #    ...     C420 - REGISTRO DOS TOTALIZADORES PARCIAIS DA REDUÇÃO Z
            cursor = conn.select("""SELECT *
                FROM fiscalinfo.ZTapeTotalizers
                WHERE PosId=%(posid)s AND FPSerialNo='%(serial)s' AND CRZ=%(CRZ)s
            """ % locals())
            regex_tax_index = re.compile("(\d\d)[TS]\d\d\d\d")
            for row in cursor:
                totalizer = row.get_entry("Totalizer")
                amount = D(row.get_entry("Amount")) / D("100")
                match = regex_tax_index.match(totalizer)
                index = ""
                if match:
                    index = match.group(1)
                lq['TC'] += 1
                lq['C420'] += 1
                report.write(records.RC420(
                    totalizer,              # Código do totalizador, conforme Tabela 4.4.6
                    amount,                 # Valor acumulado no totalizador, relativo à respectiva Redução Z.
                    index,                  # Número do totalizador quando ocorrer mais de uma situação com a mesma carga tributária efetiva.
                    ""                      # Descrição da situação tributária relativa ao totalizador parcial, quando houver mais de um com a mesma carga tributária efetiva.
                ))
                report.write("\r\n")
                match = regex_tax_rate.match(totalizer)
                if match:
                    # Add all ICMS totalizers to "C490" - start them with ZERO amount, but they will be incremented later
                    tax_rate = D(match.group(1)) / D("100")
                    add_C490(getCST_ICMS(totalizer), CFOP, tax_rate, "0", "0", "0")
                ''' NOTE - C425 must NOT be generated on "Perfil A" - only on "Perfil B" - REMOVE this later
                #    ...     C425 - RESUMO DE ITENS DO MOVIMENTO DIÁRIO
                cursor = conn.select("""
                SELECT
                    P.ProductCode AS ProductCode,
                    tdsum(OI.OrderedQty) AS Qty,
                    COALESCE(PKP.MeasureUnit,'UN') AS MeasureUnit,
                    tdmul(PR.DefaultUnitPrice,tdsum(OI.OrderedQty),2) AS TotalAmount
                FROM orderdb.OrderItem OI
                    JOIN fiscalinfo.FiscalOrderItems FOI ON FOI.OrderId=OI.OrderId AND FOI.LineNumber=OI.LineNumber AND FOI.ItemId=OI.ItemId AND FOI.Level=OI.Level AND FOI.PartCode=OI.PartCode
                    JOIN orderdb.Orders O ON OI.OrderId=O.OrderId
                    JOIN fiscalinfo.FiscalOrders FO ON OI.OrderId=FO.OrderId
                    JOIN productdb.Price PR ON PR.PriceKey=OI.PriceKey
                    JOIN productdb.Product P ON P.ProductCode=OI.PartCode
                    JOIN productdb.ProductKernelParams PKP ON PKP.ProductCode=P.ProductCode
                WHERE O.BusinessPeriod=%(period)s
                    AND O.OrderType=0
                    AND O.StateId=5
                    AND OI.Level=0
                    AND OI.OrderedQty>0
                    AND FO.FPSerialNo='%(serial)s'
                    AND FOI.TaxCode='%(totalizer)s'
                GROUP BY P.ProductCode
                """%locals())
                for row in cursor:
                    totalAmount = D(row.get_entry("TotalAmount"))
                    PIS = rate_pis/D("100") * totalAmount
                    COFINS = rate_cofins/D("100") * totalAmount
                    data = map(row.get_entry, (
                        "ProductCode",  # Código do item
                        "Qty",          # Quantidade acumulada do item
                        "MeasureUnit",  # Unidade do item
                        "TotalAmount",  # Valor acumulado do item
                    )) + [
                        PIS,            # Valor do PIS
                        COFINS,         # Valor da COFINS
                    ]
                    lq['TC']+=1
                    lq['C425']+=1
                    report.write(records.RC425(*data))
                    report.write("\r\n")
                '''
            #    ..     C460 - DOCUMENTO FISCAL EMITIDO POR ECF
            cursor = conn.select("""
            SELECT
                FO.OrderId,FO.COO,FO.FPDate,FO.TotalGross,FO.CustomerCPF,FO.CustomerName,
                CASE WHEN O.StateId=4 THEN 'S' ELSE 'N' END AS VoidIndicator
            FROM fiscalinfo.FiscalOrders FO
            JOIN orderdb.Orders O ON O.OrderId=FO.OrderId
            WHERE FO.PosId=%(posid)s
                AND FO.FPSerialNo='%(serial)s'
                AND FO.Period=%(period)s
                AND O.StateId IN (4,5)
            ORDER BY FPSerialNo,ECFModel,ECFUser,CCF
            """ % locals())
            for row in cursor:
                orderid = row.get_entry("OrderId")
                order_is_void = (row.get_entry("VoidIndicator") == "S")
                blank_void = lambda x: "" if order_is_void else x
                totalAmount = D(row.get_entry("TotalGross"))
                PIS = rate_pis / D("100") * totalAmount
                COFINS = rate_cofins / D("100") * totalAmount
                situacao = "02" if order_is_void else "00"
                lq['TC'] += 1
                lq['C460'] += 1
                report.write(records.RC460(
                    "2D",                                   # Código do modelo do documento fiscal, conforme a Tabela 4.1.1
                    situacao,                               # Código da situação do documento fiscal, conforme a Tabela 4.1.2
                    row.get_entry("COO"),                   # Número do documento fiscal (COO)
                    blank_void(row.get_entry("FPDate")),    # Data da emissão do documento fiscal
                    blank_void(totalAmount),                # Valor total do documento fiscal
                    blank_void(PIS),                        # Valor do PIS
                    blank_void(COFINS),                     # Valor da COFINS
                    blank_void(onlydigits(row.get_entry("CustomerCPF"))),   # CPF ou CNPJ do adquirente
                    blank_void(row.get_entry("CustomerName"))   # Nome do adquirente
                ))
                report.write("\r\n")
                #    ...     C470 - ITENS DO DOCUMENTO FISCAL EMITIDO POR ECF
                cursor = conn.select("""
                SELECT
                    FOI.PartCode AS ProductCode,
                    FOI.OrderedQty AS OrderedQty,
                    FOI.DecQty AS DecQty,
                    FOI.MeasureUnit AS MeasureUnit,
                    tdmul(FOI.UnitPrice,FOI.OrderedQty) AS Amount,
                    FOI.TaxCode AS TaxCode
                FROM fiscalinfo.FiscalOrderItems FOI
                JOIN orderdb.OrderItem OI ON FOI.OrderId=OI.OrderId AND FOI.LineNumber=OI.LineNumber AND FOI.ItemId=OI.ItemId AND FOI.Level=OI.Level AND FOI.PartCode=OI.PartCode
                WHERE FOI.OrderId=%(orderid)s
                ORDER BY FOI.LineNumber
                """ % locals())
                for row in cursor:
                    if float(row.get_entry("OrderedQty")) == 0.0:
                        # Ignore fully cancelled items
                        continue
                    match = regex_tax_rate.match(row.get_entry("TaxCode"))
                    tax_rate = D(match.group(1)) / D("100") if match else ZERO
                    totalAmount = D(row.get_entry("Amount"))
                    taxAmount = totalAmount * (tax_rate / D("100"))
                    if not order_is_void:
                        fileTotalTax += taxAmount
                    PIS = rate_pis / D("100") * totalAmount
                    COFINS = rate_cofins / D("100") * totalAmount
                    cst_icms = CST_ICMS if order_is_void else getCST_ICMS(row.get_entry("TaxCode"))
                    qty = D(row.get_entry("OrderedQty")) + D(row.get_entry("DecQty"))
                    lq['TC'] += 1
                    lq['C470'] += 1
                    report.write(records.RC470(
                        row.get_entry("ProductCode"),       # Código do item (campo 02 do Registro 0200)
                        qty,                                # Quantidade do item
                        row.get_entry("DecQty"),            # Quantidade cancelada, no caso de cancelamento parcial de item
                        row.get_entry("MeasureUnit"),       # Unidade do item (Campo 02 do registro 0190)
                        row.get_entry("Amount"),            # Valor do item
                        cst_icms,                           # Código da Situação Tributária, conforme a Tabela indicada no item 4.3.1.
                        CFOP,                               # Código Fiscal de Operação e Prestação
                        tax_rate,                           # Alíquota do ICMS - Carga tributária efetiva em percentual
                        PIS,                                # Valor do PIS
                        COFINS                              # Valor da COFINS
                    ))
                    report.write("\r\n")
                    # Consolidate this on C490
                    if not order_is_void:
                        add_C490(cst_icms, CFOP, str(tax_rate), totalAmount, totalAmount, taxAmount)
            for item in C490_consolidated.values():
                lq['TC'] += 1
                lq['C490'] += 1
                report.write(records.RC490(
                    item["CST_ICMS"],
                    item["CFOP"],
                    item["ALIQ_ICMS"],
                    item["VL_OPR"],
                    item["VL_BC_ICMS"],
                    item["VL_ICMS"],
                    ""
                ))
                report.write("\r\n")

        #    .    C990 - Encerra bloco C
        lq['C990'] += 1
        lq['TC'] += 1
        report.write(records.RC990(lq['TC']))
        report.write("\r\n")

        #    .    D001 - Abre bloco D
        lq['D001'] += 1
        lq['TD'] += 1
        report.write(records.RD001("1"))  # Bloco sem dados informados
        report.write("\r\n")
        #    .    D990 - Encerra bloco D
        lq['D990'] += 1
        lq['TD'] += 1
        report.write(records.RD990(lq['TD']))
        report.write("\r\n")

        #    .    E001 - Abre bloco E
        lq['E001'] += 1
        lq['TE'] += 1
        report.write(records.RE001("0"))  # Bloco com dados informados
        report.write("\r\n")
        lq['E100'] += 1
        lq['TE'] += 1
        report.write(records.RE100(period_begin, period_end))
        report.write("\r\n")

        lq['E110'] += 1
        lq['TE'] += 1
        report.write(records.RE110(
            fileTotalTax,
            "0", "0", "0", "0", "0", "0", "0", "0",
            fileTotalTax,
            "0",
            fileTotalTax,
            "0", "0"
        ))
        report.write("\r\n")
        lq['E116'] += 1
        lq['TE'] += 1
        report.write(records.RE116(
            "000",                      # Código da obrigação a recolher, conforme a Tabela 5.4
            fileTotalTax,               # Valor da obrigação a recolher
            time.strftime("%Y%m%d"),    # Data de vencimento da obrigação
            "0",                        # Código de receita referente à obrigação, próprio da unidade da federação, conforme legislação estadual
            "",                         # Número do processo ou auto de infração ao qual a obrigação está vinculada, se houver.
            "",                         # Indicador da origem do processo
            "",                         # Descrição resumida do processo que embasou o lançamento
            "",                         # Descrição complementar das obrigações a recolher
            time.strftime("%m%Y")       # Informe o mês de referência no formato “mmaaaa”
        ))
        report.write("\r\n")
        # |E116|000|3,30|01092011|0|||||082011|

        #    .    E990 - Encerra bloco E
        lq['E990'] += 1
        lq['TE'] += 1
        report.write(records.RE990(lq['TE']))
        report.write("\r\n")

        #    .    G001 - Abre bloco G
        lq['G001'] += 1
        lq['TG'] += 1
        report.write(records.RG001("1"))  # Bloco sem dados informados
        report.write("\r\n")
        #    .    G990 - Encerra bloco G
        lq['G990'] += 1
        lq['TG'] += 1
        report.write(records.RG990(lq['TG']))
        report.write("\r\n")

        #    .    H001 - Abre bloco H
        lq['H001'] += 1
        lq['TH'] += 1
        report.write(records.RH001(0))
        report.write("\r\n")
        cursor = conn.select('''
            SELECT
              COALESCE(tdsum(tdmul(Qty, ValorUnitario)),'0') as tot
            FROM
              fiscalinfo.Estoque
            WHERE tdcmp(Qty,'0')>0
           ''')
        val_inv = D(cursor.get_row(0).get_entry(0))
        cursor = conn.select('''
            SELECT
                tdsum(price.DefaultUnitPrice) as tot
            FROM
                Price
            JOIN taxcalc.ProductTaxCategory ProductTaxCategory
                ON ProductTaxCategory.ItemId=price.Context || "." || price.ProductCode
            JOIN taxcalc.TaxCategory TaxCategory
                ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN taxcalc.TaxRule TaxRule
                ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN Product Product
                ON price.ProductCode=Product.ProductCode
            JOIN productdb.ProductKernelParams PKP
                ON PKP.ProductCode=Product.ProductCode
            WHERE Product.ProductCode IN (SELECT ProductCode FROM Insumos) AND CURRENT_TIMESTAMP BETWEEN Price.ValidFrom AND Price.ValidThru
           ''')
        val_inv += D(cursor.get_row(0).get_entry(0))

        lq['H005'] += 1
        lq['TH'] += 1
        report.write(records.RH005(   # 01 -Texto fixo contendo "H005"
            period_end,    # 02 -Data do inventário
            val_inv   # 03 - Valor total do estoque
        ))
        report.write("\r\n")
        #    .    .    H010 - Inventário (diversos)                                 # ESTOQUE
        cursor = conn.select('''
            SELECT
              SKU AS productCode,
              Descr AS producName,
              "18.00" AS taxRule,
              Unidade AS measureUnit,
              CASE WHEN tdcmp(Qty,'0')<0 THEN '0' ELSE Qty END AS qty,
              ValorUnitario AS unitPrice
            FROM
              fiscalinfo.Estoque
            UNION ALL
            SELECT
                price.ProductCode AS productCode,
                Product.ProductName AS productName,
                tdScale(TaxRule.TaxRate,2,0) AS taxRule,
                PKP.MeasureUnit as measureUnit,
                1 as qty,
                price.DefaultUnitPrice as unitPrice
            FROM
                Price
            JOIN taxcalc.ProductTaxCategory ProductTaxCategory
                ON ProductTaxCategory.ItemId=price.Context || "." || price.ProductCode
            JOIN taxcalc.TaxCategory TaxCategory
                ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN taxcalc.TaxRule TaxRule
                ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
            JOIN Product
                ON price.ProductCode=Product.ProductCode
            JOIN productdb.ProductKernelParams PKP
                ON PKP.ProductCode=Product.ProductCode
            WHERE Product.ProductCode IN (SELECT ProductCode FROM Insumos) AND CURRENT_TIMESTAMP BETWEEN Price.ValidFrom AND Price.ValidThru
            GROUP BY productCode
            ORDER BY productCode
           ''')
        for row in cursor:
            productCode, qty, unitPrice, measureUnit = map(fromutf, map(row.get_entry, ("productCode", "qty", "unitPrice", "measureUnit")))
            valor = ("%.2f" % (D(qty) * D(unitPrice))).replace(".", ",")
            qty = ("%.3f" % (D(qty))).replace(".", ",")
            unitPrice = ("%.6f" % (D(unitPrice))).replace(".", ",")
            lq['H010'] += 1
            lq['TH'] += 1
            report.write(records.RH010(  # Inventário
                productCode,                    # 02 -Código do item (campo 02 do Registro 0200)
                measureUnit,                    # 03 -Unidade do item
                qty,                            # 04 -Quantidade do item (obs:3)
                unitPrice,                      # 05 -Valor unitário do item (obs:06)
                valor,                          # 06 -Valor do item (obs:02)
                "0",  # 0:proprio e em seu poder  # 07 -Indicador de propriedade/posso do item: [tabela abaixo]
                "",                             # 08 -Código do participante (campo 02 do Registro 0150)
                "",                             # 09 -Descrição complementar
                "0",                            # 10 -Código da conta analítica contábil debidata/creditada]
            ))
            report.write("\r\n")
        #    .    H990 - Encerra bloco H
        lq['H990'] += 1
        lq['TH'] += 1
        report.write(records.RH990(lq['TH']))  # 02 -Quantidade total de linhas do Bloco H
        report.write("\r\n")
        #    .    1001 - Abre bloco 1
        lq['1001'] += 1
        lq['T1'] += 1
        report.write(records.R1001("1"))  # Bloco com dados informados
        report.write("\r\n")
        #    .    C990 - Encerra bloco C
        lq['1990'] += 1
        lq['T1'] += 1
        report.write(records.R1990(lq['T1']))
        report.write("\r\n")

        #    .    9001 - Abre bloco 9
        lq['9001'] += 1
        lq['T9'] += 1
        report.write(records.R9001(0))  # 02 -Indicador de movimento: 0: Bloco com dados informados 1:Bloco sem dados informados
        report.write("\r\n")

        #    .    .    9900 - Totalizador de campos  (diversos)                     # Totalizador dos campos
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0000', lq['0000']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0001', lq['0001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0005', lq['0005']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0100', lq['0100']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0190', lq['0190']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0200', lq['0200']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('0990', lq['0990']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('C001', lq['C001']))
        report.write("\r\n")
        for recname in ('C350', 'C370', 'C390', 'C400', 'C405', 'C420', 'C425', 'C460', 'C470', 'C490'):
            if lq[recname] > 0:
                lq['9900'] += 1
                lq['T9'] += 1
                report.write(records.R9900(recname, lq[recname]))
                report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('C990', lq['C990']))
        report.write("\r\n")
        # Totalização bloco D
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('D001', lq['D001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('D990', lq['D990']))
        report.write("\r\n")
        # Totalização bloco E
        for recname in ('E001', 'E100', 'E110', 'E116', 'E990'):
            lq['9900'] += 1
            lq['T9'] += 1
            report.write(records.R9900(recname, lq[recname]))
            report.write("\r\n")
        # Totalização bloco G
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('G001', lq['G001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('G990', lq['G990']))
        report.write("\r\n")
        # Totalização bloco H
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('H001', lq['H001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('H005', lq['H005']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('H010', lq['H010']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('H990', lq['H990']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('1001', lq['1001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('1990', lq['1990']))
        report.write("\r\n")

        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('9001', lq['9001']))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('9900', lq['9900'] + 2))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('9990', "1"))
        report.write("\r\n")
        lq['9900'] += 1
        lq['T9'] += 1
        report.write(records.R9900('9999', "1"))
        report.write("\r\n")
        #    .    9990 - Encerra bloco 9
        lq['9990'] += 1
        lq['T9'] += 1
        report.write(records.R9990(lq['T9'] + 1))  # 02 -Quantidade total de linhas do Bloco 9
        report.write("\r\n")
        #    9999 - Fechamento do arquivo
        lq['9999'] += 1
        report.write(records.R9999(lq['T0'] + lq['T1'] + lq['TC'] + lq['TD'] + lq['TE'] + lq['TG'] + lq['TH'] + lq['T9'] + 2))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[paf_sped] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def estoque(posid, period, *args):
    report = Report()
    ascii = Report().ascii
    reportPath = readEncrypted(posid, "FiscalOutputPath")
    if not reportPath:
        reportPath = "./"

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))
        cursor = conn.select('''
            SELECT
              SKU AS productCode,
              Descr AS producName,
              Unidade AS measureUnit,
              Qty AS qty
            FROM
              fiscalinfo.Estoque
           ''')
        report.write("                    TABELA DE ESTOQUE\r\n")
        report.write("Código         Descrição                         Un. Quantidade\r\n")
        report.write("-------------- --------------------------------- --- ----------\r\n")
        for row in cursor:
            productCode, productName, measureUnit, qty = map(row.get_entry, ("productCode", "producName", "measureUnit", "qty"))
            report.write("%14.14s %-33.33s %2s  %10.10s\r\n" % (productCode, ascii(productName), measureUnit, qty))
    except Exception as e:
        sys_log_exception('[estoque] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def paf_envio_fisco_reducao_z(posid, period, *args):
    report = Report()

    # Numero do Credenciamento
    paf_numero_credenciamento = PAF_ECF.get_paf_cert_number()

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # set the period
        companyName, federalRegister, stateRegister, DEV_FederalRegister, DEV_CompanyName, SW_Name, serial = readEncrypted(posid, "User_CompanyName", "User_FederalRegister", "User_StateRegister", "DEV_FederalRegister", "DEV_CompanyName", "SW_Name", "ECF_Serial")
        reducao_z = etree.Element("ReducaoZ", Versao="1.0")
        mensagem = etree.SubElement(reducao_z, "Mensagem")

        # Estabelecimento
        estabelecimento = etree.SubElement(mensagem, "Estabelecimento")
        pafecf = etree.SubElement(mensagem, "PafEcf")
        ecf = etree.SubElement(mensagem, "Ecf")
        ie = etree.SubElement(estabelecimento, "Ie")
        cnpj = etree.SubElement(estabelecimento, "Cnpj")
        nome_empresarial = etree.SubElement(estabelecimento, "NomeEmpresarial")

        ie.text = stateRegister
        cnpj.text = federalRegister
        nome_empresarial.text = companyName

        # PafEcf
        numero_credenciamento = etree.SubElement(pafecf, "NumeroCredenciamento")
        nome_comercial = etree.SubElement(pafecf, "NomeComercial")
        paf_versao = etree.SubElement(pafecf, "Versao")
        cnpj_desenvolvedor = etree.SubElement(pafecf, "CnpjDesenvolvedor")
        nome_empresarial_desenvolvedor = etree.SubElement(pafecf, "NomeEmpresarialDesenvolvedor")

        numero_credenciamento.text = paf_numero_credenciamento
        nome_comercial.text = SW_Name
        paf_versao.text = PAF_ECF.get_software_version()
        cnpj_desenvolvedor.text = DEV_FederalRegister
        nome_empresarial_desenvolvedor.text = DEV_CompanyName

        # Ecf
        numero_credenciamento_ecf = etree.SubElement(ecf, "NumeroCredenciamento")
        numero_fabricacao = etree.SubElement(ecf, "NumeroFabricacao")
        tipo = etree.SubElement(ecf, "Tipo")
        marca = etree.SubElement(ecf, "Marca")
        modelo = etree.SubElement(ecf, "Modelo")
        ecf_versao = etree.SubElement(ecf, "Versao")
        caixa = etree.SubElement(ecf, "Caixa")
        dados_reducao_z = etree.SubElement(ecf, "DadosReducaoZ")

        cursor = conn.select("""
                    SELECT
                        FP.*,
                        CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
                    FROM fiscalinfo.FiscalPrinters FP
                    LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalPrinters' AND D.R=FP._ROWID_
                        AND D.C IN ('FPSerialNo','ECFType','ECFBrand','ECFModel','ECFSwVersion','ECFPosId','FPBusinessDate')
                    WHERE FP.PosId=%(posid)s AND FP.FPSerialNo='%(serial)s'
                    GROUP BY FP._ROWID_
                    """ % locals())
        row = cursor.get_row(0)
        if row:
            # Ecf Data
            numero_credenciamento_ecf.text = paf_numero_credenciamento
            numero_fabricacao.text = row.get_entry("FPSerialNo")
            tipo.text = row.get_entry("ECFType")
            marca.text = row.get_entry("ECFBrand")
            modelo.text = row.get_entry("ECFModel")
            ecf_versao.text = row.get_entry("ECFSwVersion")
            caixa.text = row.get_entry("ECFPosId")

        # Dados Redução Z
        data_referencia = etree.SubElement(dados_reducao_z, "DataReferencia")
        crz = etree.SubElement(dados_reducao_z, "CRZ")
        coo = etree.SubElement(dados_reducao_z, "COO")
        cro = etree.SubElement(dados_reducao_z, "CRO")
        venda_bruta_diaria = etree.SubElement(dados_reducao_z, "VendaBrutaDiaria")
        gt = etree.SubElement(dados_reducao_z, "GT")

        cursor = conn.select("""
                SELECT
                    Z.*,
                    CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
                FROM fiscalinfo.ZTapes Z
                LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='ZTapes' AND D.R=Z._ROWID_
                    AND D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CRZ','LastCOO','CRO','FPBusinessDate','FPDate','FPTime','DGT','GT')
                WHERE Z.PosId=%(posid)s AND Z.FPSerialNo='%(serial)s' AND Z.Period = '%(period)s'
                GROUP BY Z._ROWID_
                ORDER BY Z.FPSerialNo,Z.ECFModel,Z.ECFUser,Z.CRZ,Z.CRO
            """ % locals())
        for row in cursor:
            # Dados Reducao Z Data
            data_ref = row.get_entry("FPBusinessDate")
            data_referencia.text = data_ref[:4] + '-' + data_ref[4:6] + '-' + data_ref[6:]
            crz.text = row.get_entry("CRZ").zfill(4)
            coo.text = row.get_entry("LastCOO").zfill(9)
            cro.text = row.get_entry("CRO").zfill(3)
            venda_bruta_diaria.text = row.get_entry("DGT").replace('.', '').zfill(14)
            gt.text = row.get_entry("GT").replace('.', '').zfill(18)

        # Totalizadores Parciais
        totalizadores_parciais = etree.SubElement(dados_reducao_z, "TotalizadoresParciais")
        cursor = conn.select("""
                    SELECT
                        ZT.*,
                        CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
                    FROM fiscalinfo.ZTapeTotalizers ZT
                    LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='ZTapeTotalizers' AND D.R=ZT._ROWID_
                        AND D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CRZ','Totalizer','Amount')
                    WHERE ZT.PosId=%(posid)s AND ZT.FPSerialNo='%(serial)s' AND ZT.Period = '%(period)s'
                    GROUP BY ZT._ROWID_
                    ORDER BY ZT.FPSerialNo,ZT.ECFModel,ZT.ECFUser,ZT.CRZ,ZT.Totalizer
                """ % locals())
        for row in cursor:
            if float(row.get_entry("Amount") or 0) == 0:
                continue
            # Totalizadores Parciais Data
            totalizador_parcial = etree.SubElement(totalizadores_parciais, "TotalizadorParcial")
            nome = etree.SubElement(totalizador_parcial, "Nome")
            valor = etree.SubElement(totalizador_parcial, "Valor")

            nome.text = row.get_entry("Totalizer")
            valor.text = ("%.2f" % float(row.get_entry("Amount") or 0)).replace('.', ',')

            # Produtos Servicos
            produtos_servicos = etree.SubElement(totalizador_parcial, "ProdutosServicos")
            cursor2 = conn.select("""
                SELECT
                    F.FPSerialNo AS FPSerialNo,
                    F.AdditionalMem AS AdditionalMem,
                    F.ECFModel AS ECFModel,
                    F.ECFUser AS ECFUser,
                    F.CCF AS CCF,
                    F.COO AS COO,
                    FOI.LineNumber AS LineNumber,
                    FOI.PartCode AS ProductCode,
                    FOI.ProductName AS ProductName,
                    COUNT(FOI.OrderedQty) AS TotalQty,
                    FOI.MeasureUnit AS MeasureUnit,
                    FOI.UnitPrice AS UnitPrice,
                    FOI.DiscountAmount AS DiscountAmount,
                    tdsub(tdmul(FOI.OrderedQty,FOI.UnitPrice),FOI.DiscountAmount) AS TotalAmount,
                    FOI.TaxCode AS TaxCode,
                    FOI.VoidIndicator AS VoidIndicator,
                    CASE WHEN FOI.VoidIndicator='P' THEN tdscale(FOI.DecQty,3,1) ELSE 0 END AS VoidQty, --7.5.1.4 - Campo 19 - Informar a quantidade cancelada somente quando ocorrer o cancelamento parcial do item
                    CASE WHEN FOI.VoidIndicator='P' THEN tdmul(FOI.DecQty,FOI.UnitPrice) ELSE 0 END AS VoidAmount, --7.5.1.5 - Campo 20 - Informar o valor cancelado somente quando ocorrer o cancelamento parcial do item
                    FOI.IAT AS IAT,
                    FOI.IPPT AS IPPT,
                    COUNT(FOI.OrderedQty) AS OrderedQty,
                    CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered,
                    CASE WHEN D2.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered2
                FROM fiscalinfo.FiscalOrderItems FOI
                JOIN fiscalinfo.FiscalOrders F ON F.OrderId=FOI.OrderId
                LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalOrderItems' AND D.R=FOI._ROWID_
                    AND D.C IN ('LineNumber','PartCode','ProductName','OrderedQty','DecQty','MeasureUnit','UnitPrice','DiscountAmount','TaxCode','VoidIndicator','IAT','IPPT')
                LEFT JOIN  fiscalinfo.FiscalD D2 ON D2.TB='FiscalOrders' AND D2.R=F._ROWID_
                    AND D2.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CCF','COO')
                WHERE F.PosId=%(posid)s
                    AND F.FPSerialNo='%(serial)s'
                    AND F.Period = '%(period)s'
                GROUP BY FOI.PartCode
                ORDER BY F.FPSerialNo,F.ECFModel,F.ECFUser,F.CCF,FOI.LineNumber
                """ % locals())

            for row2 in cursor2:
                taxcode = row2.get_entry("TaxCode")
                if taxcode == "FF":
                    taxcode = "F1"
                elif taxcode == "II":
                    taxcode = "I1"
                elif taxcode == "NN":
                    taxcode = "N1"

                if taxcode == nome.text:
                    # Produto
                    produto = etree.SubElement(produtos_servicos, "Produto")
                    descricao = etree.SubElement(produto, "Descricao")
                    codigo = etree.SubElement(produto, "Codigo")
                    codigo_tipo = etree.SubElement(produto, "CodigoTipo")
                    quantidade = etree.SubElement(produto, "Quantidade")
                    unidade = etree.SubElement(produto, "Unidade")
                    valor_unitario = etree.SubElement(produto, "ValorUnitario")

                    descricao.text = row2.get_entry("ProductName")
                    codigo.text = row2.get_entry("ProductCode")
                    codigo_tipo.text = "Proprio"
                    quantidade.text = ("%.2f" % float(row2.get_entry("TotalQty") or 0)).replace('.', ',')
                    unidade.text = row2.get_entry("MeasureUnit")
                    valor_unitario.text = ("%.2f" % float(row2.get_entry("UnitPrice") or 0)).replace('.', ',')
            # Query2 produtos/servicos

        assinado = ""
        reduz_not_signed = ""
        try:
            reduz_not_signed = etree.tostring(reducao_z)
            assinado = assina_xml(reduz_not_signed)
        except:
            if not assinado or assinado is None:
                assinado = reduz_not_signed
        finally:
            report.write("""<?xml version="1.0" encoding="utf-8"?>""" + etree.tostring(assinado))
    except Exception as e:
        sys_log_exception('[paf_envio_fisco_reducao_z] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()

    assinado = ""
    reduz_not_signed = ""
    try:
        reduz_not_signed = etree.tostring(reducao_z)
        assinado = assina_xml(reduz_not_signed)
    except:
        if not assinado or assinado is None:
            assinado = reduz_not_signed
    finally:
        report.write("""<?xml version="1.0" encoding="utf-8"?>""" + etree.tostring(assinado))

    return report.getvalue()


def paf_envio_fisco_estoque(posid, data_inicial, data_final, *args):
    report = Report()

    # Numero do Credenciamento
    paf_numero_credenciamento = PAF_ECF.get_paf_cert_number()

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # set the period
        companyName, federalRegister, stateRegister, DEV_FederalRegister, DEV_CompanyName, SW_Name, serial, = readEncrypted(posid, "User_CompanyName", "User_FederalRegister", "User_StateRegister", "DEV_FederalRegister", "DEV_CompanyName", "SW_Name", "ECF_Serial")

        estoque = etree.Element("Estoque", Versao="1.0")
        mensagem = etree.SubElement(estoque, "Mensagem")

        # Estabelecimento
        estabelecimento = etree.SubElement(mensagem, "Estabelecimento")
        pafecf = etree.SubElement(mensagem, "PafEcf")
        dados_estoque = etree.SubElement(mensagem, "DadosEstoque")
        ie = etree.SubElement(estabelecimento, "Ie")
        cnpj = etree.SubElement(estabelecimento, "Cnpj")
        nome_empresarial = etree.SubElement(estabelecimento, "NomeEmpresarial")

        ie.text = stateRegister
        cnpj.text = federalRegister
        nome_empresarial.text = companyName

        # PafEcf
        numero_credenciamento = etree.SubElement(pafecf, "NumeroCredenciamento")
        nome_comercial = etree.SubElement(pafecf, "NomeComercial")
        paf_versao = etree.SubElement(pafecf, "Versao")
        cnpj_desenvolvedor = etree.SubElement(pafecf, "CnpjDesenvolvedor")
        nome_empresarial_desenvolvedor = etree.SubElement(pafecf, "NomeEmpresarialDesenvolvedor")

        numero_credenciamento.text = paf_numero_credenciamento
        nome_comercial.text = SW_Name
        paf_versao.text = PAF_ECF.get_software_version()
        cnpj_desenvolvedor.text = DEV_FederalRegister
        nome_empresarial_desenvolvedor.text = DEV_CompanyName

        # Dados Estoque
        data_referencia_inicial = etree.SubElement(dados_estoque, "DataReferenciaInicial")
        data_referencia_final = etree.SubElement(dados_estoque, "DataReferenciaFinal")
        produtos = etree.SubElement(dados_estoque, "Produtos")

        data_referencia_inicial.text = data_inicial
        data_referencia_final.text = data_final
        data_inicial = data_inicial.replace('-','')
        data_final = data_final.replace('-','')

        def getISSQN_ICMS(taxCode):
            # Implementar codigos corretos e retornos corretos
            if taxCode[0] == "N":
                return "Nao tributado"  # Nao tributado
            if taxCode[0] == "F":
                return "Substituicao tributaria"  # Substituicao tributaria
            if taxCode[0] == "I":
                return "Isento"  # Isento
            if taxCode.isdigit():  # Tributado pelo ICMS
                return "Tributado pelo ICMS"
            return "Tributado pelo ISSQN"  # Tributado pelo ISSQN

        cursor = conn.select("""
                    SELECT
                        P.ProductName AS ProductName,
                        P.ProductCode AS ProductCode,
                        P.UnitPrice AS UnitPrice,
                        P.TaxFiscalIndex AS TaxCode,
                        P.TaxRate AS TaxRate,
                        P.IAT AS IAT,
                        P.IPPT AS IPPT,
                        P.MeasureUnit as MeasureUnit,
                        COALESCE(E.Qty, 0) AS TotalQty
                    FROM fiscalinfo.FiscalProductDB P
                    LEFT JOIN fiscalinfo.Estoque E ON P.ProductCode = E.SKU""")
        for row in cursor:
            # Produtos
            produto = etree.SubElement(produtos, "Produto")
            descricao = etree.SubElement(produto, "Descricao")
            codigo = etree.SubElement(produto, "Codigo")
            codigo_tipo = etree.SubElement(produto, "CodigoTipo")
            quantidade = etree.SubElement(produto, "Quantidade")
            unidade = etree.SubElement(produto, "Unidade")
            valor_unitario = etree.SubElement(produto, "ValorUnitario")
            situacao_tributaria = etree.SubElement(produto, "SituacaoTributaria")
            aliquota = etree.SubElement(produto, "Aliquota")
            is_arredondado = etree.SubElement(produto, "IsArredondado")
            ippt = etree.SubElement(produto, "Ippt")
            situacao_estoque = etree.SubElement(produto, "SituacaoEstoque")

            descricao.text = row.get_entry("ProductName")
            codigo.text = row.get_entry("ProductCode")
            codigo_tipo.text = "Proprio"
            quantidade.text = ("%.3f" % float(row.get_entry("TotalQty") or 0)).replace('.', ',')
            unidade.text = row.get_entry("MeasureUnit")
            valor_unitario.text = ("%.2f" % float(row.get_entry("UnitPrice") or 0)).replace('.', ',')
            situacao_tributaria.text = getISSQN_ICMS(row.get_entry("TaxCode"))
            aliquota.text = ("%.2f" % float(row.get_entry("TaxRate") or 0)).replace('.', ',')
            is_arredondado.text = str(row.get_entry("IAT") == 'T').lower()
            ippt.text = "Proprio" if row.get_entry("IPPT") == 'P' else "Terceiros"
            situacao_estoque.text = "Positivo" if float(row.get_entry("TotalQty")) > 0 else "Negativo"

        assinado = ""
        estoque_not_signed = ""
        try:
            estoque_not_signed = etree.tostring(estoque)
            assinado = assina_xml(estoque_not_signed)
        except:
            if not assinado or assinado is None:
                assinado = estoque_not_signed
        finally:
            report.write("""<?xml version="1.0" encoding="utf-8"?>""" + etree.tostring(assinado))
    except Exception as e:
        sys_log_exception('[paf_envio_fisco_estoque] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def assina_xml(request):
    # type: (str) -> ElementTree.Element
    from lxml import etree as lTree
    root = lTree.XML(request)
    certificate_key = open("certificate/cert.key", "rb").read().replace("\r\n", "\n")
    certificate_cert = open("certificate/cert.pem", "rb").read().replace("\r\n", "\n")
    signed_root = XMLSigner(
        method=signxml.methods.enveloped, signature_algorithm=u'rsa-sha1', digest_algorithm=u'sha1',
        c14n_algorithm=u'http://www.w3.org/TR/2001/REC-xml-c14n-20010315').sign(
        root, key=certificate_key, cert=certificate_cert)#, reference_uri=nfe_id)
    return signed_root

def merchandiseReport(posid, period, *args):
    '''
    Ajuda em: http://www.fazenda.gov.br/confaz/confaz/Atos/Atos_Cotepe/2008/AC006_08.htm

    ANEXO V - Tabela de Mercadorias e Serviços

    6 - MONTAGEM DO ARQUIVO ELETRÔNICO:
    +------------------+------------------------------------+-----------------------------------------+--------+
    | Tipo de Registro | Nome do Registro                   | Denominação dos Campos de Classificação | A/D*   |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | P1               | Identificação do estabelecimento   | 1º registro (único)                     | ------ |
    |                  | usuário do PAF-ECF                 |                                         |        |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | P2               | Relação das mercadorias e serviços | Código da mercadoria ou serviço         | A      |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | P9               | Totalização de registros           | Penúltimo registro (único)              | ------ |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | EAD              | Assinatura digital                 | Último registro (único)                 | ------ |
    +------------------+------------------------------------+-----------------------------------------+--------+
    * A indicação "A/D" significa ascendente/descendente


    7.1 Registro Tipo P1 - identificação estabelecimento usuário do PAF-ECF
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteudo                | Tamanho | Posicao   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo de registro     | "P1"                    | 02      |   1 |   3 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ                 | CNPJ do estabelecimento | 14      |   3 |  16 |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 |Inscrição Estadual    | Inscrição Estadual do   | 14      |  17 |  30 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 |Inscrição Municipal   | Inscrição Municial do   | 14      |  31 |  44 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 05 |Razao Social do       | Razao Social do         | 50      |  45 |  94 |    X    |
    |    |estabelecimento       | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

    7.2 - REGISTRO TIPO P2 - RELAÇÃO DE MERCADORIAS E SERVIÇOS:
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo de registro     | "P2"                    | 02      |   1 |   2 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ                 | CNPJ do estabelecimento | 14      |   3 | 16  |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 | Código               | Código da mercadoria    | 14      |  17 |  30 |    X    |
    |    |                      | ou serviço              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 | Descrição            | Descrição da mercadoria | 50      |  31 |  80 |    X    |
    |    |                      | ou serviço              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 05 | Unidade              | Unidade de medida       | 06      |  81 |  86 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 06 | IAT        [7.2.1.3] | Indicador de Arredonda- | 01      |  87 |  87 |    X    |
    |    |                      | mento ou Truncamento    |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 07 | IPPT       [7.2.1.4] | Indicador de Produção   | 01      |  88 |  88 |    X    |
    |    |                      | Própria ou de Terceiro  |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 08 | Situação Tributária  | Código da Situação      | 01      |  89 |  89 |    X    |
    |    |            [7.2.1.5] | Tributaria              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 09 | Alíquota             | Alíquota                | 04      | 90  |  93 |    N    |
    |    |            [7.2.1.6] | Tributaria              |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 10 | Valor unitário       | Valor unitário com duas | 12      |  94 | 105 |    N    |
    |    |                      | casas decimais          |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

    +--------+--------------------------------+
    | Código | Situação Tributária [7.2.1.5]  |
    +--------+--------------------------------+
    |   I    | Isento                         |
    +--------+--------------------------------+
    |   N    | Não Tributado                  |
    +--------+--------------------------------+
    |   F    | Substituição Tributária        |
    +--------+--------------------------------+
    |   T    | Tributado pelo ICMS            |
    +--------+--------------------------------+
    |   S    | Tributado pelo ISSQN           |
    +--------+--------------------------------+


    7.3. REGISTRO TIPO P9 - TOTALIZAÇÃO DO ARQUIVO
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo                 | "P9"                    | 02      |  01 |  02 |    N  |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | CNPJ/MF              | CNPJ do estabelecimento | 14      |  03 |  16 |    N    |
    |    |                      | usuário do PAF-ECF      |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 03 | Inscrição Estadual   | Inscrição Estadual do   | 14      |  17 |  30 |    X    |
    |    |                      | estabelecimento         |         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 04 | Total de registros   | Qtd de registros tipo   | 06      |  31 |  36 |    N    |
    |    | tipo P2              | P2 informados no arquivo|         |     |     |         |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

     7.4 - REGISTRO TIPO EAD - ASSINATURA DIGITAL
    +----+----------------------+-------------------------+---------+-----------+---------+
    | Nº | Denominação do Campo | Conteúdo                | Tamanho | Posição   | Formato |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 01 | Tipo do registro     | "EAD"                   | 03      |  01 |  03 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+
    | 02 | Assinatura Digital   | Assinatura do Hash      | 256     |  04 | 259 |    X    |
    +----+----------------------+-------------------------+---------+-----+-----+---------+

    '''
    report = Report()
    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))
        # get the data
        cursor = conn.select(
            '''
            SELECT
                ProductCode as ProductCode, ProductName, UnitPrice, TaxFiscalIndex, FiscalCategory, TaxRate, IAT, IPPT,
                MeasureUnit, CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
            FROM fiscalinfo.FiscalProductDB DB
            LEFT JOIN fiscalinfo.FiscalD D ON D.TB='FiscalProductDB' AND D.R=DB._ROWID_ AND (D.OP='A' OR
                D.C IN ('ProductCode', 'ProductName', 'UnitPrice', 'TaxFiscalIndex', 'FiscalCategory', 'TaxRate', 'IAT',
                'IPPT', 'MeasureUnit'))
            GROUP BY DB._ROWID_
        ''')
        P2_qty = 0

        report.write("%s %s %s %s %s %s %s %s %s %s" % (
            "Cod".ljust(7).lstrip()[:7],
            "CEST".ljust(7).lstrip()[:7],
            "NCM".ljust(8).lstrip()[:8],
            "Produto".ljust(15).lstrip()[:15],
            "U.M".ljust(3).lstrip()[:3],
            "Preço".ljust(8).lstrip()[:8],
            "ST".ljust(1).lstrip(),
            "IAT".ljust(1).lstrip(),
            "IPPT".ljust(1).lstrip(),
            "ALI".ljust(4).lstrip(),
        ))
        report.write("\r\n")
        for row in cursor:
            fiscalCategory, fiscalIndex, productCode, productName, taxRate, unitPrice, measureUnit, IAT, IPPT = map(
                row.get_entry, ("FiscalCategory", "TaxFiscalIndex", "ProductCode", "ProductName", "TaxRate", "UnitPrice",
                                "MeasureUnit", "IAT", "IPPT"))
            if fiscalIndex and fiscalIndex[0] in ("I", "N", "F"):
                fcI = fiscalIndex[0]  # ICMS
            elif fiscalIndex and fiscalIndex[:2] in ("SI", "SN", "SF"):
                fcI = fiscalIndex[1]  # ISS
            elif fiscalCategory and "ICMS" in fiscalCategory:
                fcI = "T"  # Tributado pelo ICMS
            elif fiscalCategory and "ISS" in fiscalCategory:
                fcI = "S"  # Tributado pelo ISSQN
            else:
                # This should never happen, but...
                fcI = "N"  # Não Tributado
            if int(row.get_entry("Tampered")):
                # This record was tampered!
                measureUnit = "%-6.6s" % (measureUnit)
                measureUnit = measureUnit.replace(" ", "?")

            cursor_tags = conn.select("""SELECT TAG FROM producttags WHERE productCode = '{0}' AND
                tag LIKE '%NCM=%' OR productCode = '{0}' AND tag LIKE '%cest=%' """.format(productCode))

            cest, ncm = 0, 0

            for tag in cursor_tags:
                obj_tag = tag.get_entry(0).split('=') if tag.get_entry(0) else ['']
                if "NCM" == str(obj_tag[0]).upper():
                    ncm = obj_tag[1]
                elif "CEST" == str(obj_tag[0]).upper():
                    cest = obj_tag[1]

            if unitPrice:
                report.write("%s %s %s %s %s %s %s %s %s %s" % (
                    str(productCode).ljust(7).lstrip()[:7],
                    str(cest).ljust(7).lstrip()[:7],
                    str(ncm).ljust(8).lstrip()[:8],
                    str(productName).ljust(15).lstrip()[:15],
                    str(measureUnit).ljust(3).lstrip()[:3],
                    str('{:,.2f}'.format(float(unitPrice))).ljust(8).lstrip()[:8],
                    str(fcI).ljust(2).lstrip(),
                    str(IAT).ljust(2).lstrip(),
                    str(IPPT).ljust(3).lstrip(),
                    str("{0}%".format(float(taxRate or 0))).ljust(4).lstrip(),
                ))
                report.write("\r\n")
                P2_qty += 1
    except Exception as e:
        sys_log_exception('[merchandiseReport] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()

def pafEcfTableReport(posid, period_begin, period_end, *args):
    report = Report()
    try:
        companyName, federalRegister, stateRegister, municipalRegister = readEncrypted(posid, "User_CompanyName", "User_FederalRegister", "User_StateRegister", "User_MunicipalRegister")
    except:
        companyName, federalRegister, stateRegister, municipalRegister = ("BK BRASIL OPERACAO E ASSESSORIA A RESTAURANTES S/A", 11111111111111, "222222222", "333333333")

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period_begin, period_end))

        # detect manually deleted/added records
        cursor = conn.select('''
        SELECT * FROM fiscalinfo.FiscalD WHERE OP IN ('A','D')
        ''')
        tampered = (cursor.rows() > 0)

        if tampered:
            companyName = "%-50.50s" % companyName
            companyName = companyName.replace(" ", "?")
        report.write(records.U1(
            federalRegister,
            stateRegister,
            municipalRegister,
            companyName
        ))
        report.write("\r\n")

        report.write(meiosDePagamento(posid, period_begin, period_end, *args))


        # get the data
        cursor = conn.select(
            '''
        SELECT
            ProductCode,ProductName,UnitPrice,TaxFiscalIndex,FiscalCategory,TaxRate,IAT,IPPT,MeasureUnit,
            CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
        FROM fiscalinfo.FiscalProductDB DB
        LEFT JOIN fiscalinfo.FiscalD D ON D.TB='FiscalProductDB' AND D.R=DB._ROWID_ AND (D.OP='A' OR
            D.C IN ('ProductCode','ProductName','UnitPrice','TaxFiscalIndex','FiscalCategory','TaxRate','IAT','IPPT','MeasureUnit'))
        GROUP BY DB._ROWID_
        ''')
        P2_qty = 0
        for row in cursor:
            fiscalCategory, fiscalIndex, productCode, productName, taxRate, unitPrice, measureUnit, IAT, IPPT = map(row.get_entry, ("FiscalCategory", "TaxFiscalIndex", "ProductCode", "ProductName", "TaxRate", "UnitPrice", "MeasureUnit", "IAT", "IPPT"))
            if fiscalIndex and fiscalIndex[0] in ("I", "N", "F"):
                fcI = fiscalIndex[0]  # ICMS
            elif fiscalIndex and fiscalIndex[:2] in ("SI", "SN", "SF"):
                fcI = fiscalIndex[1]  # ISS
            elif fiscalCategory and "ICMS" in fiscalCategory:
                fcI = "T"  # Tributado pelo ICMS
            elif fiscalCategory and "ISS" in fiscalCategory:
                fcI = "S"  # Tributado pelo ISSQN
            else:
                # This should never happen, but...
                fcI = "N"  # Não Tributado
            if int(row.get_entry("Tampered")):
                # This record was tampered!
                measureUnit = "%-6.6s" % (measureUnit)
                measureUnit = measureUnit.replace(" ", "?")
            report.write(records.P2(
                federalRegister,
                productCode,
                productName,
                measureUnit,
                IAT,
                IPPT,
                fcI,
                taxRate or 0,
                unitPrice or 0
            ))
            report.write("\r\n")
            P2_qty += 1
    except Exception as e:
        sys_log_exception('[pafEcfTableReport] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()

def ordersCpfCnpjReport(posid, period, cpf_cnpj, *args):
    report = Report()
    try:
        companyName, federalRegister, stateRegister, municipalRegister = readEncrypted(posid, "User_CompanyName", "User_FederalRegister", "User_StateRegister", "User_MunicipalRegister")
    except:
        companyName, federalRegister, stateRegister, municipalRegister = ("BK BRASIL OPERACAO E ASSESSORIA A RESTAURANTES S/A", 11111111111111, "222222222", "333333333")
    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()

        period = period.split('-')
        month_range = calendar.monthrange(int(period[1]), int(period[0]))
        date_ini = "%s%s%s" % (period[1], period[0], '01')
        date_end = "%s%s%s" % (period[1], period[0], month_range[1])

        date_now = datetime.datetime.now()
        qtd_lines = 0

        conditional = ''

        if len(cpf_cnpj) > 0:
            #conditional = "and CustomerCPF = '{0}'".format(cpf_cnpj)
            conditional = "and CustomerCPF = '%s' " % (cpf_cnpj)
        else:
            conditional = "and CustomerCPF <> '' group by CustomerCPF"

        # get the data
        cursor = conn.select("""select CustomerCPF, sum(TotalGross) as Total from fiscalinfo.FiscalOrders where Period between '%s' and '%s' %s """ % (date_ini, date_end, conditional))

        try:
            PAF_CertNumber, DEV_FederalRegister, DEV_CompanyName, SW_Name, DEV_StateRegister, DEV_MunicipalRegister = readEncrypted(
                posid, "PAF_CertNumber", "DEV_FederalRegister", "DEV_CompanyName", "SW_Name", "DEV_StateRegister", "DEV_MunicipalRegister")
        except:
            PAF_CertNumber, DEV_FederalRegister, DEV_CompanyName, SW_Name, DEV_StateRegister, DEV_MunicipalRegister = ("INA0022017", 9203932000106, "NewUpdate Sistemas de Informatica Ltda.", "MW:POS", "147283055113", "")
        SW_Version = PAF_ECF.get_software_version()

        report.write(records.Z1(federalRegister, stateRegister, municipalRegister, companyName))
        report.write("\r\n")

        report.write(records.Z2(DEV_FederalRegister, DEV_StateRegister, DEV_MunicipalRegister, DEV_CompanyName))
        report.write("\r\n")

        report.write(records.Z3(PAF_CertNumber, SW_Name, SW_Version))
        report.write("\r\n")

        for row in cursor:
            total, customerCPF = map(row.get_entry, ("Total", "CustomerCPF"))

            if total and customerCPF:
                total_gross = "%.2f" % D(total or 0)
                total_gross = total_gross.replace(".", "")

                report.write(records.Z4(customerCPF or 0,
                                        total_gross,
                                        date_ini,
                                        date_end,
                                        date_now.strftime('%Y%m%d'),
                                        date_now.strftime('%H%M%S'))
                )
                report.write("\r\n")
                qtd_lines = qtd_lines + 1

        report.write(records.Z9(DEV_FederalRegister, DEV_StateRegister, qtd_lines))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[ordersCpfCnpjReport] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()

def productListReport(posid, period, *args):
    report = Report()
    reportPath = readEncrypted(posid, "FiscalOutputPath")
    if not reportPath:
        reportPath = "./"

    # opens the database connection
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # reserve the database connection
        conn.transaction_start()
        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))

        # get the data
        cursor = conn.select(
            '''SELECT
            Price.Context || "." || Price.ProductCode  AS ProductId,
            Price.Context,
            Price.DefaultUnitPrice as UnitPrice,
            Price.ProductCode AS ProductCode,
            Product.ProductName AS ProductName,
            TaxCategory.TaxCgyDescr AS FiscalCategory,
            tdScale(TaxRule.TaxRate,2,0) AS TaxRule,
            COALESCE(IAT.CustomParamValue, 'T') AS IAT,
            COALESCE(IPPT.CustomParamValue, 'P') AS IPPT,
            COALESCE(PKP.MeasureUnit,'UN') as MeasureUnit
        FROM
            productdb.Price Price
        JOIN taxcalc.ProductTaxCategory ProductTaxCategory
            ON ProductTaxCategory.ItemId=ProductId
        JOIN taxcalc.TaxCategory TaxCategory
            ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
        JOIN taxcalc.TaxRule TaxRule
            ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
        JOIN productdb.Product Product
            ON Price.ProductCode=Product.ProductCode
        JOIN productdb.ProductKernelParams PKP
            ON PKP.ProductCode=Product.ProductCode
        LEFT JOIN productdb.ProductCustomParams IAT
            ON IAT.ProductCode=Product.ProductCode AND IAT.CustomParamId='IAT'
        LEFT JOIN productdb.ProductCustomParams IPPT
            ON IPPT.ProductCode=Product.ProductCode AND IPPT.CustomParamId='IPPT'
        WHERE
            CURRENT_TIMESTAMP BETWEEN Price.ValidFrom AND Price.ValidThru
        ''')
        report.write("              TABELA DE MERCADORIAS E SERVIÇOS\r\n\r\n")
        report.write("Código         Descrição                    Un  Valor Unitário\r\n")
        report.write("               Sit.Tributária               IAT           IPPT\r\n")
        report.write("--------------------------------------------------------------\r\n")
        for row in cursor:
            fiscalCategory, productCode, productName, taxRule, productId, unitPrice, measureUnit, IAT, IPPT = map(row.get_entry, ("FiscalCategory", "ProductCode", "ProductName", "TaxRule", "ProductId", "UnitPrice", "MeasureUnit", "IAT", "IPPT"))
            report.write("%14.14s %-28.28s %2.2s %015.15s\r\n%14.14s %-28.28s %-3.3s %14s\r\n\r\n" % (
                productCode,
                productName.decode("UTF-8"),
                measureUnit,
                D(unitPrice),
                "",
                fiscalCategory.decode("UTF-8"),
                IAT,
                IPPT))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[productListReport] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def meiosDePagamento(posid, period_begin, period_end, *args):
    """
    Requisito XXIX:
    O PAF-ECF deve acumular e gravar em banco de dados o valor relativo ao total diário de cada meio de pagamento, por
    tipo de documento a que se refere o pagamento, que deverá ser mantido pelo prazo decadencial e prescricional, estabelecido
    no Código Tributário Nacional.

    Requisito XXX:
    O PAF-ECF deve disponibilizar função que permita a impressão, pelo ECF, de Relatório Gerencial, selecionada por
    período de data inicial e final, denominado "MEIOS DE PAGAMENTO", relacionando os valores acumulados e gravados
    no banco de dados a que se refere o requisito XXIX, contendo:
    a) a identificação do meio de pagamento e, quando for o caso, do cartão de crédito, débito ou similar;
    b) o tipo do documento a que se refere o pagamento;
    c) o valor acumulado;
    d) a data da acumulação;
    e) a soma individual de cada meio de pagamento referente ao período solicitado.
    """
    report = Report()
    conn = None
    try:
        conn = dbd.open(mbcontext, posid)
        total = ZERO
        totalNonFiscal = ZERO
        FPRN_CASHIN = int(fpcmds.FPRN_CASHIN)
        cursor = conn.select("""
        SELECT
            TT.TenderId AS TenderId,
            TT.TenderDescr AS TenderDescr,
            COALESCE(FISCAL.Amount,'0.00') AS FiscalAmount,
            COALESCE(NONFISCAL.Amount,'0.00') AS NonFiscalAmount,
            FISCAL.TAMPERED AS Tampered
        FROM productdb.TenderType TT
        LEFT JOIN (
            SELECT
        FOT.TenderId AS TenderId,
        FOT.TenderDescr AS TenderDescr,
        CASE WHEN count(D.R) > 0 THEN 1 ELSE 0 END AS Tampered,
        tdsum(COALESCE(FOT.TenderAmount,'0.00')) AS Amount
        FROM fiscalinfo.FiscalOrderTender FOT
        LEFT JOIN fiscalinfo.FiscalD D ON D.TB='FiscalOrderTender' AND D.R=FOT._ROWID_
        AND D.C IN ('TenderId','TenderDescr','TenderAmount','OrderTenderId')
        LEFT JOIN fiscalinfo.FiscalOrders FO ON FO.OrderId=FOT.OrderId
        WHERE FO.PosId=%(posid)s AND FO.Period = '%(period_begin)s'
        GROUP BY FOT.TenderId
        ) FISCAL ON FISCAL.TenderId=TT.TenderId
        LEFT JOIN (
            SELECT
                NFT.TenderId AS TenderId,
        NFT.TenderDescr AS TenderDescr,
        CASE WHEN count(D.R) > 0 THEN 1 ELSE 0 END AS Tampered,
                tdsum(COALESCE(NFT.Amount,'0.00')) AS Amount
            FROM fiscalinfo.NonFiscalDocumentTenders NFT
        LEFT JOIN fiscalinfo.FiscalD D ON D.TB='FiscalOrderTender' AND D.R=NFT._ROWID_
        AND D.C IN ('TenderId','TenderDescr','TenderAmount','OrderTenderId')
            JOIN fiscalinfo.NonFiscalDocuments NFD ON NFD.PosId=NFT.PosId AND NFD.FPSerialNo=NFT.FPSerialNo AND NFD.COO=NFT.COO
            WHERE NFD.PosId=%(posid)s AND NFD.Period = %(period_begin)s
                AND NFD.FiscalCMD=%(FPRN_CASHIN)d
            GROUP BY NFT.TenderId
        ) NONFISCAL ON NONFISCAL.TenderId=TT.TenderId
        """ % locals())
        # Nota sobre "NFD.FiscalCMD=1568"
        # Segundo a Finatel, SANGRIA E SUPRIMENTO NÃO APARECEM NESSE RELATÓRIO
        for row in cursor:
            descr = row.get_entry("TenderDescr").decode("UTF-8")
            tampered = int(row.get_entry("Tampered") or 0)
            if tampered:
                descr = "%-25.25s" % descr
                descr = descr.replace(" ", "?")
            report.write(records.A2(
                period_begin,
                descr,
                "1", #  if D(row.get_entry("FiscalAmount")) > 0 else "2" if D(row.get_entry("NonFiscalAmount")) > 0 else "3",
                100*D(row.get_entry("FiscalAmount") or 0) if D(row.get_entry("FiscalAmount") or 0) > 0 else 100*D(row.get_entry("NonFiscalAmount") or 0)
            ))
            report.write("\r\n")
    except Exception as e:
        sys_log_exception('[meiosDePagamento] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def identificacaoDoPAF_ECF(posid, *args):
    """
    Requisito XLIII:
    O PAF-ECF deve disponibilizar função que permita a impressão, pelo ECF, de Relatório Gerencial, denominado “IDENTIFICAÇÃO DO PAF-ECF”, contendo as seguintes informações extraídas do Laudo de Análise do PAF-ECF:
    a) Nº do Laudo;
    b) Identificação da empresa desenvolvedora:
    b1) CNPJ;
    b2) Razão Social;
    b3) Endereço;
    b4) Telefone;
    b5) Contato;
    c) Identificação do PAF-ECF:
    c1) Nome comercial;
    c2) Versão;
    c3) Principal arquivo executável;
    c4) Código de autenticação do principal arquivo executável (MD-5);
    c5) Outros arquivos utilizados e respectivos códigos MD-5.
    d) Relação contendo número de fabricação dos ECF autorizados para funcionar com este PAF-ECF, cadastrados no arquivo auxiliar de que trata o item 4 do requisito XXII.
    """
    report = Report()
    env = "win"  # TODO: Obter environment do POS
    main_module = PAF_ECF.get_main_module(env)
    fpr = fp(posid, mbcontext)
    main_md5 = hashlib.md5(fpr.readFile(main_module)).hexdigest()
    # main_md5 = PAF_ECF.get_MD5(main_module)
    MD5_file = PAF_ECF.SW_MD5_FILE
    MD5_hash = hashlib.md5(fpr.readFile(MD5_file)).hexdigest()
    # MD5_hash = PAF_ECF.get_MD5(MD5_file)
    PAF_CertNumber, DEV_FederalRegister, DEV_CompanyName, DEV_Address, DEV_PhoneNumber, DEV_Contact, SW_Name, ECF_Serial = readEncrypted(posid,
                                                                                                                                         "PAF_CertNumber", "DEV_FederalRegister", "DEV_CompanyName", "DEV_Address", "DEV_PhoneNumber", "DEV_Contact", "SW_Name", "ECF_Serial")
    SW_Version = PAF_ECF.get_software_version()
    PAF_CertDate = PAF_ECF.get_paf_cert_date()
    PAF_SpecVersion = PAF_ECF.SPEC_VERSION_FULL

    fields = [
        (None, "Identificação da empresa desenvolvedora"),

        (PAF_CertNumber,        "Número do laudo"),
        (PAF_CertDate,          "Data de emissão"),
        (DEV_FederalRegister,   "CNPJ"),
        (DEV_CompanyName,       "Razão Social"),
        (DEV_Address,           "Endereço"),
        (DEV_PhoneNumber,       "Telefone"),
        (DEV_Contact,           "Contato"),

        (None,                  "Identificação do PAF-ECF"),
        (PAF_SpecVersion,       "Versão da especificação"),
        (SW_Name,               "Nome comercial"),
        (SW_Version,            "Versão"),

        (MD5_file,              "Arquivo texto (lista de arquivos)"),
        (MD5_hash,              "MD5 da lista de arquivos"),

        (main_module,           "Principal executável"),
        (main_md5,              "MD5 do Principal executável"),

        (None,                  "Demais arquivos utilizados"),
    ]
    # f = fp(posid, mbcontext)
    report.write("\nIDENTIFICAÇÃO DO PAF-ECF\n")
    for value, descr in fields:
        if not value:
            report.write("\r\n%s\r\n" % descr)
            continue
        report.writeln("%s:" % descr)
        report.writeln("%s" % value)
    # Demais arquivos utilizados
    for fname in PAF_ECF.get_extra_modules(env):
        try:
            fdata = fpr.readFile(fname)
        except:
            sys_log_warning("[paf_system_md5] - File not found: %s" % fname)
            continue
        report.writeln(os.path.basename(fname))
        report.writeln("MD5: %s\r\n" % hashlib.md5(fdata).hexdigest())
    report.writeln("\nECF autorizado: %s" % ECF_Serial)
    return report.getvalue()


def electronicFiscalFile(posid, period_begin, period_end, serial, *args):
    '''
    ANEXO VI - DADOS TÉCNICOS PARA GERAÇÃO DO ARQUIVO ELETRÔNICO DOS REGISTROS EFETUADOS PELO PAF-ECF
    +------------------+------------------------------------+-----------------------------------------+--------+
    | Tipo de Registro | Nome do Registro                   | Denominação dos Campos de Classificação | A/D*   |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R01              | Id. do ECF, do Usuário, do PAF-ECF |1º registro (único)                      |        |
    |                  | e da Empresa Desenv. e Dados do Arq|                                         |        |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R02              | Relação de Reduções Z              | Nº de fabricação                        |   A    |
    |                  |                                    | Modelo                                  |   A    |
    |                  |                                    | Nº do usuário                           |   A    |
    |                  |                                    | CRZ                                     |   A    |
    |                  |                                    | CRO                                     |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R03              | Detalhe da Redução Z               | Nº de fabricação                        |   A    |
    |                  |                                    | Modelo                                  |   A    |
    |                  |                                    | Nº do usuário                           |   A    |
    |                  |                                    | CRZ                                     |   A    |
    |                  |                                    | Totalizador                             |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R04              | Cupom Fiscal,Nota Fiscal de Venda a| Nº de fabricação                        |   A    |
    |                  | Consumidor ou Bilhete de Passagem  | Modelo                                  |   A    |
    |                  |                                    | Nº do usuário                           |   A    |
    |                  |                                    | CCF, CVC ou CBP                         |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R05              | Detalhe do Cupom Fiscal, Nota      | Nº de fabricação                        |   A    |
    |                  | Fiscal de Venda a Consumidor ou    | Modelo                                  |   A    |
    |                  | Bilhete de Passagem                | Nº do usuário                           |   A    |
    |                  |                                    | CCF, CVC ou CBP                         |   A    |
    |                  |                                    | Nº do item                              |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R06              | Demais documentos emitidos pelo ECF| Nº de fabricação                        |   A    |
    |                  |                                    | Modelo                                  |   A    |
    |                  |                                    | Nº do usuário                           |   A    |
    |                  |                                    | COO                                     |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | R07              | Detalhe do Cupom Fiscal e do Docu- | Nº de fabricação                        |   A    |
    |                  | mento Não Fiscal- eio de Pagamento | Modelo                                  |   A    |
    |                  |                                    | Nº do usuário                           |   A    |
    |                  |                                    | COO, GNF ou CCF                         |   A    |
    |                  |                                    | Meio de Pagamento                       |   A    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    | EAD              | Assinatura digital                 | Último registro (único)                 |   -    |
    +------------------+------------------------------------+-----------------------------------------+--------+
    '''
    report = Report()
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        # Records must be pushed into these lists
        R01, R02, R03, R04, R05, R06, R07 = [], [], [], [], [], [], []

        # detect manually deleted/added records
        cursor = conn.select('''
        SELECT * FROM fiscalinfo.FiscalD WHERE TB IN (
            'ZTapes','ZTapeTotalizers','FiscalOrders','FiscalOrderItems','NonFiscalDocuments',
            'NonFiscalDocumentTenders','FiscalOrderTender'
        ) AND OP IN ('A','D')
        ''')
        tampered = (cursor.rows() > 0)

        '''
        7.1- REGISTRO TIPO R01 - IDENTIFICAÇÃO DO ECF, DO USUÁRIO, DO PAF-ECF E DA EMPRESA DESENVOLVEDORA E DADOS DO ARQUIVO
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | Nº | Denominação do Campo             | Conteúdo                                        | Tamanho | Posição   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R01"                                           |      03 |  01 |  03 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Nº de fabricação                 | Nº de fabricação do ECF                         |      20 |  04 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Tipo de ECF                      | Tipo de ECF                                     |      07 |  25 |  31 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | Marca do ECF                     | Marca do ECF                                    |      20 |  32 |  51 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  52 |  71 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | Versão do SB                     | Versão atual do Software Básico                 |      10 |  72 |  81 |    X    |
        |    |                                  | do ECF gravada na MF                            |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | Data de inst. do SB              | Data de inst.d a versão atual do                |      08 |  82 |  89 |    D    |
        |    |                                  | Software Básico gravada na MF ECF               |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Horário de inst.do SB            | Horário de insta.da versão atual do Software    |      06 |  90 |  95 |    H    |
        |    |                                  | Bﾇsico gravada na Memória Fiscal do ECF         |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | No.Sequencial do ECF             | No. de ordem sequencial do ECF no estabeleci-   |      03 |  96 |  98 |    N    |
        |    |                                  | mento usuário                                   |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | CNPJ do usuário                  | CNPJ do estabelecimento usuário do ECF          |      14 |  99 | 112 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 13 | Inscr.Est. do usuário            | Inscr. Estadual do estabelecimento usuário      |      14 | 113 | 126 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 14 | CNPJ da desenvolvedora           | CNPJ da empresa desenvolvedora do PAF-ECF       |      14 | 127 | 140 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 15 | Inscr.Est.desenvolvedora         | Inscr.Est.da desenvolvedora do PAF-ECF,se houver|      14 | 141 | 154 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 16 | Inscr.Municipal da desenvolvedora| Inscr.Municipal da desenvolvedora do PAF-ECF    |      14 | 155 | 168 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 17 | Denominação da emp.desenvolvedora| Denominação da empresa desenvolvedora do PAF-ECF|      40 | 169 | 208 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 18 | Nome do PAF-ECF                  | Nome Comercial do PAF-ECF                       |      40 | 209 | 248 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 19 | Versão do PAF-ECF                | Versão atual do PAF-ECF                         |      10 | 249 | 258 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 20 | Código MD-5 do PAF-ECF           | MD-5 do principal arquivo executável do PAF-ECF |      32 | 259 | 290 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 21 | Data Inicial                     | Data do início do período informado no arquivo  |      08 | 291 | 298 |    D    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 22 | Data final                       | Data do fim do período informado no arquivo     |      08 | 299 | 306 |    D    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 23 | Versão da ER-PAF-ECF             | Versão da Especificação de Requisitos do PAF-ECF|      04 | 307 | 310 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select("""
            SELECT
                FP.*,
                CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
            FROM fiscalinfo.FiscalPrinters FP
            LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalPrinters' AND D.R=FP._ROWID_
                AND D.C IN ('FPSerialNo','AdditionalMem','ECFType','ECFBrand','ECFModel','ECFSwVersion','ECFSwDate','ECFSwTime','ECFPosId','UserCNPJ')
            WHERE FP.PosId=%(posid)s AND FP.FPSerialNo='%(serial)s'
            GROUP BY FP._ROWID_
            """ % locals())
        row = cursor.get_row(0)
        if row:
            try:
                User_StateRegister, DEV_FederalRegister, DEV_StateRegister, DEV_MunicipalRegister, DEV_CompanyName, SW_Name, SW_MD5 = readEncrypted(posid,
                                                                                                                                                    "User_StateRegister", "DEV_FederalRegister", "DEV_StateRegister", "DEV_MunicipalRegister", "DEV_CompanyName", "SW_Name", "SW_MD5")
            except:
                User_StateRegister, DEV_FederalRegister, DEV_StateRegister, DEV_MunicipalRegister, DEV_CompanyName, SW_Name, SW_MD5 = ("", 0, "", "", "", "", "")
            if tampered:
                DEV_CompanyName = "%-50.50s" % DEV_CompanyName
                DEV_CompanyName = DEV_CompanyName.replace(" ", "?")
            R01.append(records.R01(
                row.get_entry("FPSerialNo"),                                    # [02] Nº Fabricação
                row.get_entry("AdditionalMem"),                                 # [03] MF adicional
                                                                                # [04] (este campo nao existe - pula para o 05)
                row.get_entry("ECFType"),                                       # [05] Tipo de ECF
                row.get_entry("ECFBrand"),                                      # [06] Marca do ECF
                get_ecf_model(row),                                             # [07] Modelo do ECF
                row.get_entry("ECFSwVersion"),                                  # [08] Versão do SB
                row.get_entry("ECFSwDate"),                                     # [09] Data gravação do SB
                row.get_entry("ECFSwTime"),                                     # [10] Hora gravação do SB
                row.get_entry("ECFPosId"),                                      # [11] No.Sequencial do ECF
                row.get_entry("UserCNPJ"),                                      # [12] CNPJ do usuário
                User_StateRegister,                                             # [13] Inscr.Est. do usuário
                DEV_FederalRegister,                                            # [14]  CNPJ da empresa desenvolvedora do PAF-ECF
                DEV_StateRegister,                                              # [15]  Inscr.Est.da desenvolvedora do PAF-ECF,se houver
                DEV_MunicipalRegister,                                          # [16]  Inscr.Municipal da desenvolvedora do PAF-ECF
                DEV_CompanyName,                                                # [17]  Denominação da empresa desenvolvedora do PAF-ECF
                SW_Name,                                                        # [18] Nome Comercial do PAF-ECF
                PAF_ECF.get_software_version(),                                 # [19] Versão atual do PAF-ECF
                SW_MD5,                                                         # [20] MD-5 do principal arquivo executável do PAF-ECF
                period_begin,                                                   # [21] Data do início do período informado no arquivo
                period_end,                                                     # [22] Data do fim do período informado no arquivo
                PAF_ECF.SPEC_VERSION                                            # [23] Versão da Especificação de Requisitos do PAF-ECF
            ))

        '''
        7.2 - REGISTRO TIPO R02 - RELACAO DE REDUCOES Z
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R02"                                           |      03 |  01 |  03 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Numero de fabricacao             | No de fabricacao do ECF                         |      20 |  04 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Numero do usuario                | No de ordem do usuario do ECF relativo a        |      02 |  45 |  46 |    N    |
        |    |                                  |  respectiva Reducao Z                           |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | CRZ                              | No do Contador de Reducao Z relativo a          |      06 |  47 |  52 |    N    |
        |    |                                  |  respectiva reducao                             |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | COO                              | No do Contador de Ordem de Operacao relativo a  |      06 |  53 |  58 |    N    |
        |    |                                  |   respectiva Reducao Z                          |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | CRO                              | No do Contador de Reinicio de Operacao relativo |      06 |  59 |  64 |    N    |
        |    |                                  |  a respectiva Reducao Z                         |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | Data do movimento                | Data das operacoes relativas a respectiva       |      08 |  65 |  72 |    D    |
        |    |                                  |  Reducao Z                                      |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Data de emissao                  | Data de emissao da Reducao Z                    |      08 |  73 |  80 |    D    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | Hora de emissao                  | Hora de emissao da Reducao Z                    |      06 |  81 |  86 |    H    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | Venda Bruta Diaria               | Valor acumulado neste totalizador relativo a    |      14 |  87 | 100 |    N    |
        |    |                                  |  respectiva Reducao Z, com duas casas decimais. |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 13 | Parametro de desconto ISSQN      | Parametro do ECF para incidencia de desconto    |      01 | 101 | 101 |    X    |
        |    |                                  |  sobre itens sujeitos ao ISSQN [7.2.1.4]        |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select("""
            SELECT
                Z.*,
                CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
            FROM fiscalinfo.ZTapes Z
            LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='ZTapes' AND D.R=Z._ROWID_
                AND D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CRZ','LastCOO','CRO','FPBusinessDate','FPDate','FPTime','DGT','ISSQN')
            WHERE Z.PosId=%(posid)s AND Z.FPSerialNo='%(serial)s' AND Z.Period BETWEEN %(period_begin)s AND %(period_end)s
            GROUP BY Z._ROWID_
            ORDER BY Z.FPSerialNo,Z.ECFModel,Z.ECFUser,Z.CRZ,Z.CRO
        """ % locals())
        for row in cursor:
            data = map(row.get_entry, (
                "FPSerialNo",     # [02] No. Fabricação
                "AdditionalMem",  # [03] MF adicional
                "ECFModel",       # [04] Modelo do ECF
                "ECFUser",        # [05] Número do usuário
                "CRZ",            # [06] CRZ - No do Contador de Reducao Z             |      06 |  47 |  52 |    N    |
                "LastCOO",        # [07] COO - No do Contador de Ordem de Operacao     |      06 |  53 |  58 |    N    |
                "CRO",            # [08] CRO - No do Contador de Reinicio de Operacao  |      06 |  59 |  64 |    N    |
                "FPBusinessDate",  # [09] Data do movimento - Data das operacoes        |      08 |  65 |  72 |    D    |
                "FPDate",         # [10] Data de emissao da Reducao Z                  |      08 |  73 |  80 |    D    |
                "FPTime",         # [11] Hora de emissao da Reducao Z                  |      06 |  81 |  86 |    H    |
                "DGT",            # [12] Venda Bruta Diaria                            |      14 |  87 | 100 |    N    |
                "ISSQN"           # [13] Parametro desc. ISSQN                         |      01 | 101 | 101 |    X    |
            ))
            ecf_model = get_ecf_model(row)
            data[2] = ecf_model
            if data[0] == 'EMULADOR':
                data[3] = '1' ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
            R02.append(records.R02(*data))
            '''
            7.3 - REGISTRO TIPO R03 - DETALHE DA REDUCAO Z
            +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
            | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 01 | Tipo                             | "R03"                                           |      03 |  01 |  03 |    X    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 02 | Numero de fabricacao             | No de fabricacao do ECF                         |      20 |  04 |  23 |    X    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 05 | Numero do usuario                | No de ordem do usuario do ECF                   |      02 |  45 |  46 |    N    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 06 | CRZ                              | No do Contador de Reducao Z relativo a          |      06 |  47 |  52 |    N    |
            |    |                                  |  respectiva reducao                             |         |     |     |         |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 07 | Totalizador Parcial              | Codigo do totalizador conforme tabela abaixo    |      07 |  53 |  59 |    X    |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            | 08 | Valor acumulado                  | Valor acumulado no totalizador, relativo a      |      13 |  60 |  72 |    N    |
            |    |                                  |  respectiva Reducao Z, com duas casas decimais. |         |     |     |         |
            +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
            '''
            cursor = conn.select("""
                SELECT
                    ZT.*,
                    CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
                FROM fiscalinfo.ZTapeTotalizers ZT
                LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='ZTapeTotalizers' AND D.R=ZT._ROWID_
                    AND D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CRZ','Totalizer','Amount')
                WHERE ZT.PosId=%(posid)s AND ZT.FPSerialNo='%(serial)s' AND ZT.Period BETWEEN %(period_begin)s AND %(period_end)s
                GROUP BY ZT._ROWID_
                ORDER BY ZT.FPSerialNo,ZT.ECFModel,ZT.ECFUser,ZT.CRZ,ZT.Totalizer
            """ % locals())
            for row in cursor:
                data = map(row.get_entry, (
                    "FPSerialNo",               # [02] No de fabricacao do ECF        |      20 |  04 |  23 |    X    |
                    "AdditionalMem",            # [03] MF adicional                   |      01 |  24 |  24 |    X    |
                    "ECFModel",                 # [04] Modelo do ECF                  |      20 |  25 |  44 |    X    |
                    "ECFUser",                  # [05] Número do usuário              |      02 |  45 |  46 |    N    |
                    "CRZ",                      # [06] CRZ-Contador de Reducao Z      |      06 |  47 |  52 |    N    |
                    "Totalizer",                # [07] Totalizador Parcial            |      07 |  53 |  59 |    X    |
                    "Amount",                   # [08] Valor acumulado                |      13 |  60 |  72 |    N    |
                ))
                data[2] = get_ecf_model(row)
                if data[0] == 'EMULADOR':
                    data[3] = '1'  ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
                R03.append(records.R03(*data))
        '''
        7.4 - REGISTRO TIPO R04 - CUPOM FISCAL, NOTA FISCAL DE VENDA A CONSUMIDOR E BILHETE DE PASSAGEM
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R04"                                           |      03 |   1 |   3 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Numero de fabricacao             | No de fabricacao do ECF                         |      20 |   4 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Numero do usuario                | No de ordem do usuario do ECF                   |      02 |  45 |  46 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | CCF,CVC ou CBP, conf. doc.emitido| No do contador do respectivo documento emitido  |      06 |  47 |  52 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | COO-Contador de Ordem de Operacao| No do COO relativo ao respectivo documento      |      06 |  53 |  58 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | Data de inicio da emissao        | Data de inicio da emissao do documento impressa |      08 |  59 |  66 |    D    |
        |    |                                  |  no cabecalho do documento                      |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | Subtotal do Documento            | Valor total do documento,com duas casas decimais|      14 |  67 |  80 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Desconto sobre subtotal          | Valor do desconto ou Percentual aplicado sobre o|      13 |  81 |  93 |    N    |
        |    |                                  |   valor do subtotal do documento(duas casas dec)|         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | Tipo de Desconto sobre subtotal  | "V" p/ valor monetario ou "P" p/ percentual     |       1 |  94 |  94 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | Acrescimo sobre subtotal         | Valor do acrescimo ou Percentual aplicado sobre |      13 |  95 | 107 |    N    |
        |    |                                  | valor do subtotal do documento(duas casas dec)  |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 13 | Tipo de Acrescimo sobre subtotal | "V" para valor monetario ou "P" para percentual |       1 | 108 | 108 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 14 | Valor Total Liquido              | Valor total do Cupom Fiscal apos                |      14 | 109 | 122 |    N    |
        |    |                                  |  desconto/acrescimo, com duas casas decimais    |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 15 | Indicador de Cancelamento        | "S" ou "N", p/ o cancelamento do documento.     |      01 | 123 | 123 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 16 | Cancel. de Acrescimo no Subtotal | Valor do cancelamento de acrescimo no subtotal  |      13 | 124 | 136 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 17 | Ordem de aplicacao de Desc./Acres| Indicador de aplicacao de desconto/acrescimo em |      01 | 137 | 137 |    X    |
        |    |                                  |  Subtotal. 'D' ou 'A' caso tenha ocorrido       |         |     |     |         |
        |    |                                  |  primeiro desconto ou acrescimo, respectivamente|         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 18 | Nome do adquirente               | Nome do Cliente                                 |      40 | 138 | 177 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 19 | CPF/CNPJ do adquirente           | CPF ou CNPJ do adquirente                       |      14 | 178 | 191 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select("""
        SELECT
            FPSerialNo,AdditionalMem,ECFModel,ECFUser,CCF,COO,COOVoid,FPDate,
            tdadd(COALESCE(TotalGross,'0.00'),COALESCE(DiscountAmount,'0.00')) AS SubTotal,
            COALESCE(DiscountAmount,'0.00') AS DiscountAmount,
            COALESCE(TotalGross,'0.00') AS TotalAmount,
            CASE WHEN StateId=4 THEN 'S' ELSE 'N' END AS VoidIndicator,
            CustomerName,
            COALESCE(CustomerCPF, '0') AS CustomerCPF,
            OrderId,
            CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
        FROM fiscalinfo.FiscalOrders FO
        LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalOrders' AND D.R=FO._ROWID_
            AND D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CCF','COO','COOVoid','FPDate','TotalGross','DiscountAmount','StateId','CustomerName','CustomerCPF','OrderId')
        WHERE FO.PosId=%(posid)s
            AND FO.FPSerialNo='%(serial)s'
            AND FO.Period BETWEEN %(period_begin)s AND %(period_end)s
        GROUP BY FO._ROWID_
        ORDER BY FO.FPSerialNo,FO.ECFModel,FO.ECFUser,FO.CCF
        """ % locals())
        for row in cursor:
            e = row.get_entry
            # Some values must be forced to zero when this is a "void current" order
            order_id = e("OrderId")
            data = [
                e("FPSerialNo"),                                # [02] No de fabricacao do ECF           |      20 |  04 |  23 |    X    |
                e("AdditionalMem"),                             # [03] MF adicional                      |      01 |  24 |  24 |    X    |
                e("ECFModel"),                                  # [04] Modelo do ECF                     |      20 |  25 |  44 |    X    |
                e("ECFUser"),                                   # [05] Número do usuário                 |      02 |  45 |  46 |    N    |
                e("CCF"),                                       # [06] CCF,CVC ou CBP, conf. doc.emitido |      06 |  47 |  52 |    N    |
                e("COO"),                                       # [07] COO-Contador de Ordem de Operacao |      06 |  53 |  58 |    N    |
                e("FPDate"),                                    # [08] Data de inicio da emissao         |      08 |  59 |  66 |    D    |
                0 if (e("VoidIndicator") == "S" and e("COOVoid")) else e("SubTotal"), # [09] Subtotal do Documento             |      14 |  67 |  80 |    N    |
                e("DiscountAmount"),                            # [10] Desconto sobre subtotal           |      13 |  81 |  93 |    N    |
                "",                                            # [11] Tipo de Desconto sobre subtotal   |       1 |  94 |  94 |    X    |
                0,                                              # [12] Acrescimo sobre subtotal          |      13 |  95 | 107 |    N    |
                "",                                            # [13] Tipo de Acrescimo sobre subtotal  |       1 | 108 | 108 |    X    |
                0 if (e("VoidIndicator") == "S" and e("COOVoid")) else e("TotalAmount"), # [14] Valor Total Liquido               |      14 | 109 | 122 |    N    |
                e("VoidIndicator"),                             # [15] Indicador de Cancelamento         |      01 | 123 | 123 |    X    |
                0,                                              # [16] Cancel. de Acrescimo no Subtotal  |      13 | 124 | 136 |    N    |
                "",                                            # [17] Ordem de aplicacao de Desc./Acres |      01 | 137 | 137 |    X    |
                e("CustomerName"),                              # [18] Nome do adquirente                |      40 | 138 | 177 |    X    |
                e("CustomerCPF") or "0",                        # [19] CPF/CNPJ do adquirente            |      14 | 178 | 191 |    N    |
            ]
            data[2] = get_ecf_model(row)
            if data[0] == 'EMULADOR':
                data[3] = '1' ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
            R04.append(records.R04(*data))
            del e
        '''
        7.5 - REGISTRO TIPO R05 - DETALHE DO CUPOM FISCAL, DA NOTA FISCAL DE VENDA A CONSUMIDOR OU DO BILHETE DE PASSAGEM
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R05"                                           |      03 |  01 |  03 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Numero de fabricacao             | Numero de fabricacao do ECF                     |      20 |  04 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Numero do usuario                | Numero de ordem do usuario do ECF               |      02 |  45 |  46 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | COO-Contador de Ordem de Operacao| Numero do COO relativo ao respectivo documento  |      06 |  47 |  52 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | CCF,CVC ou CBP, conforme o doc.  | No. do contador do respectivo documento emitido |      06 |  53 |  58 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | Numero do item                   | Numero do item registrado no documento          |      03 |  59 |  61 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | Codigo do Produto ou Servico     | Codigo do produto ou servico registrado no doc. |      14 |  62 |  75 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Descricao                        | Descr. produto/servico constante no Cupom Fiscal|     100 |  76 | 175 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | Quantidade                       | Qtde comercializada,sem separacao das casas deci|      07 | 176 | 182 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | Unidade                          | Unidade de medida                               |      03 | 183 | 185 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 13 | Valor unitario                   | Valor unitario do produto ou servico, sem a     |      08 | 186 | 193 |    N    |
        |    |                                  |   separacao das casas decimais                  |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 14 | Desconto sobre item              | Valor do desconto incidente sobre o valor do    |      08 | 194 | 201 |    N    |
        |    |                                  |   item, com duas casas decimais.                |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 15 | Acrescimo sobre item             | Valor do acrescimo incidente sobre o valor do   |      08 | 202 | 209 |    N    |
        |    |                                  |   item, com duas casas decimais.                |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 16 | Valor total liquido              | Valor total liquido do item[com duas casas dec.]|      14 | 210 | 223 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 17 | Totalizador parcial              | Codigo do totalizador relativo ao produto ou    |      07 | 224 | 230 |    X    |
        |    |                                  |   servico conforme tabela abaixo.               |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 18 | Indicador de cancelamento        | "S"/"N", conforme tenha ocorrido ou nao, o can- |      01 | 231 | 231 |    X    |
        |    |                                  |   celamento total do item no documento. Informar|         |     |     |         |
        |    |                                  |   "P" quando ocorrer o cancel. parcial do item. |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 19 | Quantidade cancelada             | Quantidade cancelada, no caso de cancelamento   |      07 | 232 | 238 |    N    |
        |    |                                  |   parcial de item,sem a separacao das casas dec.|         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 20 | Valor cancelado                  | Valor cancelado,no caso de canc. parcial de item|      13 | 239 | 251 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 21 | Cancelamento de acrescimo no item| Valor do cancelamento de acrescimo no item      |      13 | 252 | 264 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 22 | Indicador (IAT)                  | Indicador de Arredondamento/Truncamento relativo|      01 | 265 | 265 |    X    |
        |    |                                  |   a regra de calculo do valor total liquido do  |         |     |     |         |
        |    |                                  |   item, "T" p/ truncamento/"A" p/ arredondamento|         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 23 | Indicador (IPPT)                 | Indicador de Producao Propria ou de Terceiro    |      01 | 266 | 266 |    X    |
        |    |                                  |   relativo a mercadoria, "P" p/ merc. de produ- |         |     |     |         |
        |    |                                  |   cao propria ou "T" p/ produzida por terceiros |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 24 | Casas decimais da quantidade     | Parametro de no de casas decimais da quantidade |      01 | 267 | 267 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 25 | Casas decimais de valor unitario | Parametro de no de casas dec. de valor unitario |      01 | 268 | 268 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select("""
        SELECT
            F.FPSerialNo AS FPSerialNo,
            F.AdditionalMem AS AdditionalMem,
            F.ECFModel AS ECFModel,
            F.ECFUser AS ECFUser,
            F.CCF AS CCF,
            F.COO AS COO,
            F.COOVoid AS COOVoid,
            FOI.LineNumber AS LineNumber,
            FOI.PartCode AS ProductCode,
            FOI.ProductName AS ProductName,
            tdadd(FOI.OrderedQty,FOI.DecQty,3) AS TotalQty,
            FOI.MeasureUnit AS MeasureUnit,
            FOI.UnitPrice AS UnitPrice,
            FOI.DiscountAmount AS DiscountAmount,
            tdsub(tdmul(FOI.OrderedQty,FOI.UnitPrice),FOI.DiscountAmount) AS TotalAmount,
            FOI.TaxCode AS TaxCode,
            FOI.VoidIndicator AS VoidIndicator,
            CASE WHEN FOI.VoidIndicator='P' THEN tdscale(FOI.DecQty,3,1) ELSE 0 END AS VoidQty, --7.5.1.4 - Campo 19 - Informar a quantidade cancelada somente quando ocorrer o cancelamento parcial do item
            CASE WHEN FOI.VoidIndicator='P' THEN tdmul(FOI.DecQty,FOI.UnitPrice) ELSE 0 END AS VoidAmount, --7.5.1.5 - Campo 20 - Informar o valor cancelado somente quando ocorrer o cancelamento parcial do item
            FOI.IAT AS IAT,
            FOI.IPPT AS IPPT,
            FOI.OrderedQty AS OrderedQty,
            CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered,
            CASE WHEN D2.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered2
        FROM fiscalinfo.FiscalOrderItems FOI
        JOIN fiscalinfo.FiscalOrders F ON F.OrderId=FOI.OrderId
        LEFT JOIN  fiscalinfo.FiscalD D ON D.TB='FiscalOrderItems' AND D.R=FOI._ROWID_
            AND D.C IN ('LineNumber','PartCode','ProductName','OrderedQty','DecQty','MeasureUnit','UnitPrice','DiscountAmount','TaxCode','VoidIndicator','IAT','IPPT')
        LEFT JOIN  fiscalinfo.FiscalD D2 ON D2.TB='FiscalOrders' AND D2.R=F._ROWID_
            AND D2.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','CCF','COO','COOVoid')
        WHERE F.PosId=%(posid)s
            AND F.FPSerialNo='%(serial)s'
            AND F.Period BETWEEN %(period_begin)s AND %(period_end)s
            AND F.COOVoid IS NULL
        GROUP BY FOI._ROWID_
        ORDER BY F.FPSerialNo,F.ECFModel,F.ECFUser,F.CCF,FOI.LineNumber
        """ % locals())
        for row in cursor:
            taxcode = row.get_entry("TaxCode")
            if taxcode == "FF":
                taxcode = "F1"
            elif taxcode == "II":
                taxcode = "I1"
            elif taxcode == "NN":
                taxcode = "N1"

            e = row.get_entry
            data = [
                e("FPSerialNo"),                    # [02]  No de fabricacao do ECF           |      20 |  04 |  23 |    X    |
                e("AdditionalMem"),                 # [03]  MF adicional                      |      01 |  24 |  24 |    X    |
                e("ECFModel"),                      # [04]  Modelo do ECF                     |      20 |  25 |  44 |    X    |
                e("ECFUser"),                       # [05]  Número do usuário                 |      02 |  45 |  46 |    N    |
                e("COO"),                           # [06] | COO-Contador de Ordem de Operacao|      06 |  47 |  52 |    N    |
                e("CCF"),                           # [07] | CCF,CVC ou CBP, conforme o doc.  |      06 |  53 |  58 |    N    |
                e("LineNumber"),                    # [08] | Numero do item                   |      03 |  59 |  61 |    N    |
                e("ProductCode"),                   # [09] | Codigo do Produto ou Servico     |      14 |  62 |  75 |    X    |
                e("ProductName"),                   # [10] | Descricao                        |     100 |  76 | 175 |    X    |
                e("TotalQty"),                      # [11] | Quantidade                       |      07 | 176 | 182 |    N    |
                e("MeasureUnit"),                   # [12] | Unidade                          |      03 | 183 | 185 |    X    |
                e("UnitPrice"),                     # [13] | Valor unitario                   |      08 | 186 | 193 |    N    |
                e("DiscountAmount"),                # [14] | Desconto sobre item              |      08 | 194 | 201 |    N    |
                0,                                  # [15] | Acrescimo sobre item             |      08 | 202 | 209 |    N    |
                e("TotalAmount"),                   # [16] | Valor total liquido              |      14 | 210 | 223 |    N    |
                taxcode,                            # [17] | Totalizador parcial              |      07 | 224 | 230 |    X    |
                e("VoidIndicator"),                 # [18] | Indicador de cancelamento        |      01 | 231 | 231 |    X    |
                e("VoidQty"),                       # [19] | Quantidade cancelada             |      07 | 232 | 238 |    N    |
                e("VoidAmount"),                    # [20] | Valor cancelado                  |      13 | 239 | 251 |    N    |
                0,                                  # [21] | Cancelamento de acrescimo no item|      13 | 252 | 264 |    N    |
                e("IAT"),                           # [22] | Indicador (IAT)                  |      01 | 265 | 265 |    X    |
                e("IPPT"),                          # [23] | Indicador (IPPT)                 |      01 | 266 | 266 |    X    |
                3,                                  # [24] | Casas decimais da quantidade     |      01 | 267 | 267 |    N    |
                3,                                  # [25] | Casas decimais de valor unitario |      01 | 268 | 268 |    N    |
            ]
            data[2] = get_ecf_model(row)
            if data[0] == 'EMULADOR':
                data[3] = '1' ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
            R05.append(records.R05(*data))
            del e
        '''
        7.6 - REGISTRO TIPO R06 - DEMAIS DOCUMENTOS EMITIDOS PELO ECF
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R06"                                           |      03 |   1 |   3 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Numero de fabricacao             | Numero de fabricacao do ECF                     |      20 |   4 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF Adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Numero do usuario                | Numero de ordem do usuario do ECF               |      02 |  45 |  46 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | COO-Contador de Ordem de Operacao| Numero do COO relativo ao respectivo documento  |      06 |  47 |  52 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | GNF-Cont.Geral de Operacao N Fisc| No GNF relativo ao respectivo docto, qdo houver |      06 |  53 |  58 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | GRG-Cont.Geral de Relat.Gerencial| No do GRG relativo ao respectivo docto [7.6.1.2]|      06 |  59 |  64 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | CDC-Cont.Comprovante de Cred/Deb | No do CDC relativo ao respectivo docto [7.6.1.3]|      04 |  65 |  68 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Denominacao                      | Simbolo referente a denominacao do docto fiscal |      02 |  69 |  70 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | Data final de emissao            | Data final de emissao (no rodape do documento)  |      08 |  71 |  78 |    D    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | Hora final de emissao            | Hora final de emissao (no rodape do documento)  |      06 |  79 |  84 |    H    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select('''
        SELECT
            FPSerialNo,AdditionalMem,ECFModel,ECFUser,COO,GNF,GRG,CDC,DocType,FPDate,FPTime,
            CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered
        FROM NonFiscalDocuments NFD
        LEFT JOIN fiscalinfo.FiscalD D ON D.TB='NonFiscalDocuments' AND D.R=NFD._ROWID_ AND (D.OP='A' OR
            D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','COO','GNF','GRG','CDC','DocType','FPDate','FPTime'))
        WHERE PosId=%(posid)s
            AND FPSerialNo='%(serial)s'
            AND Period BETWEEN %(period_begin)s AND %(period_end)s
        GROUP BY NFD._ROWID_
        ORDER BY FPSerialNo,ECFModel,ECFUser,COO
        ''' % locals())
        for row in cursor:
            data = map(row.get_entry, (
                "FPSerialNo",       # [02] No de fabricacao do ECF           |      20 |  04 |  23 |    X    |
                "AdditionalMem",    # [03] MF adicional                      |      01 |  24 |  24 |    X    |
                "ECFModel",         # [04] Modelo do ECF                     |      20 |  25 |  44 |    X    |
                "ECFUser",          # [05] Número do usuário                 |      02 |  45 |  46 |    N    |
                "COO",              # [06] COO-Contador de Ordem de Operacao |      06 |  47 |  52 |    N    |
                "GNF",              # [07] GNF-Cont.Geral de Operacao N Fisc |      06 |  53 |  58 |    N    |
                "GRG",              # [08] GRG-Cont.Geral de Relat.Gerencial |      06 |  59 |  64 |    N    |
                "CDC",              # [09] CDC-Cont.Comprovante de Cred/Deb  |      04 |  65 |  68 |    N    |
                "DocType",          # [10] Denominacao                       |      02 |  69 |  70 |    X    |
                "FPDate",           # [11] Data final de emissao             |      08 |  71 |  78 |    D    |
                "FPTime",           # [12] Hora final de emissao             |      06 |  79 |  84 |    H    |
            ))
            data[2] = get_ecf_model(row)
            if data[0] == 'EMULADOR':
                data[3] = '1' ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
            R06.append(records.R06(*data))

        '''
        7.7 - REGISTRO TIPO R07 - DETALHE DO CUPOM FISCAL E DO DOCUMENTO NAO FISCAL - MEIO DE PAGAMENTO
        +----+----------------------------------+-------------------------------------------------+---------+-----------+---------+
        | No | Denominacao do Campo             | Conteudo                                        | Tamanho | Posicao   | Formato |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 01 | Tipo                             | "R07"                                           |      03 |  01 |  03 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 02 | Numero de fabricacao             | Numero de fabricacao do ECF                     |      20 |  04 |  23 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 03 | MF adicional                     | Letra indicativa de MF adicional                |      01 |  24 |  24 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 04 | Modelo do ECF                    | Modelo do ECF                                   |      20 |  25 |  44 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 05 | Numero do usuario                | Numero de ordem do usuario do ECF               |      02 |  45 |  46 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 06 | COO-Contador de Ordem de Operacao| No do COO relativo ao respectivo Cupom Fiscal ou|      06 |  47 |  52 |    N    |
        |    |                                  |   Comprovante Nao Fiscal                        |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 07 | CCF                              | Numero do Contador de Cupom Fiscal relativo ao  |      06 |  53 |  58 |    N    |
        |    |                                  |   respectivo Cupom Fiscal emitido               |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 08 | GNF                              | No Contador Geral Nao Fiscal relativo ao res-   |      06 |  59 |  64 |    N    |
        |    |                                  |   pectivo Comprovante Nao Fiscal emitido        |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 09 | Meio de pagamento                | Descr. do totalizador parcial de meio de pagto  |      15 |  65 |  79 |    X    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 10 | Valor pago                       | Valor do pagamento efetuado, com duas casas dec |      13 |  80 |  92 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 11 | Indicador de estorno             | "S"/"N",conforme tenha ocorrido ou nao,o estorno|      01 |  93 |  93 |    X    |
        |    |                                  |   do pagto, ou "P" p/ estorno parcial do pagto  |         |     |     |         |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        | 12 | Valor estornado                  | Valor do estorno efetuado,com duas casas dec.   |      13 |  94 | 106 |    N    |
        +----+----------------------------------+-------------------------------------------------+---------+-----+-----+---------+
        '''
        cursor = conn.select('''
        SELECT * FROM (
            SELECT
                DT.FPSerialNo AS FPSerialNo,
                DOC.AdditionalMem AS AdditionalMem,
                DOC.ECFModel AS ECFModel,
                DOC.ECFUser AS ECFUser,
                DT.COO AS COO,
                0 AS COOVoid,
                0 AS CCF,
                DOC.GNF AS GNF,
                DT.TenderDescr AS TenderDescr,
                DT.Amount AS Amount,
                'N' AS RefundIndicator,
                '0.00' AS RefundedAmount,
                CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered,
                CASE WHEN D2.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered2
            FROM NonFiscalDocumentTenders DT
            JOIN NonFiscalDocuments DOC ON DOC.FPSerialNo=DT.FPSerialNo AND DOC.COO=DT.COO
            LEFT JOIN fiscalinfo.FiscalD D ON D.TB='NonFiscalDocumentTenders' AND D.R=DT._ROWID_ AND (D.OP='A' OR
                D.C IN ('FPSerialNo','COO','COOVoid','TenderDescr','Amount'))
            LEFT JOIN fiscalinfo.FiscalD D2 ON D2.TB='NonFiscalDocuments' AND D2.R=DOC._ROWID_ AND (D2.OP='A' OR
                D2.C IN ('AdditionalMem','ECFModel','ECFUser','GNF'))
            WHERE DOC.PosId=%(posid)s
                AND DOC.FPSerialNo='%(serial)s'
                AND DOC.Period BETWEEN %(period_begin)s AND %(period_end)s
            GROUP BY DT._ROWID_

            UNION ALL
            SELECT
                F.FPSerialNo AS FPSerialNo,
                F.AdditionalMem AS AdditionalMem,
                F.ECFModel AS ECFModel,
                F.ECFUser AS ECFUser,
                F.COO AS COO,
                F.COOVoid AS COOVoid,
                F.CCF AS CCF,
                0 AS GNF,
                FOT.TenderDescr AS TenderDescr,
                FOT.TenderAmount AS Amount,
                'N' AS RefundIndicator,
                '0.00' AS RefundedAmount,
                CASE WHEN D.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered,
                CASE WHEN D2.TB IS NOT NULL THEN 1 ELSE 0 END AS Tampered2
            FROM fiscalinfo.FiscalOrders F
            JOIN fiscalinfo.FiscalOrderTender FOT ON FOT.OrderId=F.OrderId
            LEFT JOIN fiscalinfo.FiscalD D ON D.TB='FiscalOrders' AND D.R=F._ROWID_ AND (D.OP='A' OR
                D.C IN ('FPSerialNo','AdditionalMem','ECFModel','ECFUser','COO','COOVoid','CCF'))
            LEFT JOIN fiscalinfo.FiscalD D2 ON D2.TB='FiscalOrderTender' AND D2.R=FOT._ROWID_ AND (D2.OP='A' OR
                D2.C IN ('TenderDescr','TenderAmount'))
            WHERE F.PosId=%(posid)s
                AND F.FPSerialNo='%(serial)s'
                AND F.Period BETWEEN %(period_begin)s AND %(period_end)s
            GROUP BY FOT._ROWID_
        )
        ORDER BY FPSerialNo,ECFModel,ECFUser,COO
        ''' % locals())
        for row in cursor:
            data = map(row.get_entry, (
                "FPSerialNo",       # [02] No de fabricacao do ECF           |      20 |  04 |  23 |    X    |
                "AdditionalMem",    # [03] MF adicional                      |      01 |  24 |  24 |    X    |
                "ECFModel",         # [04] Modelo do ECF                     |      20 |  25 |  44 |    X    |
                "ECFUser",          # [05] Número do usuário                 |      02 |  45 |  46 |    N    |
                "COO",              # [06] COO-Contador de Ordem de Operacao |      06 |  47 |  52 |    N    |
                "CCF",              # [07] CCF                               |      06 |  53 |  58 |    N    |
                "GNF",              # [08] GNF                               |      06 |  59 |  64 |    N    |
                "TenderDescr",      # [09] Meio de pagamento                 |      15 |  65 |  79 |    X    |
                "Amount",           # [10] Valor pago                        |      13 |  80 |  92 |    N    |
                "RefundIndicator",  # [11] Indicador de estorno              |      01 |  93 |  93 |    X    |
                "RefundedAmount",   # [12] Valor estornado                   |      13 |  94 | 106 |    N    |
            ))
            if row.get_entry("COOVoid") != None:
                data[9] = "S"
                data[10] = data[8]
            data[2] = get_ecf_model(row)
            if data[0] == 'EMULADOR':
                data[3] = '1' ## Corrigindo ECFUser, que no emulador por algum motivo esta chegando 1308, e excede numero maximo de caracteres do campo(2)
            R07.append(records.R07(*data))

        # All records done! Consolidate and output report
        all_records = R01 + R02 + R03 + R04 + R05 + R06 + R07
        report.write("\r\n".join(all_records))
        report.write("\r\n")
    except Exception as e:
        sys_log_exception('[electronicFiscalFile] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def fiscal_eft_customer_slip(posid, eft_xml, *args):
    report = Report()
    eft_xml = etree.XML(eft_xml)
    receiptCustomer = eft_xml.get("ReceiptCustomer")
    report.write(base64.b64decode(receiptCustomer or ''))
    return report.getvalue()

def fiscal_eft_merchant_slip(posid, eft_xml, *args):
    report = Report()
    eft_xml = etree.XML(eft_xml)
    receiptMerchant = eft_xml.get("ReceiptMerchant")
    report.write(base64.b64decode(receiptMerchant or ''))
    return report.getvalue()


def paf_indice_tecnico(*args):
    conn = None
    try:
        conn = dbd.open(mbcontext)
        cursor = conn.select("""
            SELECT
                I.ProductCode AS ProductCode,
                P.ProductName AS ProductName,
                I.SKU AS SKU,
                E.Descr AS Insumo,
                E.Unidade AS Unidade,
                I.Qty AS IndiceTecnico
            FROM fiscalinfo.Insumos I
                JOIN fiscalinfo.Estoque E ON I.SKU=E.SKU
                JOIN productdb.Product P ON P.ProductCode=I.ProductCode
            ORDER BY I.ProductCode
        """)
        report = Report()
        report.write("    ÍNDICE TÉCNICO DE PRODUÇÃO\n")
        current_pcode = ""
        for row in cursor:
            pcode, pname, sku, insumo, unidade, itecnico = map(row.get_entry, ("ProductCode", "ProductName", "SKU", "Insumo", "Unidade", "IndiceTecnico",))
            if pcode != current_pcode:
                report.write("\n")
                report.write("%(pcode)s - %(pname)s\n" % locals())
                current_pcode = pcode
            report.write("   %(sku)s - %(insumo)s (%(itecnico)s %(unidade)s)\n" % locals())
    except Exception as e:
        sys_log_exception('[paf_indice_tecnico] Exception: {}'.format(e))
        raise
    finally:
        if conn:
            conn.close()
    return report.getvalue()


def paf_system_md5(posid, *args):
    # ANEXO X
    # DADOS TÉCNICOS PARA GERAÇÃO DO ARQUIVO TEXTO DE QUE TRATA O ALÍNEA D DO INCISO I DA CLÁUSULA NONA DO CONVÊNIO ICMS 15/08
    # (REQUISITO IX)
    # http://www.fazenda.gov.br/confaz/confaz/atos/atos_cotepe/2008/AC006_08.htm
    report = Report()
    DEV_FederalRegister, DEV_StateRegister, DEV_MunicipalRegister, DEV_CompanyName, SW_Name, PAF_CertNumber = readEncrypted(posid, "DEV_FederalRegister", "DEV_StateRegister", "DEV_MunicipalRegister", "DEV_CompanyName", "SW_Name", "PAF_CertNumber")
    SW_Version = PAF_ECF.get_software_version()
    # PAF_SpecVersion = PAF_ECF.SPEC_VERSION
    report.write(records.N1(DEV_FederalRegister, DEV_StateRegister, DEV_MunicipalRegister, DEV_CompanyName))
    report.write("\r\n")
    report.write(records.N2(PAF_CertNumber, SW_Name, SW_Version))
    report.write("\r\n")
    env = "win"  # TODO: Obter environment do POS
    files = PAF_ECF.get_all_modules(env)
    sorted_files = sorted(files, key=lambda s: s.lower())
    qty = 0
    fpr = fp(posid, mbcontext)
    for fname in sorted_files:
        try:
            fdata = fpr.readFile(fname)
        except:
            sys_log_warning("[paf_system_md5] - File not found: %s" % fname)
            continue
        report.write(records.N3(os.path.basename(fname).upper(), hashlib.md5(fdata).hexdigest().upper()))
        report.write("\r\n")
        qty += 1
    report.write(records.N9(DEV_FederalRegister, DEV_StateRegister, qty))
    report.write("\r\n")
    return report.getvalue()


def paf_parametros_de_config(posid, date_time, *args):
    # Requisito VII, ITEM 21
    # Parâmetros de Configuração: para emitir Relatório Gerencial pelo ECF contendo a configuração
    # programada no PAF-ECF em execução para os parâmetros de configuração previstos nesta especificação.
    # opens the database connection

    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        cursor = conn.select("SELECT KeyValue FROM storecfg.Configuration WHERE KeyPath = 'Store.UnidadeFederacao';")
        state = None
        for row in cursor:
            state = row.get_entry("KeyValue")
    finally:
        if conn:
            conn.close()
    if state in ("AC", "AL", "AM", "AP", "CE", "MG", "PA", "PR", "PE", "PI", "RN", "RS", "RO", "RR", "SP"):
        state_code = "ND"
    elif state == "RJ":
        state_code = "R"
    elif state == "MA":
        state_code = "S"
    elif state == "TO":
        state_code = "T"
    elif state == "DF":
        state_code = "U"
    elif state == "SC":
        state_code = "V"
    elif state in ("GO", "MS"):
        state_code = "W"
    elif state in ("ES", "PB"):
        state_code = "Y"
    elif state == "BA":
        state_code = "Z"
    else:
        state_code = "ND"  # MT e SE
    report = Report()
    report.write("""======================================
      PARAMETROS DE CONFIGURACAO
======================================


  Perfil de requisitos do PAF-ECF: %s


======================================
   Impresso em %s
======================================
""" % (state_code, date_time))

    return report.getvalue()


def fiscalReport(reportFunction, *args):
    """
    Generates a report not signed
    @param reportFunction: The report function to be executed
    @param args: extra arguments to the report function
    @return: the report
    """
    func = globals()[reportFunction]
    report = func(*args)
    return report

def signedFiscalReport(reportFunction, *args):
    """
    Generates a report and sign it (add the EAD record)
    @param reportFunction: The report function to be executed
    @param args: extra arguments to the report function
    @return: the signed report (reportData + EAD)
    """
    report = fiscalReport(reportFunction, *args)
    return signFiscalReport(report)


def signFiscalReport(reportData, *args):
    """
    Signs a fiscal report (adds the EAD record)
    @param reportData: The report to be signed
    @return: the signed report (reportData + EAD)
    """
    # Generate the EAD record
    EAD = PAF_ECF.get_EAD_signature(reportData)
    # Output the signed report
    return "%s%s" % (reportData, EAD)


def _decimal_to_fixed_int(v):
    return int((D(v) * 100).quantize(D("1"), decimal.ROUND_DOWN))


def _decimal_to_fixed_int3(v):
    return int((D(v) * 1000).quantize(D("1"), decimal.ROUND_DOWN))
