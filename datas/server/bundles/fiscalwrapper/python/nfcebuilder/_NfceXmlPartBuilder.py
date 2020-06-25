from abc import ABCMeta, abstractmethod

from pos_model import Order
from typing import Dict, Any


class NfceXmlPartBuilder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        raise NotImplementedError()
