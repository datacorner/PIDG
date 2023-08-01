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

    def processTest(self, config):
        print("Process Test")
	    # Get configuration from cmdline & ini file
        config = cmdLineConfig.emulate_readIni(configfile=config) 
        return pipelineFactory(config).process()

    def test_csv_Generate_Map(self):
        evtmapfile = "tests/data/evtmap-gen.csv"
        configfile="./tests/config/config-csv-evtmap-gen.ini"
        try:
            os.remove(evtmapfile)
        except:
            pass
        self.e, self.t, self.l = self.processTest(configfile)
        df = pd.read_csv(evtmapfile)
        self.assertTrue(df.shape[0]==29)

    def test_csv_check_Map(self):
        filename = "./tests/data/test.csv"
        configfile="./tests/config/config-csv-evtmap-map.ini"
        self.e, self.t, self.l = self.processTest(configfile)
        self.assertTrue(self.e==1394 and self.t==1130 and self.l==1130)

if __name__ == '__main__':
    unittest.main()