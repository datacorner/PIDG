import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

class testCSVFiles(unittest.TestCase):
    def setUp(self):
        print("Running CSV import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of CSV import Test")

    def processTest(self):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config = cmdLineConfig.emulate_readIni(configfile="./tests/config/config-csv.ini")
        log = pipelineFactory.getLogger(config)
        return pipelineFactory(config, log).process()

    def test_csv_1(self):
        self.e, self.t, self.l = self.processTest()
        self.assertTrue(self.e==1394 and self.t==1394 and self.l==1394)

if __name__ == '__main__':
    unittest.main()