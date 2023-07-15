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

    def processTest(self, filename, sep):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config, src = cmdLineConfig.emulate_readIni(sourcetype="csv", 
                                                    configfile="./tests/config/config-csv.ini",
                                                    filename=filename,
                                                    sep=sep) 
        return pipelineFactory(src, config).createAndExecute()

    def test_csv_file_test(self):
        filename = "./tests/data/test.csv"
        sep = ","
        self.e, self.t, self.l = self.processTest(filename, sep)
        self.assertTrue(self.e==1394 and self.t==1394 and self.l==1394)


class testXESFiles(unittest.TestCase):
    def setUp(self):
        print("Running XES import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of XES import Test")

    def processTest(self, filename):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config, src = cmdLineConfig.emulate_readIni(sourcetype="xes", 
                                                    configfile="./tests/config/config-xes.ini",
                                                    filename=filename) 
        return pipelineFactory(src, config).createAndExecute()

    def test_xes_file_test(self):
        filename = "./tests/data/test.xes"
        self.e, self.t, self.l = self.processTest(filename)
        self.assertTrue(self.e==1394 and self.t==1394 and self.l==1394)

class testExcelFiles(unittest.TestCase):
    def setUp(self):
        print("Running Excel import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of Excel import Test")

    def processTest(self, filename, sheet):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config, src = cmdLineConfig.emulate_readIni(sourcetype="excel", 
                                                    configfile="./tests/config/config-excel.ini",
                                                    filename=filename,
                                                    sheet=sheet) 
        return pipelineFactory(src, config).createAndExecute()

    def test_excel_file_test(self):
        filename = "./tests/data/test.xlsx"
        sheet = "test"
        self.e, self.t, self.l = self.processTest(filename, sheet)
        self.assertTrue(self.e==1394 and self.t==1394 and self.l==1394)

if __name__ == '__main__':
    unittest.main()