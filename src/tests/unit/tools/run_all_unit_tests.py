import unittest
import sys
reload(sys)
sys.setdefaultencoding('utf8')

loader = unittest.TestLoader()
tests = loader.discover(start_dir=".", top_level_dir=".")
unittest.main(testLoader=loader)
