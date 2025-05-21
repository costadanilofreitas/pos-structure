from StringIO import StringIO
from datetime import datetime
from xml.sax import saxutils

from production.model import ProductionOrder, Item, StateEvent


def _validxml(name, clazz):
    """private - checks if an attribute should be written in the XML"""
    if not name.startswith("_"):
        value = getattr(clazz, name)
        if (not hasattr(value, '__iter__')) and (not callable(value)):
            return True
    return False


def utf(value):
    """retrieves the utf8 representation of a value"""
    return value.encode("UTF-8") if isinstance(value, unicode) else str(value)


class OrderXml(object):

    """ class OrderXml(object)
    Class used to generate an XML representation of a ProductionOrder
    """
    _OUT_TYPES = (str, unicode, int, long, float, bool)
    _ORDER_ATTRS = [name for name in dir(ProductionOrder) if _validxml(name, ProductionOrder)]
    # level attribute generated when writing the xml to avoid gaps in the sequence
    _ITEM_ATTRS = [name for name in dir(Item) if _validxml(name, Item) and name != 'level']
    _EVENT_ATTRS = [name for name in dir(StateEvent) if _validxml(name, StateEvent)]

    def to_xml(self, order):
        # type: (ProductionOrder) -> str
        """ obj.to_xml(order) -> str
        Creates and XML representation of the given order.
        @param order: {ProductionOrder} - the production box to generate XML from
        @return {str} - The XML output
        """
        order.tagged_lines = order.build_tagged_lines()
        io = StringIO()
        io.write('<?xml version="1.0" encoding="UTF-8"?>\n<ProductionOrder')
        self._write_attributes(io, self._ORDER_ATTRS, order)
        io.write('>\n')
        # Write custom storage
        self._write_custom_storage(io, order, 1)
        # Write items recursivelly
        io.write('  <Items>\n')
        for item in order.items:
            self._write_item(io, item, 0, 2)
        io.write('  </Items>\n')
        # Write the order properties
        io.write('  <Properties>\n')
        for key in order.properties:
            self._write_property(io, key, order.properties[key], 2)
        io.write('  </Properties>\n')
        # Write the state history
        io.write('  <StateHistory>\n')
        for event in order.state_history:
            io.write('    <StateEvent')
            self._write_attributes(io, self._EVENT_ATTRS, event)
            io.write('/>\n')
        io.write('  </StateHistory>\n')
        io.write('  <ProdStateHistory>\n')
        for prod_state in order.prod_state_history:
            io.write('    <ProdState')
            self._write_attributes(io, self._EVENT_ATTRS, prod_state)
            io.write('/>\n')
        io.write('  </ProdStateHistory>\n')
        io.write('</ProductionOrder>')
        return io.getvalue()

    def _write_comments(self, io, item, level):
        level = int(level)
        level += 1
        for comment_id in item.comments:
            ident = (level * '  ')
            comment = item.comments[comment_id]
            io.write('{0}<Comment id="{1}" comment={2}/>\n'.format(ident, comment_id, utf(saxutils.quoteattr(comment.text))))

    def _write_item(self, io, item, item_level, indent_level):
        """private - writes an Item recursivelly"""
        indent_space = (indent_level * '  ')
        io.write('%s<Item' % indent_space)
        io.write(' %s=%s' % ('level', saxutils.quoteattr(str(item_level))))
        self._write_attributes(io, self._ITEM_ATTRS, item)
        io.write('>\n')
        indent_level += 1
        # write custom item properties
        if len(item.properties) > 0:
            prop_space = (indent_level * '  ')
            io.write('%s<Properties>\n' % prop_space)
            prop_level = indent_level + 1
            for key in item.properties:
                self._write_property(io, key, item.properties[key], prop_level)
            io.write('%s</Properties>\n' % prop_space)

        if len(item.tags) > 0:
            tags_space = (indent_level * '  ')
            tag_space = ((indent_level + 1) * '  ')
            io.write('{}<Tags>\n'.format(tags_space))
            for key in item.tags:
                io.write('{}<Tag name="{}"/>\n'.format(tag_space, item.tags[key]))
            io.write('{}</Tags>\n'.format(tags_space))

        if len(item.tag_history) > 0:
            tags_space = (indent_level * '  ')
            tag_space = ((indent_level + 1) * '  ')
            io.write('{}<TagHistory>\n'.format(tags_space))
            for event in item.tag_history:
                io.write('{}<TagEvent tag="{}" action="{}" timestamp="{}"/>\n'.format(
                    tag_space, event.tag, event.action.name, event.date.isoformat()))
            io.write('{}</TagHistory>\n'.format(tags_space))

        # Write custom storage
        self._write_custom_storage(io, item, indent_level)
        # Write comments
        self._write_comments(io, item, indent_level)
        # Write sub-items recursivelly
        item_level += 1
        for subitem in item.items:
            self._write_item(io, subitem, item_level, indent_level)
        io.write('%s</Item>\n' % indent_space)

    def _write_property(self, io, key, value, level):
        """private - writes an Item recursivelly"""
        ident = (int(level) * '  ')
        io.write('{0}<Property key="{1}" value={2}/>\n'.format(ident, key, utf(saxutils.quoteattr(value))))

    def _write_attributes(self, io, names, obj):
        """private - writes a list of attributes"""
        out_types = self._OUT_TYPES
        quoteattr = saxutils.quoteattr
        for name in names:
            value = getattr(obj, name)
            if type(value) in out_types:
                io.write(' %s=%s' % (name, quoteattr(utf(value))))
            elif isinstance(value, datetime):
                io.write(' %s=%s' % (name, quoteattr(value.isoformat())))

    def _write_custom_storage(self, io, obj, level):
        """private - writes any custom storage data of an object"""
        storage = obj._storage
        ident = (int(level) * '  ')
        quoteattr = saxutils.quoteattr
        for context, dic in storage.iteritems():
            context = quoteattr(utf(context))
            for key, value in dic.iteritems():
                if not key.startswith("_"):
                    key = quoteattr(utf(key))
                    if type(value) in (str, unicode):
                        value = utf(value)
                    else:
                        value = repr(value).decode('string_escape')
                    value = quoteattr(utf(value))
                    io.write('%s<Custom context=%s key=%s value=%s/>\n' % (ident, context, key, value))
