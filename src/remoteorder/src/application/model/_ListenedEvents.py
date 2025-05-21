# -*- coding: utf-8 -*-


class ListenedEvents(object):
    # Evento para tratar itens em ruptura
    RupturaDataUpdated = "RupturaDataUpdated"
    # Evento recebido quando o serviço remoto confirma a conclusão do tratamento dos últimos dados de ruptura
    RuptureAck = "RuptureAck"
    # Evento recebido quando uma Order deve ser guardada na loja
    LogisticOrderConfirm = "LogisticOrderConfirm"
    # Evento para o componente de logística para atualziar o tempo de entrega de uma order
    UpdatePickupTime = "UpdatePickupTime"
    # Evento com o novo tempo de entrega da uma Order
    LogisticPickupTimeUpdated = "LogisticPickupTimeUpdated"
    # Evento recebido do servidor quando a atualização do status foi recebida com sucesso
    SacStoreStatusUpdateAck = "SacStoreStatusUpdateAck"
    # Evento que o Sac envia solicitando as informações do monitor de expedição da loja
    SacOrderMonitorRequest = "SacOrderMonitorRequest"
    # Evento indicando que o Sac cancelou um pedido e o mesmo precisa ser cancelado na loja
    SacOrderCancel = "SacOrderCancel"
    # Evento indicando que o OrderManager deseja receber o Menu da loja
    OrderManagerMenuRequest = "OrderManagerMenuRequest"
    # Evento recebido quando o serviço remoto confirmou que um pedido foi integrado
    PosOrderConfirmAck = "PosOrderConfirmAck"
    # Evento recebido quando o serviço remoto confirmou que um pedido foi produzido
    PosOrderProducedAck = "PosOrderProducedAck"
    # Evento de Ping recebido pelo servico remoto
    Ping = "Ping"

    # Evento de recebido pelo serviço de logística informando que a busca foi iniciada
    LogisticSearching = "LogisticSearching"
    # Evento de recebido pelo serviço de logística informando que a busca foi efetuada com sucesso
    LogisticFound = "LogisticFound"
    # Evento de recebido pelo serviço de logística informando que não foi encontrada
    LogisticNotFound = "LogisticNotFound"
    # Evento de recebido pelo serviço de logística informando que a logistica foi cancelada
    LogisticCanceled = "LogisticCanceled"
    # Evento de recebido pelo serviço de logística informando que a logistica foi finalizadas
    LogisticFinished = "LogisticFinished"
    # Evento de recebido pelo serviço de logística informando que a logistica foi confirmada
    PosLogisticConfirmAck = "PosLogisticConfirmAck"

    KdsOrderProduced = "KdsOrderProduced"
    PosOrderReadyToDeliveryAck = "PosOrderReadyToDeliveryAck"

    # Evento recebido pelo serviço de logística informando que o pedido saiu para entrega
    OrderLogisticDispatched = "OrderLogisticDispatched"
    # Evento para confirmação que o servidor recebeu o evento do pedido que saiu para entrega
    PosLogisticDispatchedAck = "PosLogisticDispatchedAck"
    # Evento para confirmação que o servidor recebeu o evento do pedido entregue
    PosLogisticDeliveredAck = "PosLogisticDeliveredAck"
    # Evento de recebido pelo serviço de logística informando que o pedido foi entregue
    OrderLogisticDelivered = "OrderLogisticDelivered"
