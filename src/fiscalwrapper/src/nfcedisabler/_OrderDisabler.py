# -*- coding: utf-8 -*-

import time
from xml.etree import cElementTree as eTree

from _ModuleLogger import logger
from old_helper import OrderTaker
from nfcedisabler import NfceDisabler, OrderRepository
from pos_model import OrderKey
from posot import OrderTakerException
from requests.exceptions import RequestException


class OrderDisabler(object):
    def __init__(self, order_repository, nfce_disabler, order_taker):
        # type: (OrderRepository, NfceDisabler, OrderTaker) -> None
        self.order_repository = order_repository
        self.nfce_disabler = nfce_disabler
        self.order_taker = order_taker

    def disable_all_orders(self, ):
        logger.info("Inutilizando notas")
        order_keys = self.order_repository.get_all_orders_to_disable()
        logger.info("Orders para inutilizar: {0}".format(len(order_keys)))

        for order_key in order_keys:  # type: OrderKey
            try:
                logger.info("Inutilizando order: {0}".format(order_key.order_id))
                order_xml = self.order_taker.get_order_picture(order_key.pos_id, order_key.order_id)
                logger.info("Iniciando inutilização da order {0} do pos {1}".format(order_key.order_id, order_key.pos_id))
                self.nfce_disabler.disable_fiscal_number(eTree.XML(order_xml))
                self.order_repository.mark_order_disabled(order_key.pos_id, order_key.order_id)
                logger.info("Order inutilizada com sucesso: {0}".format(order_key.order_id))
            except RequestException as _:
                logger.exception("Erro de Conexao com a Sefaz tentando inutulizar nota, tentaremos novamente...")
            except OrderTakerException:
                logger.exception("Order Taker Error, tentaremos novamente...")
            except BaseException as _:
                logger.exception("Erro inutilizando nota, verifique o Layout e os parametros enviados pela Sefaz, não tentaremos novamente.")
                self.order_repository.mark_order_not_disabled(order_key.pos_id, order_key.order_id)
            finally:
                time.sleep(5)
