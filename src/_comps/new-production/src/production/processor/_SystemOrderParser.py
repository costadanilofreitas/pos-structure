import json
import xml.sax.handler
from production.model import ProductionOrder, Item, Comment, StateEvent


def xstr(v):
    return str(v) if v is not None else None


def xbool(v):
    return "true" if (v and str(v).lower() == "true") else "false"


def json_object(value):
    try:
        return json.loads(value)
    except:
        return None


class SystemOrderParser(xml.sax.handler.ContentHandler):
    # [production prop], [<Order> attr], [type converter]
    # <Order> attributes to be merged
    _ORDER_MERGE = (
        ('state', 'state', str),
        ('state_id', 'stateId', int),
        ('originator', 'originatorId', str),
        ('originator_number', 'originatorNumber', int),
        ('pos_id', 'posId', int),
        ('pod_type', 'podType', str),
        ('order_type', 'type', str),
        ('order_subtype', 'subType', str),
        ('sale_type', 'saleTypeDescr', str),
        ('total_gross', 'totalGross', str),
        ('tax_total', 'taxTotal', str),
        ('tagged_lines', 'taggedLines', str),
    )
    # ALL <Order> attributes
    _ORDER_ATTRS = _ORDER_MERGE + (
        ('order_id', 'orderId', int),
        ('period', 'businessPeriod', int),
        ('pod_type', 'podType', str),
        ('created_at', 'createdAt', str),
        ('created_at_gmt', 'createdAtGMT', str),
        ('business_day', 'businessPeriod', str),
        ('operator_id', 'operatorId', int),
        ('multiorder_id', 'multiOrderId', int),
        ('major', 'major', int),
        ('minor', 'minor', int),
        ('session_id', 'sessionId', str),
    )
    # <SaleLine> attributes to be merged
    _LINE_MERGE = (
        ('qty', 'qty', int),
        ('qty_added', 'incQty', int),
        ('qty_voided', 'decQty', int),
        ('multiplied_qty', 'multipliedQty', float),
        ('modifier_label', 'modifierLabel', xstr),
        ('only', 'onlyModifiers', xbool),
        ('properties', 'customProperties', json_object),
    )
    # noinspection PyTypeChecker
    # ALL <SaleLine> attributes
    _LINE_ATTRS = _LINE_MERGE + (
        ('line_number', 'lineNumber', int),
        ('item_id', 'itemId', str),
        ('part_code', 'partCode', int),
        ('description', 'productName', unicode),
        ('item_type', 'itemType', str),
        ('level', 'level', float),
        ('pos_level', 'level', float),
        ('default_qty', 'defaultQty', int),
        ('min_qty', 'minQty', int),
        ('max_qty', 'maxQty', int),
        ('product_priority', 'productPriority', int),
        ('json_tags', 'jsonArrayTags', str),
        ('last_updated', 'lastUpdated', str),
    )
    # <-- ALL <State> attributes
    _STATE_ATTRS = (
        ('state', 'state', str),
        ('state_id', 'stateId', int),
        ('timestamp', 'timestamp', str),
    )

    current_item = None

    def __init__(self, merge_existing=True, user_cache_thread=None):
        self.merge = merge_existing             #: Merge flag
        self.order = None                       #: Contains the resulting order (after the parsing is done)
        self.saved_order = None                 #: Contains the original order (for comparing after parsing)
        self._stack = {}                        #: hierarchical pile of items
        self.current_item = None                #: item being parsed
        self.mainItem = None                    #: level 0 item
        if merge_existing:
            self._missing = set()   #: Set of level-0 items that existed but were not found in the new XML
        self.user_cache_thread = user_cache_thread

    def _create_attributes(self, tuples, attrs):
        d = {}
        for myname, othername, func in tuples:
            value = attrs.get(othername)
            if value or hasattr(func, 'allowempty'):
                d[myname] = func(value)
        return d

    def startElement(self, name, attrs):
        if name == "Order":
            self._parse_order(attrs)
        elif name == "SaleLine":
            self._parse_line(attrs)
        elif name == "State":
            self._parse_state(attrs)
        elif name == "OrderProperty":
            self._parse_property(attrs)
        elif name == "Comment":
            self._parse_comment(attrs)

    def endElement(self, name):
        if self.merge and name == "Order" and self._missing:
            # After all the order has been merged, void items that where not found
            for item in self._missing:
                if item.qty > 0:
                    item.qty = 0
        if self.saved_order is not None:
            # Check if the order has changed
            self.order.modified = self.order.equal_items(self.saved_order) is False

        # Check voided items
        for item in self.order.items:
            if item.qty == 0:
                self._mark_voided(item)
            elif item.voided is True:
                self._clear_voided(item)

    def _mark_voided(self, item):
        item.voided = True
        for sub_item in item.items:
            self._mark_voided(sub_item)

    def _clear_voided(self, item):
        item.voided = False
        for sub_item in item.items:
            self._clear_voided(sub_item)

    def _parse_order(self, attrs):
        if self.order is None:  # Create a new order
            kargs = self._create_attributes(self._ORDER_ATTRS, attrs)
            self.order = ProductionOrder(**kargs)
            self._update_operator_info()
        else:  # Merge attributes
            self.saved_order = self.order.clone()
            order = self.order
            for key, value in self._create_attributes(self._ORDER_MERGE, attrs).items():
                setattr(order, key, value)
            # Populate the list of items, so that we can find "missing ones" later
            self._missing = set(order.items)

    def _update_operator_info(self):
        self._update_operator_id()

        users = self.user_cache_thread.get_users_info() if self.user_cache_thread else []
        if self.order.operator_id in users:
            user = users[self.order.operator_id]
            self._update_operator_name(user.name)
            self._update_operator_level(user.level)

    def _update_operator_id(self):
        self.order.operator_id = self._parse_user_from_session_id() if self._session_id_has_user() else "0"

    def _update_operator_name(self, name):
        self.order.operator_name = name

    def _update_operator_level(self, level):
        self.order.operator_level = level

    def _parse_user_from_session_id(self):
        return self.order.session_id.split("user=")[1].split(",")[0]

    def _session_id_has_user(self):
        return "user=" in self.order.session_id

    def _parse_line(self, attrs):
        item = self._find_item(attrs) if self.merge else None
        if item is None:
            # Create a new item
            kargs = self._create_attributes(self._LINE_ATTRS, attrs)
            item = Item(**kargs)
            item.last_updated += "Z"
            # Put it on its parent list
            level = float(item.level)
            parent = (self.order if level == 0 else (self._stack.get(str(level - 1), None) or self._stack.get(str(float(int(level) - 1)), None)))
            if parent:
                parent.items.append(item)
        else:  # Just merge the attributes
            for key, value in self._create_attributes(self._LINE_MERGE, attrs).items():
                setattr(item, key, value)
        if item.level == 0:
            self.mainItem = item
        elif item.level > 0:
            item.main_item_description = self.mainItem.description

        # Record where we are
        self._stack[str(item.level)] = item
        self.current_item = item

    def _parse_comment(self, attrs):
        """parses a comment from an item"""
        description = attrs.get("comment")
        if description is not None:
            comment = Comment()
            comment.comment_id = attrs.get("commentId")
            comment.text = description
            self.current_item.comments[comment.comment_id] = comment

    def _parse_property(self, attrs):
        key = attrs.get('key')
        value = attrs.get('value')
        if value and self.order:
            self.order.properties[key] = value

    def _find_item(self, attrs):
        """finds a matching item for the given saleline attributes"""
        level, line, item_code = (float(attrs.get("level")), int(attrs.get("lineNumber")), "%s.%s" % (attrs.get("itemId"), attrs.get("partCode")))
        parent = (self.order if level == 0 else (self._stack.get(str(level - 1), None) or self._stack.get(str(float(int(level) - 1)), None)))
        if not parent:
            return None
        for item in parent.items:
            if (item.line_number == line) and (item.item_code == item_code) and (item.level == level):
                self._missing.discard(item)
                return item
        return None  # Not found

    def _parse_state(self, attrs):
        """parses a <State> tag"""
        # Creates a new StateEvent
        kargs = self._create_attributes(self._STATE_ATTRS, attrs)
        new = StateEvent(**kargs)
        for event in self.order.state_history:
            if event.state_id == new.state_id and event.timestamp == new.timestamp:
                break  # This event is already in the order
        else:
            # Event not found... add it!
            self.order.state_history.append(new)
