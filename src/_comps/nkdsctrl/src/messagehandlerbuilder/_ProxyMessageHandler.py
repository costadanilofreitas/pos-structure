from logging import Logger
from xml.etree import cElementTree as eTree
from threading import Thread
from xml.etree.ElementTree import Element

from messagehandler import MessageHandler
from messagebus import TokenCreator, TokenPriority, AckMessage, DefaultToken, Event, Message, NakMessage, MessageBus
from msgbus import FM_PARAM
from model import Kds, KdsModel
from typing import List

MSG_GRP_KDS = '0B'
TK_KDS_GETMODEL = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "1")
TK_KDS_UPDATE_VIEW = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "2")
TK_KDS_REFRESH = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "3")
TK_KDS_REFRESH_END = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "4")
TK_KDS_SET_PROD_STATE = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "5")
TK_KDS_UNDO_SERVE = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "6")
TK_KDS_TOGGLE_TAG_LINE = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "8")
TK_KDS_CHANGE_VIEW = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "A")
TK_KDS_BUMP_BAR_COMMAND = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "B")
TK_KDS_BUMP_ZOOM_NEXT = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "C")
TK_KDS_SELECT_ORDER = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "20")
TK_KDS_UPDATE_STATISTICS = TokenCreator.create_token(TokenPriority.high, MSG_GRP_KDS, "21")

MSG_GRP_PRODUCTION = "0C"
TK_PROD_REFRESH_VIEW = TokenCreator.create_token(TokenPriority.low, MSG_GRP_PRODUCTION, "1")
TK_PROD_SET_ORDER_STATE = TokenCreator.create_token(TokenPriority.low, MSG_GRP_PRODUCTION, "2")
TK_PROD_UNDO = TokenCreator.create_token(TokenPriority.low, MSG_GRP_PRODUCTION, "7")
TK_PROD_TOGGLE_TAG_LINE = TokenCreator.create_token(TokenPriority.low, MSG_GRP_PRODUCTION, "8")
TK_PROD_GET_STATISTICS = TokenCreator.create_token(TokenPriority.low, MSG_GRP_PRODUCTION, "102")

new_production = "ProductionSystem"

none_kds_found_message = "None KDS found"


class ProxyMessageHandler(MessageHandler):
    def __init__(self, comp_name, kds_list, message_bus, logger):
        # type: (str, List[Kds], MessageBus, Logger) -> None
        self.comp_name = comp_name
        self.kds_list = kds_list
        self.message_bus = message_bus
        self.logger = logger

        self.statistics_cache = ''
        init_thread = Thread(target=self.get_current_statistics)
        init_thread.daemon = True
        init_thread.start()

    def handle_event(self, message_bus, event):
        return

    def handle_message(self, message_bus, message):
        data = message.data.split('\0')
        resp = None

        if message.token == TK_KDS_SELECT_ORDER:
            kds_id = int(data[0])
            self.logger.info("Receiving TK_KDS_SELECT_ORDER for KDS - {:02d}".format(kds_id))

            # TODO: Change Selected Order and Store it

            message.token = DefaultToken.TK_SYS_ACK

        elif message.token == TK_KDS_GETMODEL:
            resp = self.handle_kds_get_model(data)
        elif message.token == TK_KDS_CHANGE_VIEW:
            resp = self.handle_kds_change_view(data)
        elif message.token == TK_KDS_UPDATE_VIEW:
            resp = self.handle_kds_update_view(data, message_bus)
        elif message.token == TK_KDS_REFRESH:
            resp = self.handle_kds_refresh(data, message_bus)
        elif message.token == TK_KDS_REFRESH_END:
            resp = self.handle_kds_refresh_end(data, message_bus)
        elif message.token == TK_KDS_SET_PROD_STATE:
            resp = self.handle_kds_set_prod_state(data, message_bus)
        elif message.token == TK_KDS_UNDO_SERVE:
            resp = self.handle_kds_undo_serve(data, message_bus)
        elif message.token == TK_KDS_UPDATE_STATISTICS:
            resp = self.handle_kds_update_statistics(data, message_bus)
        elif message.token == TK_KDS_BUMP_BAR_COMMAND:
            resp = self.handle_kds_bump_bar_command(data, message_bus)
        elif message.token == TK_KDS_BUMP_ZOOM_NEXT:
            resp = self.handle_kds_zoom_next(data)
        elif message.token == TK_KDS_TOGGLE_TAG_LINE:
            resp = self.handle_kds_toggle_tag_line(data, message_bus)
        else:
            kds_id = int(data[0])
            resp = self.forward_message(kds_id, message, message_bus)

        message_bus.reply_message(message, resp)
        self.logger.info("Message replied")

    def handle_kds_get_model(self, data):
        self.logger.info("TK_KDS_GETMODEL - Received")

        kds_id = data[0]
        kds = self.get_kds(kds_id)

        if not kds:
            self.logger.info("TK_KDS_GETMODEL - KdsId: {} not found".format(kds_id))
            return NakMessage(none_kds_found_message, 0)

        self.logger.info("TK_KDS_GETMODEL - KdsId: {}".format(kds_id))

        kds_model = KdsModel(kds, kds_id)
        kds_model_xml = kds_model.get_model_xml()
        kds_model_xml.append(eTree.Element("Statistics", text=self.statistics_cache))
        resp = AckMessage(eTree.tostring(kds_model_xml, encoding='utf8', method='xml'), 0)

        self.logger.info("TK_KDS_GETMODEL - Finished")
        return resp

    def handle_kds_change_view(self, data):
        self.logger.info("TK_KDS_CHANGE_VIEW - Received")

        kds_id = data[0]
        view_name = data[1]
        kds = self.get_kds(kds_id)

        if not kds:
            self.logger.info("TK_KDS_CHANGE_VIEW - KdsId: {} not found".format(kds_id))
            return NakMessage(none_kds_found_message, 0)

        self.set_selected_view(kds, view_name)

        self.logger.info("TK_KDS_CHANGE_VIEW - KdsId: {}".format(kds_id))

        kds_model = KdsModel(kds, kds_id)
        kds_model_xml = kds_model.get_model_xml()
        resp = AckMessage(eTree.tostring(kds_model_xml, encoding='utf8', method='xml'), 0)

        self.logger.info("TK_KDS_CHANGE_VIEW - Received")
        return resp

    def get_kds(self, kds_id):
        return next((x for x in self.kds_list if x.name == kds_id), None)

    @staticmethod
    def get_bump_bar_command(bump_bar_commands, command_code):
        return next((x for x in bump_bar_commands if command_code in x.keys), None)

    @staticmethod
    def set_selected_view(kds, view_name):
        for view in kds.views:
            view.selected = view.name == view_name

        has_selected_view = next((x for x in kds.views if x.selected), None)
        if not has_selected_view:
            kds.views[0].selected = True

    @staticmethod
    def set_view_zoom(kds, production_view):
        view = next((x for x in kds.views if x.production_view == production_view), None)
        if not view:
            return

        view.selected_zoom += 1
        if view.selected_zoom == len(view.zoom_levels):
            view.selected_zoom = 0

    def handle_kds_update_view(self, data, message_bus):
        self.logger.info("TK_KDS_UPDATE_VIEW - Finished")

        production_view = data[0]
        xml = eTree.XML(data[1])
        order_id = xml.get("order_id")

        self.logger.info("TK_KDS_UPDATE_VIEW - ProductionView: {} / OrderId: {}".format(production_view, order_id))

        view_update_xml = self.create_view_update_xml(production_view, xml)
        for kds in self.get_kds_list_with_production_view(production_view):
            self.logger.info("TK_KDS_UPDATE_VIEW - Sending event for KDS: {} / OrderId: {}".format(kds, order_id))

            event_subject = "KDS" + kds
            event_type = "PROD_ORDER_" + order_id + "_" + production_view
            event = self.send_event(event_subject, event_type, view_update_xml)
            message_bus.publish_event(event)

        self.logger.info("TK_KDS_UPDATE_VIEW - Finished")

        return AckMessage('', 0)

    def handle_kds_refresh(self, data, message_bus):
        self.logger.info("TK_KDS_REFRESH - Received")
        response = AckMessage('', 0)

        kds_id = data[0]
        for view in self.get_production_views_with_kds_id(kds_id):
            self.logger.info("TK_KDS_REFRESH - Sending event for View: {}".format(view))

            message = Message(TK_PROD_REFRESH_VIEW, FM_PARAM, str(view), 3000000)
            reply = message_bus.send_message(new_production, message)
            if reply.token != DefaultToken.TK_SYS_ACK:
                response = NakMessage()

        self.logger.info("TK_KDS_REFRESH - Finished")

        return response

    def handle_kds_set_prod_state(self, data, message_bus):
        self.logger.info("TK_KDS_SET_PROD_STATE - Received")

        kds_id = data[0]
        order_id = data[1]
        prod_state = data[2]
        view = data[3]

        log_message = "TK_KDS_SET_PROD_STATE - Sending event for KDS: {} / OrderId: {} / ProdState {}"
        self.logger.info(log_message.format(kds_id, order_id, prod_state))

        message_data = order_id + "\0" + view + "\0" + prod_state
        message = Message(TK_PROD_SET_ORDER_STATE, FM_PARAM, message_data, 3000000)
        message_bus.send_message(new_production, message)

        self.logger.info("TK_KDS_SET_PROD_STATE - Finished")

        return AckMessage('', 0)

    def handle_kds_zoom_next(self, data):
        self.logger.info("TK_KDS_BUMP_ZOOM_NEXT - Received")

        kds_id = data[0]
        production_view = data[1]
        kds = self.get_kds(kds_id)

        if not kds:
            self.logger.info("TK_KDS_BUMP_ZOOM_NEXT - KdsId: {} not found".format(kds_id))
            return NakMessage(none_kds_found_message, 0)

        self.set_view_zoom(kds, production_view)

        self.logger.info("TK_KDS_BUMP_ZOOM_NEXT - KdsId: {}".format(kds_id))

        kds_model = KdsModel(kds, kds_id)
        kds_model_xml = kds_model.get_model_xml()
        resp = AckMessage(eTree.tostring(kds_model_xml, encoding='utf8', method='xml'), 0)

        self.logger.info("TK_KDS_BUMP_ZOOM_NEXT - Received")
        return resp

    def handle_kds_refresh_end(self, data, message_bus):
        self.logger.info("TK_KDS_REFRESH_END - Received")
    
        production_view = data[0]
        for kds in self.get_kds_list_with_production_view(production_view):
            self.logger.info("TK_KDS_REFRESH_END - Sending event for KDS: {}".format(kds))
        
            event_subject = "KDS" + kds
            event_type = "REFRESH_END_" + production_view
            refresh_end_xml = eTree.XML("<RefreshEnd name=\"{}\" updated=\"true\"/>".format(production_view))
            event = self.send_event(event_subject, event_type, refresh_end_xml)
            message_bus.publish_event(event)
    
        self.logger.info("TK_KDS_REFRESH_END - Finished")
    
        return AckMessage('', 0)
    
    def handle_kds_toggle_tag_line(self, data, message_bus):
        self.logger.info("TK_KDS_TOGGLE_TAG_LINE - Received")
    
        kds_id = data[0]
        order_id = data[1]
        line_number = data[2]
        tag_name = data[3]
        view = data[4]
    
        log_message = "TK_KDS_TOGGLE_TAG_LINE - Sending event for KDS: {} / OrderId: {} / LineNumber {} / TagName {}"
        self.logger.info(log_message.format(kds_id, order_id, line_number, tag_name))
    
        message_data = order_id + "\0" + view + "\0" + line_number + "\0" + tag_name
        message = Message(TK_PROD_TOGGLE_TAG_LINE, FM_PARAM, message_data, 3000000)
        message_bus.send_message(new_production, message)
    
        self.logger.info("TK_KDS_TOGGLE_TAG_LINE - Finished")
    
        return AckMessage('', 0)

    def handle_kds_update_statistics(self, data, message_bus):
        self.logger.info("TK_KDS_UPDATE_STATISTICS - Received")

        try:
            statistics = data[0]
            self.statistics_cache = statistics
        except ValueError:
            pass

        for kds_id in self.get_all_kds_ids():
            event_data = eTree.tostring(self.create_statistics_event_from_json(self.statistics_cache))
            event = Event(subject='KDS{}'.format(kds_id), event_type='Statistics', data=event_data)
            message_bus.publish_event(event)

        self.logger.info("TK_KDS_UPDATE_STATISTICS - Finished")

        return AckMessage('', 0)

    def handle_kds_bump_bar_command(self, data, message_bus):
        self.logger.info("TK_KDS_BUMP_BAR_COMMAND - Received")

        kds_id = data[0]
        bump_bar_name = data[1]
        command_code = data[2]

        log_message = "TK_KDS_BUMP_BAR_COMMAND - KdsId: {} / BumpBar: {} / Command: {}"
        self.logger.info(log_message.format(kds_id, bump_bar_name, command_code))

        kds = self.get_kds(kds_id)
        if not kds:
            self.logger.info("TK_KDS_BUMP_BAR_COMMAND - KdsId: {} not found".format(kds_id))
            return NakMessage(none_kds_found_message, 0)

        bump_bar = kds.bump_bar
        command = self.get_bump_bar_command(bump_bar.commands, command_code)
        if not command:
            self.logger.info("TK_KDS_BUMP_BAR_COMMAND - Key not mapped")
            return AckMessage('', 0)

        root_element = eTree.Element("Event")
        eTree.SubElement(root_element, "Command", name=command.name)
        event = Event(subject='KDS{}'.format(kds_id), event_type='KdsModel', data=eTree.tostring(root_element))
        message_bus.publish_event(event)

        self.logger.info("TK_KDS_BUMP_BAR_COMMAND - Received")
        return AckMessage('', 0)

    def handle_kds_undo_serve(self, data, message_bus):
        self.logger.info("TK_KDS_UNDO_SERVE - Received")

        kds_id = data[0]
        view = data[1]

        log_message = "TK_KDS_UNDO_SERVE - Sending event for KDS: {}"
        self.logger.info(log_message.format(kds_id))

        message = Message(TK_PROD_UNDO, FM_PARAM, str(view), 3000000)
        message_bus.send_message(new_production, message)

        self.logger.info("TK_KDS_UNDO_SERVE - Finished")

        return AckMessage('', 0)

    @staticmethod
    def create_view_update_xml(production_view, xml):
        view_update_xml = eTree.Element("ViewUpdate", name=production_view)
        view_update_xml.append(xml)

        return view_update_xml

    @staticmethod
    def send_event(event_subject, event_type, xml):
        event_xml = eTree.Element("Event", subject=event_subject, type=event_type)
        event_xml.append(xml)
        event = Event(event_subject, event_type, eTree.tostring(event_xml))

        return event

    def forward_message(self, kds_id, message, message_bus):
        self.logger.info("Receiving message for KDS - {:02d}".format(kds_id))
        resp = message_bus.send_message(self.comp_name, message)
        self.logger.info("Message forwarded")

        return resp

    def get_kds_list_with_production_view(self, kds_view):
        kds_list = []
        for kds in self.kds_list:
            if len([v for v in kds.views if v.production_view == kds_view]) > 0:
                kds_list.append(kds.name)

        return list(set(kds_list))

    def get_production_views_with_kds_id(self, kds_id):
        view_list = []

        kds = next((x for x in self.kds_list if x.name == kds_id), None)
        for view in kds.views:
            view_list.append(view.production_view)

        return list(set(view_list))

    @staticmethod
    def create_statistics_event_from_json(json_data):
        # type: (str) -> Element
        root_element = eTree.Element("Event")
        eTree.SubElement(root_element, "Statistics", text=json_data)
        return root_element

    def get_all_kds_ids(self):
        kds_list = []
        for kds in self.kds_list:
            kds_list.append(kds.name)

        return list(set(kds_list))

    def get_current_statistics(self):
        statistics_ok = False
        while statistics_ok is False:
            try:
                resp = self.message_bus.send_message(new_production, Message(TK_PROD_GET_STATISTICS))
                if resp.token == DefaultToken.TK_SYS_ACK:
                    self.statistics_cache = resp.data
                    statistics_ok = True
            except BaseException: # noqa
                pass
