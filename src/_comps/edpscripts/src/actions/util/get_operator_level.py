from sysactions import get_user_information
from xml.etree import cElementTree as eTree

from model.customexception import NotFoundUserError


def get_user_level(user_id):
    if user_id is None:
        return None

    user_xml_str = get_user_information(user_id)
    if user_xml_str is None:
        raise NotFoundUserError("USER_NOT_FOUND")
    
    user_xml = eTree.XML(user_xml_str)
    user_element = user_xml.find("user")
    user_level = int(user_element.attrib["Level"])
    
    return user_level
