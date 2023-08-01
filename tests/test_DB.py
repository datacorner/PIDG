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

    def processTest(self, configfile):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config = cmdLineConfig.emulate_readIni(configfile=configfile) 
        log = pipelineFactory.getLogger(config)
        return pipelineFactory(config, log).process()

    def test_odbc_sqls(self):
        self.e, self.t, self.l = self.processTest("./tests/config/config-odbc-sqls.ini")
        self.assertTrue(self.e==12 and self.t==12 and self.l==12)

    def test_odbc_sqlite(self):
        self.e, self.t, self.l = self.processTest("./tests/config/config-odbc-sqlite.ini")
        self.assertTrue(self.e==6 and self.t==6 and self.l==6)

if __name__ == '__main__':
    unittest.main()