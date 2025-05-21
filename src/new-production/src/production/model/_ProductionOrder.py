import cPickle as pickle
from datetime import datetime

import pytz
from production.model import ProdStates
from typing import List, Optional
from tzlocal import get_localzone

from ._CustomStorage import CustomStorage
from ._Item import Item
from ._StateEvent import StateEvent
from ._TagEvent import TagEvent

time_offset = datetime.now() - datetime.utcnow()


class ProductionOrder(CustomStorage):

    """ class ProductionOrder(CustomStorage)
    Represents a production order.
    Instances of this class can be handled and/or modified by any production-box.
    Use the methods write_data, read_data and delete_data in order to modify instances
    in a safe way (avoiding name conflicts).
    """
    # Note - NEVER use mutable objects as the default value here (they are shared by all instances)
    # Mutable objects MUST be created in the constructor
    order_id = 0  #: Order identification number
    state = ""  #: Current order state ("IN_PROGRESS", "TOTALED", ..etc..)
    state_id = 0  #: Current state number
    prod_sequence = ""  #: Production sequence number used to sort orders - SHOULD ONLY BE SET ON A CLONED ORDER
    pos_id = 0  #: Current order POS id
    originator = ""  #: Name of the order originator
    pod_type = ""  #: The point-of-distribution of this order ("FC", "DT")
    created_at = ""  #: Local timestamp of the "order start" (in database format: YYYY-MM-DDTHH:MM:SS[.SSS])
    created_at_gmt = ""  #: UTC timestamp of the "order start" (in database format: YYYY-MM-DDTHH:MM:SS[.SSS])
    operator_id = 0  #: ID of the operator who took this order
    operator_name = ""
    operator_level = 0
    order_type = ""  #: Order type ("SALE", "REFUND", ..etc..)
    order_subtype = ""  #: Order sub-type (script-defined, and generally not known by the kernel)
    sale_type = ""  #: Current sale type (EAT_IN, TAKE_OUT, etc...)
    total_gross = ""  #: Order total gross amount
    product_priority = 0  #: Product display priority
    state_history = None  #: List of StateEvent objects of this order
    items = None  #: Level-0 items of this order
    properties = None  #: List of OrderProperties from the Order Picture
    cloned = False  #: Indicates if this is a cloned instance of an order
    purged = False  #: Indicates if this order has just been purged from the database
    buzz_flag = False  #: Indicates if this order should generated an audible alert
    session_id = ""  #: Session ID for this order
    tagged_lines = ""  #: List of tagged lines separated by comma
    display_time = ""  #: Time to be displayed in the KDS
    show_timer = True  #: Whether the timer should be displayed for this order
    tagged_timestamp = None  #: Time when the whole order was tagged
    modified_after_display = False  #: If the order was modified after being displayed in the KDS
    recalled = False  #: Whether this order was called back after being served
    first_processing = False  #: Indicates if this is the first processing time
    reprocessed = False  #: Indicates if this order is being reprocessed
    max_prep_time = None
    points = None
    skip_course = False
    round_robin_path = ""
    tags = None
    _prod_state_history = None

    def __init__(self, **kargs):
        super(ProductionOrder, self).__init__()
        self.state_history = []  # type: List[StateEvent]
        self.items = []  # type: List[Item]
        self.properties = {}
        self.undo_list = []  # type: List[ChangeProdStateUndoCommand]
        self.tag_history = []  # type: List[TagEvent]
        self.points = None
        self._prod_state_history = []  # type: List[StateEvent]
        self.tags = {}
        for key, val in kargs.items():
            setattr(self, key, val)

    @property
    def prod_state(self):
        if self._prod_state_history:
            return self._prod_state_history[-1].prod_state
        return ProdStates.NORMAL

    @prod_state.setter
    def prod_state(self, new_state):
        date_now = datetime.now()
        timezone = pytz.timezone(get_localzone().zone)
        date_now_tz = timezone.localize(date_now).strftime("%Y-%m-%dT%H:%M:%S%z")
        self._prod_state_history.append(StateEvent(prod_state=new_state, timestamp=date_now_tz))

    @property
    def prod_state_last_update(self):
        if self._prod_state_history:
            return self._prod_state_history[-1].timestamp
        return None

    @property
    def prod_state_history(self):
        return tuple(self._prod_state_history or [])

    @property
    def display_time_gmt(self):
        try:
            timestamp_date = datetime.strptime(self.display_time[0:19], "%Y-%m-%dT%H:%M:%S")
            gmt_date = timestamp_date - time_offset
            return gmt_date.isoformat() + "Z"
        except ValueError:
            return ""

    def __str__(self):
        ret = ""
        for item in self.items:
            ret += str(item) + "\n"

        return "Id: {}, ProdState: {}, Sequence: {}, SaleType: {}, State: {}{}{}{}\nItems:\n{}". \
            format(self.order_id,
                   self.prod_state,
                   self.prod_sequence,
                   self.sale_type,
                   self.state,
                   ", MaxPrepTime: {}".format(self.max_prep_time) if self.max_prep_time else "",
                   ", Points: {}".format(self.points) if self.points is not None else "",
                   ", RoundRobinPath: {}".format(self.round_robin_path) if hasattr(self, "round_robin_path") else "",
                   ret)

    def __repr__(self):
        return "(%s) %s" % (object.__repr__(self), str(self))

    def __eq__(self, other):
        # type: (ProductionOrder) -> bool
        prop_list_to_compare = [
            "order_id",
            "state_history",
            "items",
            "prod_state",
            "tags",
            "tagged_lines",
            "display_time"
        ]

        def _dump_prop(order, prop):
            return pickle.dumps(getattr(order, prop), pickle.HIGHEST_PROTOCOL)

        if not other:
            return False

        if not isinstance(other, ProductionOrder):
            return NotImplemented

        return not any(_dump_prop(other, p) != _dump_prop(self, p) for p in prop_list_to_compare)

    def add_tag(self, line_id, tag):
        item = self.get_item_by_line_id(line_id)
        if item is None:
            return

        item.add_tag(tag)
        self.add_sons_tags(item, tag)

    def add_sons_tags(self, item, tag):
        for son in item.items:
            son.add_tag(tag)
            if son.items:
                self.add_sons_tags(son, tag)

    def remove_tag(self, line_id, tag):
        item = self.get_item_by_line_id(line_id)
        if item is None:
            return

        item.remove_tag(tag)
        self.remove_sons_tags(item, tag)

    def remove_sons_tags(self, item, tag):
        for son in item.items:
            son.remove_tag(tag)
            if son.items:
                self.remove_sons_tags(son, tag)

    def toggle_tag(self, line_id, tag):
        item = self.get_item_by_line_id(line_id)
        if item is None:
            return
        item.toggle_tag(tag)

    def build_tagged_lines(self):
        ret = ""
        for item in self.items:
            ret += self.build_item_tags(item)
        if ret != "":
            ret = ret[:-1]

        return ret

    def build_item_tags(self, item):
        ret = ""
        if item.has_tags():
            line_id = item.get_line_id()
            for tag in item.get_tags():
                ret += line_id + "=" + tag + ","
        for son in item.items:
            ret += self.build_item_tags(son)

        return ret

    def get_item_by_line_id(self, line_id):
        # type: (str) -> Optional[Item]
        for item in self.items:
            found = self.get_item_or_son(line_id, item)
            if found is not None:
                return found
        return None

    def get_item_or_son(self, line_id, item):
        if item.get_line_id() == line_id:
            return item

        for son in item.items:
            found = self.get_item_or_son(line_id, son)
            if found is not None:
                return found

        return None

    def get_item(self, item):
        # type: (Item) -> Optional[Item]
        for current_item in self.items:
            if current_item.line_number == item.line_number and current_item.item_code == item.item_code:
                return current_item
        return None

    def clone(self):
        """ order.clone -> ProductionOrder
        Creates a clone of this ProductionOrder.
        The cloned instance can be safely modified and/or stored for any purpose, without
        affecting the original instance.
        Any production box that puts orders into a "output queue" should clone the order
        first, otherwise the instance could be further modified by another production box.
        @return {ProductionOrder} - the cloned instance
        """
        return pickle.loads(pickle.dumps(self, -1))

    def equal_items(self, order):
        if order is None:
            return False

        if isinstance(order, ProductionOrder) is False:
            return False

        for item in order.items:
            saved_item = self.get_item(item)
            if saved_item is None:
                return False
            if compare_items(item, saved_item, is_level0=True) is False:
                return False

        for item in self.items:
            other_item = order.get_item(item)
            if other_item is None:
                return False
            if compare_items(item, other_item, is_level0=True) is False:
                return False
        return True

    # Private methods
    def get_tagged_lines(self):
        if self.tagged_lines == '':
            return set()

        return set([x for x in self.tagged_lines.split(',')])


def compare_items(item1, item2, is_level0=False):
    """ compares two production items, and returns True if they can be consolidated """
    if item1 is None or item2 is None:
        return False
    items1, items2 = real_items(item1.items), real_items(item2.items)
    if (item1.part_code == item2.part_code) and (len(items1) == len(items2)) and (item1.level == item2.level):
        if (not is_level0) and item1.qty != item2.qty:
            return False  # Only consider the quantity for non-level0
        if compare_comments(item1, item2) is False:
            # Items have different comments
            return False
        if items1 and not all(map(compare_items, items1, items2)):
            return False
        return True


def compare_comments(item1, item2):
    if item1 is None or item2 is None:
        return False
    if item1.comments is None and item2.comments is None:
        return True
    if (item1.comments is None and item2.comments is not None) or (item1.comments is not None and item2.comments is None):
        return False
    if item1.comments.keys() != item2.comments.keys():
        return False

    for key in item1.comments:
        item1_comment = item1.comments[key]
        item2_comment = item2.comments[key]
        if item1_comment.comment_id != item2_comment.comment_id:
            return False
        if item1_comment.text != item2_comment.text:
            return False

    return True


def real_items(item_list):
    return [item for item in item_list if (item.item_type not in ("INGREDIENT", "CANADD")) or (item.default_qty != item.qty) or (item.only == "true")]
