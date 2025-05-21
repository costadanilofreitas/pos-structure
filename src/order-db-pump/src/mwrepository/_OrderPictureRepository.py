import orderpump.repository
from messagebus import MessageBus, TokenCreator, TokenPriority, Message, DataType, DefaultToken

sale_control_group = "A"

TK_SLCTRL_OMGR_ORDERPICT = TokenCreator.create_token(TokenPriority.low, sale_control_group, "2")


class OrderPictureRepository(orderpump.repository.OrderPictureRepository):
    def __init__(self, message_bus):
        # type: (MessageBus) -> None
        self.message_bus = message_bus

    def get_order_picture(self, order_id):
        reply = self.message_bus.send_message("ORDERMGR1",
                                              Message(TK_SLCTRL_OMGR_ORDERPICT,
                                                      data_type=DataType.param,
                                                      data="\0{}".format(str(order_id)),
                                                      timeout=30000000))

        if reply.token == DefaultToken.TK_SYS_ACK:
            return reply.data.split("\0")[2]
        else:
            raise Exception("Invalid token from OrderManager: {} - {}".format(reply.token, reply.data))
