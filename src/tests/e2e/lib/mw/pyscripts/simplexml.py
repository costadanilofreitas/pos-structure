# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\simplexml.py
from xml.etree import ElementTree
from minixsv import pyxsval
from genxmlif import GenXmlIfError
from genxmlif.xmlifElementTree import ElementExtension

class ValidationError(Exception):
    pass


class XmlDictObject(dict):
    """
    Adds object like functionality to the standard dictionary.
    """

    def __init__(self, initdict = None):
        if initdict is None:
            initdict = {}
        dict.__init__(self, initdict)
        return

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def __str__(self):
        if '_text' in self:
            return self.__getitem__('_text')
        else:
            return ''

    @staticmethod
    def wrap(x):
        """
        Static method to wrap a dictionary recursively as an XmlDictObject
        """
        if isinstance(x, dict):
            return XmlDictObject(((k, XmlDictObject.wrap(v)) for k, v in x.iteritems()))
        elif isinstance(x, list):
            return [ XmlDictObject.wrap(v) for v in x ]
        else:
            return x

    @staticmethod
    def _unwrap(x):
        if isinstance(x, dict):
            return dict(((k, XmlDictObject._unwrap(v)) for k, v in x.iteritems()))
        elif isinstance(x, list):
            return [ XmlDictObject._unwrap(v) for v in x ]
        else:
            return x

    def unwrap(self):
        """
        Recursively converts an XmlDictObject to a standard dictionary and returns the result.
        """
        return XmlDictObject._unwrap(self)


def _convert_dict_to_xml_recurse(parent, dictitem):
    raise not isinstance(dictitem, list) or AssertionError
    if isinstance(dictitem, dict):
        for tag, child in dictitem.iteritems():
            if str(tag) == '_text':
                parent.text = str(child)
            elif isinstance(child, list):
                for listchild in child:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _convert_dict_to_xml_recurse(elem, listchild)

            else:
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _convert_dict_to_xml_recurse(elem, child)

    else:
        parent.text = str(dictitem)


def convert_dict_to_xml(xmldict):
    """
    Converts a dictionary to an XML ElementTree Element
    """
    roottag = xmldict.keys()[0]
    root = ElementTree.Element(roottag)
    _convert_dict_to_xml_recurse(root, xmldict[roottag])
    return root


def _convert_xml_to_dict_recurse(node, dictclass):
    nodedict = dictclass()
    if len(node.items()) > 0:
        nodedict.update(dict(node.items()))
    for child in node:
        newitem = _convert_xml_to_dict_recurse(child, dictclass)
        if child.tag in nodedict:
            if isinstance(nodedict[child.tag], list):
                nodedict[child.tag].append(newitem)
            else:
                nodedict[child.tag] = [nodedict[child.tag], newitem]
        else:
            nodedict[child.tag] = newitem

    if node.text is None:
        text = ''
    else:
        text = node.text.strip()
    if len(nodedict) > 0:
        if len(text) > 0:
            nodedict['_text'] = text
    else:
        nodedict = text
    return nodedict


def convert_xml_to_dict(root, dictclass = XmlDictObject):
    """
    Converts an XML file or ElementTree Element to a dictionary
    """
    if isinstance(root, str):
        root = ElementTree.parse(root).getroot()
    elif not isinstance(root, (ElementExtension, ElementTree._ElementInterface, ElementTree.Element)):
        raise TypeError('Expected ElementTree.Element or file path string')
    return dictclass({root.tag: _convert_xml_to_dict_recurse(root, dictclass)})


def loads(s, validate = False, xsd_text = None):
    if validate or xsd_text:
        try:
            wrapper = pyxsval.parseAndValidateXmlInputString(s, xsdText=xsd_text, xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
        except (pyxsval.XsvalError, GenXmlIfError) as e:
            raise ValidationError(e)

        root = wrapper.getTree().getroot()
    else:
        root = ElementTree.fromstring(s)
    obj = convert_xml_to_dict(root)
    return obj


def load(fp, validate = False, xsd_text = None):
    tree = ElementTree.parse(fp)
    if validate or xsd_text:
        s = ElementTree.tostring(tree.getroot())
        try:
            wrapper = pyxsval.parseAndValidateXmlInputString(s, xsdText=xsd_text, xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
        except (pyxsval.XsvalError, GenXmlIfError) as e:
            raise ValidationError(e)

        root = wrapper.getTree().getroot()
    else:
        root = tree.getroot()
    obj = convert_xml_to_dict(root)
    return obj


def dumps(objs):
    root = convert_dict_to_xml(objs)
    s = ElementTree.tostring(root)
    return s


def dump(objs, fp):
    root = convert_dict_to_xml(objs)
    tree = ElementTree.ElementTree(root)
    tree.write(fp)