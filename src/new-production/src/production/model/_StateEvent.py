import json
from io import StringIO
from datetime import datetime

time_offset = datetime.now() - datetime.utcnow()


class StateEvent(object):

    """ class StateEvent(object)
    Represents an order state change
    """
    # Note - NEVER use mutable objects as the default value here (they are shared by all instances)
    # Mutable objects MUST be created in the constructor
    prod_state = None   #: {str} - Production state name
    state = None        #: {str} - State name
    state_id = None     #: {int} - State id
    line_id = None      #: {int} - line identification (line number or line_number-item_id-level-part_code)
    item_tag = None     #: {str} - item tag name
    timestamp = ""      #: {str} - Timestamp (database format, UTC)

    @property
    def timestamp_gmt(self):
        try:
            timestamp_date = datetime.strptime(self.timestamp[0:19], "%Y-%m-%dT%H:%M:%S")
            gmt_date = timestamp_date - time_offset
            return gmt_date.isoformat()
        except ValueError:
            return ""

    def __init__(self, **kargs):
        for key, val in kargs.iteritems():
            setattr(self, key, val)
        if not self.timestamp:
            raise ValueError('timestamp attribute is mandatory')

    def __str__(self):
        buf = StringIO()
        if self.prod_state is not None:
            buf.write('Production State:{} '.format(self.prod_state))
        if self.state is not None:
            buf.write('POS State:{} '.format(self.state))
        if self.line_id is not None:
            buf.write('Line:{} '.format(self.line_id))
        if self.item_tag is not None:
            buf.write('Item Tag:{} '.format(self.item_tag))
        buf.write('Time={}'.format(self.timestamp))

        return buf.getvalue()

    def __repr__(self):
        result = {}
        if self.prod_state is not None:
            result['prod_state'] = self.prod_state
        if self.state is not None:
            result['state'] = self.state
        if self.state_id is not None:
            result['state_id'] = self.state_id
        if self.line_id is not None:
            result['line_id'] = self.line_id
        if self.item_tag is not None:
            result['item_tag'] = self.item_tag
        result['timestamp'] = self.timestamp

        return json.dumps(result)
