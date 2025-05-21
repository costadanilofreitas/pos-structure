# -*- coding: utf-8 -*-

import logging

from sysactions import mbcontext

logger = logging.getLogger("TableActions")


def publish_event(pos_id, action_type, event_type, event_data, event_source_pos_id=0):
    event_subject = "POS{}".format(pos_id)
    event_data = str(event_data)
    event_xml = """<Event subject="{0}" type="{1}">
                        <{2}>
                            {3}
                        </{2}>
                   </Event>""".format(event_subject, event_type, action_type, event_data)

    mbcontext.MB_EasyEvtSend(subject=event_subject,
                             type=event_type,
                             xml=event_xml,
                             synchronous=False,
                             sourceid=event_source_pos_id,
                             queue=None,
                             timeout=-1)
