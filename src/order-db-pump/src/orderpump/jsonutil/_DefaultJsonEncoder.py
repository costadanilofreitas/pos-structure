from datetime import datetime
from decimal import Decimal
from json import JSONEncoder


class DefaultJsonEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)

        if isinstance(o, datetime):
            return o.isoformat()

        return super(DefaultJsonEncoder, self).default(o)
