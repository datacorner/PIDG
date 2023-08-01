import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

class testBPRepo(unittest.TestCase):
    def setUp(self):
        print("Running ODBC import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of ODBC import Test")

    def processTest(self, configfile):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config = cmdLineConfig.emulate_readIni(configfile=configfile) 
        log = pipelineFactory.getLogger(config)
        return pipelineFactory(config, log).process()

    def test_bp_repo_delta(self):
        self.e, self.t, self.l = self.processTest("./tests/config/config-bprepo-delta.ini")
        self.assertTrue(self.e>0 and self.t==self.l and self.l>0)

    def test_bp_repo_full(self):
        self.e, self.t, self.l = self.processTest("./tests/config/config-bprepo-full.ini")
        self.assertTrue(self.e>0 and self.t==self.l and self.l>0)

if __name__ == '__main__':
    unittest.main()