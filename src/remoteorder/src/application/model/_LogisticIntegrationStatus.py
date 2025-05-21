class LogisticIntegrationStatus(object):
    WAITING = "Waiting"
    NEED_SEARCH = "NeedSearch"
    SEARCHING = "Searching"
    WAITING_SEARCHING_RESPONSE = "WaitingSearchingResponse"
    WAITING_CONFIRM_RESPONSE = "WaitingConfirmResponse"
    WAITING_CANCEL_RESPONSE = "WaitingCancelResponse"
    WAITING_LOGISTIC_CANCEL_RESPONSE = "WaitingLogisticCancelResponse"
    CANCELED = "Canceled"
    NOT_FOUND = "NotFound"
    
    SENT = "Sent"
    RECEIVED = "Received"
    CONFIRMED = "Confirmed"
    FINISHED = "Finished"

    @staticmethod
    def is_final_status(status):
        if status == LogisticIntegrationStatus.SENT:
            return True
        
        if status == LogisticIntegrationStatus.CONFIRMED:
            return True
        
        if status == LogisticIntegrationStatus.RECEIVED:
            return True
        
        if status == LogisticIntegrationStatus.FINISHED:
            return True
        
        return False
