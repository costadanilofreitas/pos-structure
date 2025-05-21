# -*- coding: utf-8 -*-
# Module name: cfgtools.py
# Module Description: Python wrapper for the cfgtools API
#
# Copyright (C) 2012 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

"""
Python wrapper for the cfgtools API.
Minimal usage example:
>>> import cfgtools
>>> cfg = cfgtools.read("/path/to/my.cfg")
>>> some_value = cfg.find_value("Group1.Subgroup.SomeValue")
>>> # .. do something with some_value ..
>>> # Iterate over all "level 1" groups and their keys
>>> for group in cfg.groups:
        for key in group.keys:
           print "%s.%s = %s"%(group.name,key.name,key.value())
>>> print "done!"
"""

import re
import os
import xml.sax
import xml.sax.handler
import xml.sax.saxutils as saxutils

# Key types
ARRAY = 0x00000001
STRING = 0x00000002
DATA = 0x00000004
INTEGER = 0x00000008
REAL = 0x00000010
DATE = 0x00000020
BOOLEAN = 0x00000040

_TYPES_TAGMAP = {"array": ARRAY, "string": STRING, "data": DATA, "integer": INTEGER, "real": REAL, "date": DATE, "boolean": BOOLEAN}
_TYPES_MAP = {ARRAY: "array", STRING: "string", DATA: "data", INTEGER: "integer", REAL: "real", DATE: "date", BOOLEAN: "boolean"}
_RE_PATH = re.compile(r"[\.|/\\]")  # allowed separators: [. | / \]


def read(file_or_path):
    """ cfgtools.read("file_or_path") -> Configuration
    Parses a configuration file and creates a new Configuration instance.
    @param file_or_path - file instance or path to a file
    @return Configuration instance
    @raise SAXException if the configuration could not be parsed
    """
    handler = _CfgSaxHandler()
    xml.sax.parse(file_or_path, handler)
    cfg = handler.cfg
    bundle = os.environ.get('BUNDLEDIR')
    loader = os.environ.get('LOADERCFG')
    override = os.environ.get('CFGOVERRIDE')
    override = (str(override).lower() == "yes")
    override = (override and bundle is not None and loader is not None)
    if override:
        try:
            loader = loader[len(bundle):][:-4]
            bundle = bundle.split('/')
            bundle = bundle[len(bundle) - 1] or bundle[len(bundle) - 2]
        except:
            override = False
    if override:
        def _group_visit(gs, v):
            for g in gs.groups:
                _group_visit(g, v + '_' + g.name)
            for k in gs.keys:
                ovar = v + '_' + k.name
                oval = os.environ.get(ovar)
                if oval is not None:
                    k.values = [oval]
        for grp in cfg.groups:
            _group_visit(grp, bundle + '_' + loader + '_' + grp.name)
    return cfg


def read_string(string):
    """ cfgtools.read_string(string) -> Configuration
    Parses a configuration file from a string and creates a new Configuration instance.
    @param string - string with the XML data
    @return Configuration instance
    @raise SAXException if the configuration could not be parsed
    """
    handler = _CfgSaxHandler()
    xml.sax.parseString(string, handler)
    return handler.cfg


class Configuration(object):
    __slots__ = ('groups', 'version', )

    def __init__(self):
        self.groups = []
        self.version = "1.0"

    def group(self, name):
        """obj.group(name) -> Group
        Finds the first child group with the given name.
        @param name - the name of the group
        @return a Group instance, or None if not found
        """
        return _byname(self.groups, name)

    def find_group(self, path):
        """obj.find_group(path) -> Group
        Finds a group in the hierarchy, following the given path
        @param path - the path to look for, where groups are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.OtherGroup"
        @return a Group instance, or None if not found
        """
        return _bypath(self, path)

    def find_key(self, path):
        """obj.find_key(path) -> Key
        Finds a key in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @return a Key instance, or None if not found
        """
        return _bypath(self, path, iskey=True)

    def find_value(self, path, default=None):
        """obj.find_value(path) -> str
        Finds a key value in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @param default - the default value to return if the given path
                         is not found
        @return the value found, or default
        """
        key = _bypath(self, path, iskey=True)
        return default if key is None else key.value()

    def find_values(self, path):
        """obj.find_values(path) -> list
        Finds a key values list in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @return the values list found, or None if not found
        """
        key = _bypath(self, path, iskey=True)
        return None if key is None else key.values

    def add_group(self, name, descr=None):
        """obj.add_group(self, "name", descr=None) -> Group
        Creates a new group as a child of this element.
        @param name - group name
        @param descr - optional group description
        """
        grp = Group(name, descr, self)
        if self.groups:
            self.groups[len(self.groups) - 1].next = grp
        self.groups.append(grp)
        return grp

    def write(self, output_io):
        """obj.write(output_io)
        Serializes this configuration structure XML to an IO.
        @param output_io - IO to write XML data to
        """
        self._write(output_io, 0)

    def _write(self, out, level):
        out.write("""<?xml version="1.0" encoding="UTF-8"?>\n<config version="%s">\n""" % self.version)
        for group in self.groups:
            group._write(out, level + 1)
        out.write("""</config>\n""")


class Group(object):
    __slots__ = ('name', 'descr', 'keys', 'groups', 'next', 'parent')

    def __init__(self, name=None, descr=None, parent=None):
        self.name = name
        self.descr = descr
        self.keys = []
        self.groups = []
        self.next = None
        self.parent = parent

    def group(self, name):
        """obj.group(name) -> Group
        Finds the first child group with the given name.
        @param name - the name of the group
        @return a Group instance, or None if not found
        """
        return _byname(self.groups, name)

    def key(self, name):
        """obj.key(name) -> Key
        Finds a child key with the given name.
        @param name - the name of the key
        @return a Key instance, or None if not found
        """
        return _byname(self.keys, name)

    def key_value(self, keyname, default=None):
        """obj.key_value(keyname, default=None) -> str
        Retrieves the value of a child key with the given name.
        @param keyname - the name of the key
        @param default - default value to return if the key is not found
        @return {str} - the key value, or None if not found
        """
        key = _byname(self.keys, keyname)
        return default if key is None else key.value()

    def find_group(self, path):
        """obj.find_group(path) -> Group
        Finds a group in the hierarchy, following the given path
        @param path - the path to look for, where groups are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.OtherGroup"
        @return a Group instance, or None if not found
        """
        return _bypath(self, path)

    def find_key(self, path):
        """obj.find_key(path) -> Key
        Finds a key in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @return a Key instance, or None if not found
        """
        return _bypath(self, path, iskey=True)

    def find_value(self, path, default=None):
        """obj.find_value(path) -> str
        Finds a key value in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @param default - the default value to return if the given path
                         is not found
        @return the value found, or default
        """
        key = _bypath(self, path, iskey=True)
        return default if key is None else key.value()

    def find_values(self, path):
        """obj.find_values(path) -> list
        Finds a key values list in the hierarchy, following the given path
        @param path - the path to look for, where groups/keys are separated
               using one of: [. | / \]. E.g.: "MyGroup.SubGroup.MyKey"
        @return the values list found, or None if not found
        """
        key = _bypath(self, path, iskey=True)
        return None if key is None else key.values

    def add_group(self, name, descr=None):
        """obj.add_group(self, "name", descr=None) -> Group
        Creates a new group as a child of this element.
        @param name - group name
        @param descr - optional group description
        """
        grp = Group(name, descr, self)
        if self.groups:
            self.groups[len(self.groups) - 1].next = grp
        self.groups.append(grp)
        return grp

    def add_key(self, name, descr=None):
        """obj.add_key(self, "name", descr=None) -> Key
        Creates a new key as a child of this element.
        @param name - key name
        @param descr - optional key description
        """
        key = Key(name, descr, self)
        if self.keys:
            self.keys[len(self.keys) - 1].next = key
        self.keys.append(key)
        return key

    def _write(self, out, level):
        out.write('%s<group' % ("\t" * level))
        if self.name is not None:
            out.write(' name=%s' % saxutils.quoteattr(self.name.encode("UTF-8")))
        if self.descr is not None:
            out.write(' descr=%s' % saxutils.quoteattr(self.descr.encode("UTF-8")))
        out.write('>\n')
        for group in self.groups:
            group._write(out, level + 1)
        for key in self.keys:
            key._write(out, level + 1)
        out.write('%s</group>\n' % ("\t" * level))


class Key(object):
    __slots__ = ('name', 'descr', 'type', 'values', 'next', 'parent')

    def __init__(self, name=None, descr=None, parent=None):
        self.name = name
        self.descr = descr
        self.type = None
        self.values = []
        self.next = None
        self.parent = parent

    def value(self):
        """obj.value() -> str
        Gets the first value of this key.
        @return the value or None if this key is empty
        """
        return self.values[0] if self.values else None

    def add_value(self, value):
        """obj.add_value("value")
        Adds a value to this key
        @param value - value to add
        @return self for convenience
        """
        self.values.append(value)
        return self

    def _write(self, out, level):
        out.write('%s<key' % ("\t" * level))
        if self.name is not None:
            out.write(' name=%s' % saxutils.quoteattr(self.name.encode("UTF-8")))
        if self.descr is not None:
            out.write(' descr=%s' % saxutils.quoteattr(self.descr.encode("UTF-8")))
        out.write('>\n')
        if self.values:
            level += 1
            typestr = _TYPES_MAP[self.type]
            if self.type == ARRAY:
                typestr = "string"
                out.write('%s<array>\n' % ("\t" * level))
                level += 1
            for val in self.values:
                out.write('%s<%s>%s</%s>\n' % ("\t" * level, typestr, saxutils.escape(val.encode("UTF-8")), typestr))
            if self.type == ARRAY:
                level -= 1
                out.write('%s</array>\n' % ("\t" * level))
            level -= 1
        out.write('%s</key>\n' % ("\t" * level))


def _bypath(node, path, index=0, iskey=False):
    "private - finds keys or groups recursivelly given a path"
    if node is not None:
        if isinstance(path, basestring):
            path = _RE_PATH.split(path)
        next_idx = index + 1
        if index < len(path):
            if iskey and (next_idx == len(path)):
                return node.key(path[index])
            return _bypath(node.group(path[index]), path, next_idx, iskey)
        return node
    return None


def _byname(array, name):
    "private - finds a node in a list"
    for obj in array:
        if obj.name == name:
            return obj
    return None


class _CfgSaxHandler(xml.sax.handler.ContentHandler):
    "private - SAX handler used to parse configuration files"
    def __init__(self):
        self.cfg = Configuration()
        self.current = self.cfg
        self.currval = None

    def startElement(self, name, attrs):
        if name == "group":
            if isinstance(self.current, (Configuration, Group)):
                self.current = self.current.add_group(name=attrs.get("name"), descr=attrs.get("descr"))
        elif name == "key":
            if isinstance(self.current, Group):
                self.current = self.current.add_key(name=attrs.get("name"), descr=attrs.get("descr"))
        elif name in _TYPES_TAGMAP:
            if self.current.type is None:
                self.current.type = _TYPES_TAGMAP[name]
            if self.currval is None and name != "array":
                self.currval = u""
        elif name == "config":
            if self.current == self.cfg:
                ver = attrs.get("version")
                if ver:
                    self.current.version = ver

    def characters(self, content):
        if self.currval is not None and isinstance(self.current, Key):
            self.currval += content

    def endElement(self, name):
        if self.currval is not None and isinstance(self.current, Key):
            self.current.values.append(self.currval)
            self.currval = None
        elif name == "group" or name == "key":
            self.current = self.current.parent
