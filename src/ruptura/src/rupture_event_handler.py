# -*- coding: utf-8 -*-

import json
from logging import Logger

import bustoken
from messagehandler import EventHandler
from msgbus import MBEasyContext, TK_SYS_ACK, TK_SYS_NAK, FM_STRING

from rupture_events import RuptureEvents
from rupture_service import RuptureService


class RuptureEventHandler(EventHandler):
    def __init__(self, mb_context, logger, rupture_service):
        # type: (MBEasyContext, Logger, RuptureService) -> None
        super(RuptureEventHandler, self).__init__(mb_context)

        self.logger = logger
        self.rupture_service = rupture_service

    def get_handled_tokens(self):
        return [bustoken.TK_RUPTURA_GET_ENABLED,
                bustoken.TK_RUPTURA_GET_DISABLED,
                bustoken.TK_RUPTURA_UPDATE_ITEMS,
                bustoken.TK_RUPTURA_CHECK_ITEMS,
                bustoken.TK_RUPTURA_GET_CLEAN_TIME_WINDOW]

    def handle_message(self, msg):
        try:
            processing_message = "Start processing message: {}"

            if msg.token == bustoken.TK_RUPTURA_CHECK_ITEMS:
                self.logger.info(processing_message.format("TK_RUPTURA_CHECK_ITEMS"))

                params = msg.data.split('\0')
                changes_json, session_id = params[:2]

                all_items = "False"
                if len(params) == 3:
                    all_items = params[2]

                changes_dict = json.loads(changes_json or "{}")
                items_to_disable = self.rupture_service.check_items(changes_dict, session_id, all_items)
                data = json.dumps(items_to_disable) if items_to_disable else ""

                self._success_reply_message(msg, data)

            elif msg.token == bustoken.TK_RUPTURA_UPDATE_ITEMS:
                self.logger.info(processing_message.format("TK_RUPTURA_UPDATE_ITEMS"))

                changes_json, session_id, pos_id = msg.data.split('\0')
                self.rupture_service.update_items(changes_json, session_id)

                self._success_reply_message(msg)

            elif msg.token == bustoken.TK_RUPTURA_GET_ENABLED:
                self.logger.info(processing_message.format("TK_RUPTURA_GET_ENABLED"))

                if msg.data == 'UI':
                    items = self.rupture_service.get_enabled_items_list()
                    data = json.dumps(items, default=lambda o: o.__dict__, sort_keys=True)
                else:
                    data = json.dumps(self.rupture_service.get_enabled_items())

                self._success_reply_message(msg, data)

            elif msg.token == bustoken.TK_RUPTURA_GET_DISABLED:
                self.logger.info(processing_message.format("TK_RUPTURA_GET_DISABLED"))

                if msg.data == 'UI':
                    items = self.rupture_service.get_disabled_items_list()
                    data = json.dumps(items, default=lambda o: o.__dict__, sort_keys=True)
                else:
                    data = json.dumps(self.rupture_service.get_disabled_items())

                self._success_reply_message(msg, data)

            elif msg.token == bustoken.TK_RUPTURA_GET_CLEAN_TIME_WINDOW:
                self.logger.info(processing_message.format("TK_RUPTURA_GET_CLEAN_TIME_WINDOW"))
                data = json.dumps(self.rupture_service.get_clean_time())
                self._success_reply_message(msg, data)

        except BaseException as ex:
            self.logger.exception("Error handling message")
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, FM_STRING, repr(ex))

    def handle_event(self, subject, evt_type, data, msg):
        try:
            self.logger.info("Start processing event: {}".format(subject))

            if subject == RuptureEvents.FullRuptureRequest:
                self.rupture_service.create_full_snapshot()
            elif subject == RuptureEvents.CleanRupture:
                self.rupture_service.clean_rupture_items(evt_type)

        except Exception as _:
            self.logger.exception("Error processing event: {}".format(subject))
        finally:
            self.logger.info("Finishing event: {}".format(subject))

    def terminate_event(self):
        # No need to stop anything into this component
        pass

    def _success_reply_message(self, msg, data=None):
        msg.token = TK_SYS_ACK
        if data:
            self.mbcontext.MB_ReplyMessage(msg, FM_STRING, data)
        else:
            self.mbcontext.MB_EasyReplyMessage(msg)
