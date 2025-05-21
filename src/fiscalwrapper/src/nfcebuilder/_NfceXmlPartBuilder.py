# -*- coding: utf-8 -*-

from typing import Dict, Any
from abc import ABCMeta, abstractmethod
from pos_model import Order


class NfceXmlPartBuilder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        raise NotImplementedError()
