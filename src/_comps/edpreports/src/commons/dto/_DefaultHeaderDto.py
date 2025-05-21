from typing import Optional  # noqa
from datetime import datetime


class DefaultHeaderDto(object):
    def __init__(self,
                 report_type,
                 initial_date,
                 end_date, pos,
                 operator_id,
                 operator_name,
                 store_code,
                 generated_time):
        # type: (str, datetime, datetime, Optional[int], Optional[str], Optional[str], str, datetime) -> None
        self.report_type = report_type
        self.initial_date = initial_date
        self.end_date = end_date
        self.pos = pos
        self.operator_id = operator_id
        self.operator_name = operator_name
        self.store_code = store_code
        self.generated_time = generated_time
