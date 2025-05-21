from __future__ import absolute_import  # JetBrains warning fix

import unittest

from mock import Mock, NonCallableMagicMock
from schedulecomp import CronTrigger, Clock


class CronTriggerTestCase(unittest.TestCase):
    def test_whenTimeValidForCronExpressionIsReadyReturnsTrue(self):
        clock_mock = NonCallableMagicMock(spec=Clock)
        clock_mock.current_time = Mock(return_value=(2016, 3, 22, 22, 0))

        cron_trigger = CronTrigger(clock_mock, "0 * * * * comment")

        self.assertIs(cron_trigger.is_ready(), True)

    def test_whenTimeNotValidForCronExpressionIsReadyReturnsFalse(self):
        clock_mock = NonCallableMagicMock(spec=Clock)
        clock_mock.current_time = Mock(return_value=(2016, 3, 22, 22, 14))

        cron_trigger = CronTrigger(clock_mock, "0 * * * * comment")

        self.assertIs(cron_trigger.is_ready(), False)

