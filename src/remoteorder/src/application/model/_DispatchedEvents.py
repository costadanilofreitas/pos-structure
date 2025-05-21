# -*- coding: utf-8 -*-
import json
import logging
from logging import Logger

from ._RemoteOrderModelJsonEncoder import RemoteOrderModelJsonEncoder
from typing import Optional, Union

remote_order_logger = logging.getLogger("RemoteOrder")


class DispatchedEvents(object):

    def __init__(self, mb_context):
        self.mb_context = mb_context

    # Evento informando que a Order previamente recebida foi confirmada pela loja
    PosOrderConfirm = "PosOrderConfirm"
    # Evento informando que a Order previamente recebida pela loja
    PosOrderReceived = "PosOrderReceived"
    # Evento informando que a Order previamente recebida não foi processada corretamente pela loja
    PosOrderCancel = "PosOrderCancel"
    # Evento que o POS envia ao SAC indicando que a order foi cancelada com sucesso
    PosOrderCancelAck = "PosOrderCancelAck"
    # Evento que o POS envia ao SAC indicando que a order Não foi cancelada
    PosOrderCancelError = "PosOrderCancelError"
    # Evento sinalizando que ocorreu um erro no evento de atualização de PickUp Time
    PosErrorInPickupOrder = "PosErrorInPickupOrder"
    # Evento que o POS envia indicando que o pickup.time foi atualizado com sucesso
    PosPickupTimeUpdated = "PosPickupTimeUpdated"
    # Evento criado pelo POS para indicar que houve diferença de preço em uma order
    PosPriceWarning = "PosPriceWarning"
    # Evento enviado quando o status da loja muda
    PosStoreStatusUpdate = "PosStoreStatusUpdate"
    # Evento que a loja envia com as informações do monitor de expedição
    PosOrderMonitorResponse = "PosOrderMonitorResponse"
    # Evento que o POS envia com o menu da loja
    PosMenuResponse = "PosMenuResposne"
    # Evento que o POS envia quando um pedido for produzido
    PosOrderProduced = "PosOrderProduced"
    # Evento que o POS envia para o SAC para notificar mudança na ruptura de itens
    PosRupture = "Rupture"
    # Evento que o POS envia quando abre a loja
    PosStoreOpened = "PosStoreOpened"
    # Evento que o POS envia quando fecha a loja
    PosStoreClosed = "PosStoreClosed"
    # Evento para o componente de logística para atualizar o tempo de entrega de uma order
    PosUpdatePickupTime = "PosUpdatePickupTime"
    # Evento disparado pelo POS para servico remoto avisando que o ping foi escutado
    PosPong = "Pong"

    # Evento para busca de Logistica
    LogisticRequest = "LogisticRequest"
    # Evento para cancelamento de Logistica
    LogisticCancel = "LogisticCancel"
    # Evento para confirmação de Logistica
    PosLogisticConfirm = "PosLogisticConfirm"
    # Evento para confirmação de Logistica encontrada
    LogisticFoundAck = "LogisticFoundAck"
    # Evento para confirmação de Logistica finalizada
    LogisticFinishedAck = "LogisticFinishedAck"
    # Evento para notificação que o pedido já foi produzido
    PosOrderReadyToDelivery = "PosOrderReadyToDelivery"
    # Evento enviado para o serviço de logística informando que o evento OrderLogisticDispatched foi processado
    OrderLogisticDispatchedAck = "OrderLogisticDispatchedAck"
    # Evento para notificação que o pedido já foi enviado
    PosLogisticDispatched = "PosLogisticDispatched"
    # Evento para notificação que o pedido já foi entregue
    PosLogisticDelivered = "PosLogisticDelivered"
    # Evento enviado para o serviço de logística informando que o evento OrderLogisticDelivered foi processado
    OrderLogisticDeliveredAck = "OrderLogisticDeliveredAck"

    def send_event(self, subject, evt_type="", data="", logger=remote_order_logger):
        # type: (DispatchedEvents, Optional[str], Optional[str], Optional[Union[Logger, None]]) -> None

        self.mb_context.MB_EasyEvtSend(subject, evt_type, data)

        if logger is None:
            return
        logger.info("Event dispatched: {}".format(subject))

    def send_pos_order_cancel_to_server(self, order_error):
        order_error_json = json.dumps(order_error, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
        self.send_event(self.PosOrderCancel, "", order_error_json)
