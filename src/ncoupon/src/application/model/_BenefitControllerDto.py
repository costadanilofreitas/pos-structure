from datetime import datetime

from application.model import BenefitAppliers, OperationDescription
from typing import Optional


class BenefitControllerDto(object):

    def __init__(self):
        # type: () -> None

        self.benefit_id = None  # type: Optional[str]
        self.pos_id = None  # type: Optional[int]
        self.operation_description = None  # type: Optional[OperationDescription]
        self.benefit_applier = None  # type: Optional[BenefitAppliers]
        self.retry_quantity = None  # type: Optional[int]
        self.last_retry_date_utc = None  # type: Optional[datetime]
