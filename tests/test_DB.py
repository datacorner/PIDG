import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

class testODBCFiles(unittest.TestCase):
    def setUp(self):
        print("Running ODBC import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of ODBC import Test")

    def processTest(self):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config, src = cmdLineConfig.emulate_readIni(sourcetype="odbc", 
                                                    configfile="./tests/config/config-odbc.ini") 
        return pipelineFactory(src, config).createAndExecute()

    def test_odbc_1(self):
        self.e, self.t, self.l = self.processTest()
        self.assertTrue(self.e==6 and self.t==6 and self.l==6)

if __name__ == '__main__':
    unittest.main()