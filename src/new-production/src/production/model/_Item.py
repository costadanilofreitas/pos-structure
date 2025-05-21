import copy
from datetime import datetime

from typing import List, Dict, Optional

from ._CustomStorage import CustomStorage
from ._TagEvent import TagEvent
from ._TagEventType import TagEventType
import cPickle as pickle


class Item(CustomStorage):

    """ class Item(CustomStorage)
    Represents an item of a production order.
    Instances of this class can be handled and/or modified by any production-box.
    Use the methods write_data, read_data and delete_data in order to modify instances
    in a safe way (avoiding name conflicts).
    """
    # Note - NEVER use mutable objects as the default value here (they are shared by all instances)
    # Mutable objects MUST be created in the constructor
    line_number = 0             #: Number of the "sale line" that represents this item
    item_id = ""                #: The "context" of this item (n levels)
    part_code = ""              #: The product code (one level)
    item_code = ""              #: "item_id.part_code" (n+1 levels)
    description = ""            #: The product name
    qty = 0                     #: Item quantity
    qty_added = 0               #: Total quantity added of this item
    qty_voided = 0              #: Total quantity voided of this item
    qty_modified = 0            #: Quantity modified (for components only)
    default_qty = 0             #: Default quantity of this item (only for sub-items)
    min_qty = 0                 #: Minimum quantity of this item (only for sub-items)
    max_qty = 0                 #: Maximum quantity of this item (only for sub-items)
    multiplied_qty = 0          #: Real (multiplied) item quantity (considers parent quantity)
    item_type = ""              #: Indicates if this item is an OPTION, etc
    level = 0                   #: Item level (0, 1, 2, ...)
    pos_level = 0               #: Item level from the complete order in the POS
    modifier_label = None       #: Optional modifier label
    only = ""                   #: Only modifier
    json_tags = ""  #: product tags as json text
    product_priority = 100  #: sorting items
    voided = False  #: If this item, or a parent item, was voided
    last_updated = ''  #: last time this item was changed in the POS
    main_item_description = ''  #: name of level 0 item
    items = ()  #: List of child items
    comments = ()  #: item comments
    properties = ()  #: List of custom properties from the Order Picture
    prep_time = None
    send_moment = None
    tags = ()
    tag_history = ()
    points = None
    count = 0
    total_count = 0

    def __init__(self, **kargs):
        CustomStorage.__init__(self)
        self.items = list()
        self.comments = dict()
        self.properties = dict()
        self.tags = {}  # type: Dict[str, str]
        self.tag_history = []  # type: List[TagEvent]
        self.joined_items = []  # type: List[Item]
        self.prep_time = None  # type: int
        self.send_moment = None  # type: datetime
        self.points = None  # type: int
        for key, val in kargs.iteritems():
            setattr(self, key, val)
        if not self.item_code:
            self.item_code = "%s.%s" % (self.item_id, self.part_code)

    def __str__(self):
        item_description = " " * int(self.level) + str(self.qty) + " " + self.description.encode("utf-8")
        if self.has_tags():
            item_description += " ["
            for tag in self.tags:
                item_description += tag.encode("utf-8") + ", "
            item_description = item_description[:-2]
            item_description += "]"

        item_description += " [" + self.get_line_id() + "]"
        item_description += " {}".format(self.item_type)
        if self.prep_time is not None:
            item_description += " PrepTime: " + str(self.prep_time)
        if self.send_moment is not None:
            item_description += " SendMoment: " + str(self.send_moment.isoformat())
        if self.points is not None:
            item_description += " Points: " + str(self.points)
        if len(self.joined_items) > 0:
            item_description += "\nJoined Items:"
            for joined_item in self.joined_items:
                item_description += "\n" + str(joined_item)
        for son in self.items:
            item_description += "\n" + str(son)

        return item_description

    def __repr__(self):
        return "(%s) %s" % (object.__repr__(self), str(self))

    def get_tags(self):
        return self.tags.keys()

    def has_tags(self):
        return len(self.tags)

    def has_tag(self, tag):
        return tag in self.tags

    def has_some_tag(self, tags):
        if self.qty == 0:
            return True

        for tag in tags:
            if tag in self.tags:
                break
        else:
            return False

        return True

    def does_not_have_tag(self, tag):
        return tag not in self.tags

    def add_view(self, kds_view):
        if 'kds_view' in self.tags.keys() and self.tags['kds_view'] == kds_view:
            return False

        self.tags['kds_view'] = kds_view
        self.tag_history.append(TagEvent(kds_view, TagEventType.added, datetime.now()))
        return True

    def add_tag(self, tag):
        self.tags[tag] = tag
        self.tag_history.append(TagEvent(tag, TagEventType.added, datetime.now()))

    def remove_tag(self, tag):
        if tag in self.tags:
            del self.tags[tag]
            self.tag_history.append(TagEvent(tag, TagEventType.removed, datetime.now()))

    def toggle_tag(self, tag):
        if tag in self.tags:
            self.remove_tag(tag)
        else:
            self.add_tag(tag)

    def is_product(self):
        return self.item_type in ("PRODUCT", "CANADD")

    def is_ingredient(self):
        return self.item_type == "INGREDIENT"

    def is_served(self):
        if self.is_product():
            return self.has_tag("served")
        else:
            for son in self.items:
                if not son.is_served():
                    return False
            return True

    def all_has_at_least_one_tag(self, tags):
        if self.qty == 0:
            return True

        if self.is_product():
            for tag in tags:
                if tag in self.tags:
                    break
            else:
                return False

        for son in self.items:
            if not son.all_has_at_least_one_tag(tags):
                return False

        return True

    def at_least_one_has_at_least_one_tag(self, allowed_tags):
        if self.qty == 0:
            return True
        if self.is_product():
            if not self.tags:
                return True

            has_item = False
            for tag in self.tags:
                if tag in allowed_tags:
                    has_item = True

            return has_item
        else:
            for son in self.items:
                if son.at_least_one_has_at_least_one_tag(allowed_tags):
                    return True
            return False

    def get_last_tag_time(self, tag):
        # type: (str) -> Optional[datetime]
        if self.is_product():
            for event in reversed(self.tag_history):
                if event.tag == tag and event.action == TagEventType.added:
                    return event.date
            return None
        else:
            last_time = None
            for son in self.items:
                son_last_time = son.get_last_tag_time(tag)
                if son_last_time is not None and (last_time is None or son_last_time > last_time):
                    last_time = son_last_time
            return last_time

    def clone(self, clear_data=False):
        return pickle.loads(pickle.dumps(self, -1))


    # Private Methods
    def get_line_id(self):
        part_code = str(self.part_code)
        if hasattr(self, "original_part_code"):
            part_code = str(self.original_part_code)
        level = str(int(self.level))
        if hasattr(self, "original_level"):
            level = str(int(self.original_level))

        return str(self.line_number) + "-" + self.item_id + "-" + level + "-" + part_code
