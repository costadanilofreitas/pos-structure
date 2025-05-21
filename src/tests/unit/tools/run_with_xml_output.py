import unittest
from xmlrunner import XMLTestRunner
import sys
reload(sys)
sys.setdefaultencoding('utf8')

loader = unittest.TestLoader()
tests = loader.discover(start_dir=".", top_level_dir=".")
runner = XMLTestRunner(output=".\\test_results")
runner.run(tests)
