# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\chipservices\test.py
import unittest
import datetime
from xml.etree import ElementTree
import chipclient

class TestChipClient(unittest.TestCase):

    def setUp(self):
        self.resource_name = 'dimensions'
        self.response_exists = 'statuses'
        self.chip = chipclient.ChipClient('https://chipservices.test.paneracloud.com/chip/api', service='repo')

    def testOptions(self):
        pass

    def testGetResource(self):
        r = self.chip.get(self.resource_name)
        self.assertNotEquals(r.get(self.response_exists, None), None, 'Unexpected results for {0}'.format(self.resource_name))
        return


class TestChipRepo(unittest.TestCase):

    def setUp(self):
        self.cafe_nbr = 600601
        self.today = datetime.datetime.today()
        self.version = '1.0'
        self.chip_repo = chipclient.ChipRepository('https://chipservices.test.paneracloud.com/chip/api')

    def testGetDimensions(self):
        dims = self.chip_repo.get_dimensions()
        self.assertTrue('statuses' in dims.keys())

    def testGetCafeObject(self):
        obj = self.chip_repo.get_object(object_type='orderdayfile', cafe_nbr=self.cafe_nbr)
        self.assertTrue(obj)

    def testGetCafeObjectWithDate(self):
        obj = self.chip_repo.get_object(object_type='orderdayfile', cafe_nbr=self.cafe_nbr, effective_date=self.today)
        self.assertTrue(obj)

    def testGetCafeObjectWithVersion(self):
        obj = self.chip_repo.get_object(object_type='orderdayfile', cafe_nbr=self.cafe_nbr, version=self.version)
        self.assertTrue(obj)

    def testGetCafeObjectWithDateAndVersion(self):
        obj = self.chip_repo.get_object(object_type='orderdayfile', cafe_nbr=self.cafe_nbr, effective_date=self.today, version=self.version)
        self.assertTrue(obj)

    def testGetCafeObjectPayload(self):
        obj = self.chip_repo.get_object(object_type='orderdayfile', cafe_nbr=self.cafe_nbr)
        xml = ElementTree.fromstring(obj.get_payload())
        self.assertTrue(xml.tag == 'orderDayFile')

    def testGetEnterpriseObjectWithDate(self):
        obj = self.chip_repo.get_object(object_type='hierarchy', effective_date=self.today)
        self.assertTrue(obj)

    def testGetEnterpriseObjectWithDateAndVersion(self):
        obj = self.chip_repo.get_object(object_type='hierarchy', effective_date=self.today, version=self.version)
        self.assertTrue(obj)