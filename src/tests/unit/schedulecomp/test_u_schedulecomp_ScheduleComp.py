from __future__ import absolute_import  # JetBrains warning fix

import unittest

from mock import Mock, NonCallableMagicMock
from schedulecomp import ScheduleComp, CronTrigger, JobParser, Job, EventJob, TokenJob, Clock
from msgbus import FM_PARAM, FM_XML, FM_STRING, MBEasyContext


class ScheduleComp_ProcessCronTrigger(unittest.TestCase):

    def test_whenCronTriggerIsActiveJobIsExecuted(self):
        job_mock = Mock(spec=Job)
        job_mock.execute = Mock()

        job_parser = self._jobParserThatCreate(job_mock)
        cron_trigger = self._fixed_is_read_cron_trigger_with_value(True)

        schedule_comp = ScheduleComp(job_parser, [cron_trigger])

        schedule_comp.process_cron_triggers()

        job_mock.execute.assert_called_once()

    def test_whenCronTriggerIsNotActiveJobIsNotExecuted(self):
        job_mock = Mock(spec=Job)
        job_mock.execute = Mock()

        job_parser = self._jobParserThatCreate(job_mock)
        cron_trigger = self._fixed_is_read_cron_trigger_with_value(False)

        schedule_comp = ScheduleComp(job_parser, [cron_trigger])

        schedule_comp.process_cron_triggers()

        job_mock.execute.assert_not_called()

    def _jobParserThatCreate(self, job):
        job_parser = NonCallableMagicMock(spec=JobParser)
        job_parser.create_job = Mock(side_effect=[job])

        return job_parser

    def _fixed_is_read_cron_trigger_with_value(self, value):
        cron_trigger = Mock(spec=CronTrigger)
        cron_trigger.is_ready = Mock(side_effect=[value])
        return cron_trigger
