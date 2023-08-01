import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

class testSAP(unittest.TestCase):
    def setUp(self):
        print("Running SAP import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of SAP import Test")

    def processTest(self):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config = cmdLineConfig.emulate_readIni(configfile="./tests/config/config-sap.ini") 
        log = pipelineFactory.getLogger(config)
        return pipelineFactory(config, log).process()

    def test_sap_1(self):
        self.e, self.t, self.l = self.processTest()
        self.assertTrue(self.e==29 and self.t==29 and self.l==29)
