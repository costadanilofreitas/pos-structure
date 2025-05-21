# -*- coding: utf-8 -*-

import json
import os
import random
import re
from datetime import timedelta, datetime

import uuid
from behave import *
from helper import sqlite_helper, mw_helper, common_helper
from messagebus import TokenCreator, TokenPriority
from model import DatabaseModel
from mw.common.msgbus import MBEasyContext, TK_SYS_NAK, FM_PARAM


@when("send a order release for all jsons in folder with auto produce {auto_produce} using {send_method} method")
def step_impl(context, auto_produce, send_method):
    auto_produce = auto_produce.lower() == "on"
    send_method = send_method.lower()

    current_file_path = os.path.dirname(os.path.abspath(__file__))
    jsons_to_test_path = os.path.join(current_file_path, "..", "jsons_to_test")
    jsons_file_name = os.listdir(jsons_to_test_path)
    context.orders_to_bump = len(jsons_file_name)

    for json_file_name in jsons_file_name:
        json_path = os.path.join(jsons_to_test_path, json_file_name)
        with open(json_path) as json_file:
            json_template = json.load(json_file)

        json_template["id"] = "${REMOTE_ID}"
        json_template["shortReference"] = "${SHORT_REFERENCE}"
        json_template["createAt"] = "${CREATE_AT_TIME}"
        json_template["merchant"] = "1000"
        json_template = json.dumps(json_template)

        _send_remote_order(json_template, context, auto_produce, send_method)


@when("send a order release for json in folder with auto produce {auto_produce} using {send_method} method")
def step_impl(context, auto_produce, send_method):
    auto_produce = auto_produce.lower() == "on"
    send_method = send_method.lower()

    current_file_path = os.path.dirname(os.path.abspath(__file__))
    jsons_to_test_path = os.path.join(current_file_path, "..", "json_to_test")
    jsons_file_name = os.listdir(jsons_to_test_path)
    context.orders_to_bump = len(jsons_file_name)

    for json_file_name in jsons_file_name:
        json_path = os.path.join(jsons_to_test_path, json_file_name)
        with open(json_path) as json_file:
            json_template = json.load(json_file)

        json_template["id"] = "${REMOTE_ID}"
        json_template["shortReference"] = "${SHORT_REFERENCE}"
        json_template["createAt"] = "${CREATE_AT_TIME}"
        json_template["merchant"] = "1000"
        json_template = json.dumps(json_template)

        _send_remote_order(json_template, context, auto_produce, send_method)


@when("send a order release for all jsons in remote order log with limit of {limit} orders by log with auto produce {auto_produce} using {send_method} method")
def step_impl(context, limit, auto_produce, send_method):
    auto_produce = auto_produce.lower() == "on"
    send_method = send_method.lower()

    current_file_path = os.path.dirname(os.path.abspath(__file__))
    logs_to_test_path = os.path.join(current_file_path, "..", "logs_to_test")
    logs_file_name = os.listdir(logs_to_test_path)

    for log_file_name in logs_file_name:
        log_path = os.path.join(logs_to_test_path, log_file_name)
        with open(log_path, "r") as log_file:
            log_text = log_file.read()

        remote_order_jsons_by_type = [re.findall(r"TK_REMOTE_ORDER_CREATE_AND_PRODUCE.*?({.*})", log_text)[:int(limit)],
                                      re.findall(r"TK_REMOTE_ORDER_CREATE.*?({.*})", log_text)[:int(limit)],
                                      re.findall(r"LogisticOrderConfirm.*?({.*})", log_text)[:int(limit)]]

        remote_order_jsons = []
        for remote_order_type in remote_order_jsons_by_type:
            remote_order_jsons.extend(remote_order_type)

        context.orders_to_bump = len(remote_order_jsons)

        for remote_order_json in remote_order_jsons:
            json_template = json.loads(remote_order_json)
            json_template["id"] = "${REMOTE_ID}"
            json_template["shortReference"] = "${SHORT_REFERENCE}"
            json_template["createAt"] = "${CREATE_AT_TIME}"
            json_template["merchant"] = "1000"
            json_template = json.dumps(json_template)

            _send_remote_order(json_template, context, auto_produce, send_method)


@step("the remote order payment types are inserted on database")
def step_impl(context):
    query = """
    insert or ignore into tendertype values (9000, 'Ifood', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    insert or ignore into tendertype values (9001, 'UberEats', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    insert or ignore into tendertype values (9002, 'App', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    insert or ignore into tendertype values (128, 'PAGAMENTO ONLINE - iFOOD', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    insert or ignore into tendertype values (200, 'ONLINE VOUCHER - iFOOD ', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    insert or ignore into tendertype values (201, 'Maquininha Externa Delivery', 'BRL', NULL, 0, NULL, 0.00, 9, 0, 0, NULL);
    """
    sqlite_helper.execute_query(query, DatabaseModel.PRODUCT_DB, commit=True)


@step("the SacOrderCancel is released to RemoteOrderId: {remote_order_id}")
def void_remote_order(context, remote_order_id):
    mb_context = context.mb_context  # type: MBEasyContext
    data = json.dumps(dict(id=remote_order_id))
    mb_context.MB_EasyEvtSend(subject="SacOrderCancel", type="", xml=data)


def _send_remote_order(order_json, context, auto_produce=True, send_method="message"):
    send_method = send_method.lower()
    mb_context = context.mb_context  # type: MBEasyContext

    context.remote_id = str(uuid.uuid4())
    context.code = str(uuid.uuid4())
    short_reference = str(random.randint(1, 9999)).zfill(4)

    if not hasattr(context, "created_at_time"):
        context.created_at_time = common_helper.convert_from_localtime_to_utc(datetime.now())
    context.pickup_time = context.created_at_time + timedelta(minutes=random.randint(9, 17))

    if hasattr(context, "original_id"):
        order_json = order_json.replace(u"${ORIGINAL_ID}", context.original_id)
    else:
        context.original_id = context.remote_id

    order_json = order_json.replace(u"${REMOTE_ID}", context.remote_id)
    order_json = order_json.replace(u"${CODE}", context.code)
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    order_json = order_json.replace(u"${PICKUP_TIME}", context.pickup_time.strftime((date_format)))
    order_json = order_json.replace(u"${CREATE_AT_TIME}", context.created_at_time.strftime(date_format))
    order_json = order_json.replace(u"${CREATED_AT}", context.created_at_time.strftime(date_format))
    order_json = order_json.replace(u"${SHORT_REFERENCE}", short_reference)

    order_json = json.loads(order_json)
    context.short_reference = order_json.get("shortReference")
    context.partner = order_json.get("partner").upper()
    context.part_code_list = mw_helper.get_part_code_list(order_json.get("items"))
    context.client_name = None
    context.pickup_type = None

    for index, element in enumerate(order_json.get("custom_properties")):
        key = element["key"].lower()
        value = element["value"]

        if key == "customer_name":
            context.client_name = value
        elif key == "schedule_time":
            now = datetime.utcnow() + timedelta(minutes=30)
            order_json["custom_properties"][index]["value"] = now.isoformat()

    for key, value in order_json.get("pickup").items():
        if key == "type":
            context.pickup_type = value
            break

    order_json = str(json.dumps(order_json, ensure_ascii=False))
    if send_method == "message":
        token = TokenCreator.create_token(TokenPriority.low, "37", "208")
        if auto_produce:
            token = TokenCreator.create_token(TokenPriority.low, "37", "207")

        msg = mb_context.MB_EasySendMessage("RemoteOrder", token, FM_PARAM, order_json)
        if msg.token == TK_SYS_NAK:
            raise Exception("Error sending message")

    elif send_method == "event":
        mb_context.MB_EasyEvtSend(subject="LogisticOrderConfirm", type="", xml=order_json, synchronous=True)

    else:
        raise Exception("Unknown send method: {}".format(send_method))
