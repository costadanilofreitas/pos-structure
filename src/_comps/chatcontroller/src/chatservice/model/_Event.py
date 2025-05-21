# -*- coding: utf-8 -*-

class Event(object):
    # Evento que indica que uma nova mensagem do SAC está disponível
    SAC_CHAT_MESSAGE_NEW = "SacChatMessageNew"
    # Evento para informar o servidor que novas mensagens foram enviadas pela loja
    POS_CHAT_MESSAGE_NEW = "PosChatMessageNew"
    # Evento que o servidor envia para a loja para informar que as mensagens enviadas pela loja foram recebidas
    SAC_CHAT_MESSAGE_ACK = "SacChatMessageAck"
    # Evento que a loja envia para indicar que as mensagens do SAC foram recebidas com sucesso
    POS_CHAT_MESSAGE_ACK = "PosChatMessageAck"
