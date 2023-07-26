import unittest
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

class testEventMap(unittest.TestCase):
    def setUp(self):
        print("Running CSV import Test")

    def tearDown(self):
        print("**** E:{} T:{} L:{} ****".format(self.e, self.t, self.l))
        print("End of CSV import Test")

    def processTest(self, filename, sep, config):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config, src = cmdLineConfig.emulate_readIni(sourcetype="csv", 
                                                    configfile=config,
                                                    filename=filename,
                                                    sep=sep) 
        return pipelineFactory(src, config).createAndExecute()


    def test_csv_Generate_Map(self):
        evtmapfile = "tests/data/evtmap-gen.csv"
        filename = "./tests/data/test.csv"
        configfile="./tests/config/config-csv-evtmap-gen.ini"
        sep = ","
        try:
            os.remove(evtmapfile)
        except:
            pass
        self.e, self.t, self.l = self.processTest(filename, sep, configfile)
        df = pd.read_csv(evtmapfile)
        self.assertTrue(df.shape[0]==29)

    def test_csv_check_Map(self):
        filename = "./tests/data/test.csv"
        configfile="./tests/config/config-csv-evtmap-map.ini"
        sep = ","
        self.e, self.t, self.l = self.processTest(filename, sep, configfile)
        self.assertTrue(self.e==1394 and self.t==1130 and self.l==1130)

if __name__ == '__main__':
    unittest.main()