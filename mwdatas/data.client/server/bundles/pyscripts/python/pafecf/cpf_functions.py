# -*- coding: utf-8 -*-
# Python module responsible to validate the Brazilian CPF numbers
#
# Copyright (C) 2008-2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$


def _gen(cpf):
    """Gera o próximo dígito do número de CPF

    """
    res = []
    for i in range(len(cpf)):
        a = cpf[i]
        b = (len(cpf) + 1 - i)
        res.append(b * a)

    res = reduce(int.__add__, res) % 11

    if res > 1:
        return (11 - res)
    else:
        return 0


def _translate(cpf):
    """Traduz o número como string na forma:

    123.456.789-10

    para a forma:

    12345678910

    """

    i = xrange(256)
    t = [' '] * 256
    e = ''.join([chr(x) for x in i if not chr(x).isdigit()])

    for x in i:
        if chr(x).isdigit():
            t[x] = chr(x)

    return cpf.translate(''.join(t), e)


class CPF(object):

    _gen = staticmethod(_gen)
    _translate = staticmethod(_translate)

    def __init__(self, cpf):
        """O argumento cpf pode ser uma string nas formas:

        12345678910
        123.456.789-10

        ou uma lista ou tuple
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0]
        (1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0)

        """

        if isinstance(cpf, basestring):
            if not cpf.isdigit():
                cpf = self._translate(cpf)

        self.cpf = [int(x) for x in cpf]

    def __getitem__(self, index):
        """Retorna o dígito em index como string

        """

        return self.cpf[index]

    def __repr__(self):
        """Retorna uma representação 'real', ou seja:

        eval(repr(cpf)) == cpf

        """

        return "CPF('%s')" % ''.join([str(x) for x in self.cpf])

    def __eq__(self, other):
        """Provê teste de igualdade para números de CPF

        """

        if isinstance(other, CPF):
            return self.cpf == other.cpf
        return False

    def __str__(self):
        """Retorna uma representação do CPF na forma:

        123.456.789-10

        """

        d = iter("..-")
        s = map(str, self.cpf)
        for i in xrange(3, 12, 4):
            s.insert(i, d.next())
        r = ''.join(s)
        return r

    def isValid(self):
        """Valida o número de cpf

        """

        s = self.cpf[:9]
        s.append(self._gen(s))
        s.append(self._gen(s))
        return s == self.cpf[:]
