# -*- coding: utf-8 -*-
import logging
import os
from threading import Thread

import boto3
import cfgtools
from helper import config_logger, import_pydevd
from mbcontextmessagehandler import MbContextMessageHandler, MbContextMessageBus
from msgbus import MBEasyContext, FM_PARAM, TK_SYS_NAK, TK_STORECFG_GET

from messagehandlerbuilder import TopicClientMessageHandlerBuilder
from topicclient import SqsConsumer

REQUIRED_SERVICES = "StoreWideConfig"


def main():
    import_pydevd(os.environ["LOADERCFG"], 9152, False)

    config_logger(os.environ["LOADERCFG"], "TopicClient")
    config_logger(os.environ["LOADERCFG"], "TopicClientReceiveThread")

    mbcontext = MBEasyContext("TopicClient")
    message_bus = MbContextMessageBus(mbcontext)

    message_handler = MbContextMessageHandler(message_bus, "TopicClient", "TopicClient", REQUIRED_SERVICES, None)

    store_code = _read_swconfig(mbcontext, "Store.Id")
    context = _read_swconfig(mbcontext, "BackOffice.Host")
    config = cfgtools.read(os.environ["LOADERCFG"])
    topic_arn = config.find_value("TopicClient.TopicArn")
    aws_access_key = config.find_value("TopicClient.AwsAccessKey")
    aws_secret_key = config.find_value("TopicClient.AwsSecretKey")
    subjects = config.find_values("TopicClient.ClientSubjects")
    queue_url = config.find_value("TopicClient.QueueUrl")
    region_name = config.find_value("TopicClient.RegionName")
    endpoint_url = config.find_value("TopicClient.EndpointUrl", None)

    queue = boto3.resource("sqs",
                           aws_access_key_id=aws_access_key,
                           aws_secret_access_key=aws_secret_key,
                           region_name=region_name,
                           endpoint_url=endpoint_url)\
        .Queue(queue_url + store_code)

    sqs_consumer = SqsConsumer(message_bus, queue, store_code)
    t = Thread(target=sqs_consumer.run)
    t.daemon = True
    t.start()

    for subject in subjects:
        message_bus.subscribe(subject)

    message_handler_builder = TopicClientMessageHandlerBuilder(topic_arn,
                                                               endpoint_url,
                                                               region_name,
                                                               aws_access_key,
                                                               aws_secret_key,
                                                               subjects,
                                                               store_code,
                                                               context)
    message_handler.event_handler_builder = message_handler_builder
    return message_handler.handle_events()


def _read_swconfig(mbcontext, key):
    rmsg = mbcontext.MB_EasySendMessage("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=key)
    if rmsg.token == TK_SYS_NAK:
        return None
    return str(rmsg.data)
