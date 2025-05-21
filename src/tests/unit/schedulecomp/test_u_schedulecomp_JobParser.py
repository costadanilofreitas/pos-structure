from __future__ import absolute_import  # JetBrains warning fix

import unittest

from mock import Mock, NonCallableMagicMock
from schedulecomp import ScheduleComp, CronTrigger, JobParser, Job, EventJob, TokenJob, Clock
from msgbus import FM_PARAM, FM_XML, FM_STRING, MBEasyContext


class JobParserTestCase(unittest.TestCase):
    def test_eventJobDescriptionWithJustSubject_ParsedCorrecly(self):
        job_description = "EventJob:Subject"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        event_job = job_parser.create_job(job_description)

        self.assertIsInstance(event_job, EventJob)
        self.assertEqual(event_job.subject, "Subject")

    def test_eventJobDescriptionWithJustSubjectAndType_ParsedCorrecly(self):
        job_description = "EventJob:Subject/Type"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        event_job = job_parser.create_job(job_description)

        self.assertIsInstance(event_job, EventJob)
        self.assertEqual(event_job.subject, "Subject")
        self.assertEqual(event_job.type, "Type")

    def test_eventJobDescriptionWithJustSubjectAndTypeAndExtraParameters_ParsedCorreclyAndExtraParametersIgnored(self):
        job_description = "EventJob:Subject/Type/1/2/3/4"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        event_job = job_parser.create_job(job_description)

        self.assertIsInstance(event_job, EventJob)
        self.assertEqual(event_job.subject, "Subject")
        self.assertEqual(event_job.type, "Type")

    def test_invalidJobDescriptionNoJobTypeAndParametersSeparator_ExceptionIsRisen(self):
        job_description = "EventJob"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        self.assertRaises(Exception, job_parser.create_job, job_description)

    def test_invalidJobDescriptionInvalidJobType_ExceptionInRisen(self):
        job_description = "EventJob2:asdf/asdf"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        self.assertRaises(Exception, job_parser.create_job, job_description)

    def test_tokenJobDescriptionWithServiceNameAndToken_ParsedCorrecly(self):
        job_description = "TokenJob:service_name/234"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        token_job = job_parser.create_job(job_description)

        self.assertIsInstance(token_job, TokenJob)
        self.assertEqual(token_job.service_name, "service_name")
        self.assertEqual(token_job.token, 234)
        self.assertEqual(token_job.format, FM_PARAM)

    def test_tokenJobDescriptionWithServiceNameTokenAndFormat_ParsedCorrecly(self):
        job_description = "TokenJob:service_name/234/FM_XML"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        token_job = job_parser.create_job(job_description)

        self.assertIsInstance(token_job, TokenJob)
        self.assertEqual(token_job.service_name, "service_name")
        self.assertEqual(token_job.token, 234)
        self.assertEqual(token_job.format, FM_XML)

    def test_tokenJobDescriptionWithInvalidToken_RaisesException(self):
        job_description = "TokenJob:service_name/asdf/FM_XML"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        self.assertRaises(Exception, job_parser.create_job, job_description)

    def test_tokenJobDescriptionWithTooFewParameters_RaisesException(self):
        job_description = "TokenJob:service_name"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        self.assertRaises(Exception, job_parser.create_job, job_description)

    def test_tokenJobDescriptionWithExtraParamters_ParsedCorrectlyAndExtraParametersIgnored(self):
        job_description = "TokenJob:service_name/123/FM_STRING/asdf/asdf/asdf"

        not_used_mbcontext = None
        job_parser = JobParser(not_used_mbcontext)

        token_job = job_parser.create_job(job_description)

        self.assertIsInstance(token_job, TokenJob)
        self.assertEqual(token_job.service_name, "service_name")
        self.assertEqual(token_job.token, 123)
        self.assertEqual(token_job.format, FM_STRING)
