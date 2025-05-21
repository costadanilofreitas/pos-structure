from __future__ import absolute_import  # JetBrains warning fix

import unittest

from mock import Mock, NonCallableMagicMock
from schedulecomp import ScheduleComp, CronTrigger, JobParser, Job, EventJob, TokenJob, Clock
from msgbus import FM_PARAM, FM_XML, FM_STRING, MBEasyContext


class EventJobTestCase(unittest.TestCase):
    def test_whenEventJobIsExecuted_EventIsSentOnMessageBus(self):
        mbcontext_mock = NonCallableMagicMock(spec=MBEasyContext)

        mbcontext_mock.MB_EasyEvtSend = Mock()
        event_job = EventJob(mbcontext_mock, "event_subject", "event_type")
        event_job.execute()

        mbcontext_mock.MB_EasyEvtSend.assert_called_once_with("event_subject", "event_type", "")

    def test_whenTokenJobIsExecuted_MessageIsSentOnMessageBus(self):
        mbcontext_mock = NonCallableMagicMock(spec=MBEasyContext)

        mbcontext_mock.MB_EasySendMessage = Mock()
        token_job = TokenJob(mbcontext_mock, "service_name", 1234, FM_XML)

        token_job.execute()

        mbcontext_mock.MB_EasySendMessage.assert_called_once_with("service_name", 1234, format=FM_XML)
