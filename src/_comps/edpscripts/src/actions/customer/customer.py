from msgbus import FM_PARAM, TK_SYS_ACK, TK_SYS_NAK
from bustoken import create_token, MSGPRT_LOW

from utilfunctions import json_serialize

from .model import AddCustomerRequest

from .. import mb_context

TK_CUSTOMER_ADD_CUSTOMER = create_token(MSGPRT_LOW, "96", "1")
TK_CUSTOMER_GET_CUSTOMER = create_token(MSGPRT_LOW, "96", "2")
TK_CUSTOMER_UPDATE_CUSTOMER = create_token(MSGPRT_LOW, "96", "3")
TK_CUSTOMER_DELETE_CUSTOMER = create_token(MSGPRT_LOW, "96", "4")


class Customer(object):
    @staticmethod
    def add_customer(add_customer_request):
        # type: (AddCustomerRequest) -> None
        
        data = json_serialize(add_customer_request)
        response = mb_context.MB_EasySendMessage("Customer", TK_CUSTOMER_ADD_CUSTOMER, FM_PARAM, data)

        if response.token == TK_SYS_NAK:
            raise Exception("Error")

    @staticmethod
    def get_customer(phone):
        # type: (str) -> object

        response = mb_context.MB_EasySendMessage("Customer", TK_CUSTOMER_GET_CUSTOMER, FM_PARAM, str(phone))
    
        if response.token == TK_SYS_ACK:
            return response.data
    
        return None

    @staticmethod
    def update_customer(add_customer_request):
        # type: (AddCustomerRequest) -> None
    
        data = json_serialize(add_customer_request)
        response = mb_context.MB_EasySendMessage("Customer", TK_CUSTOMER_UPDATE_CUSTOMER, FM_PARAM, data)
    
        if response.token == TK_SYS_NAK:
            raise Exception("Error")
