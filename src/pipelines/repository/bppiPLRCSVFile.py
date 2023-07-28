__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppi.repository.bppiRepository import bppiRepository
import pandas as pd
from pipelines.readers.csvFileReader import csvFileReader

CSV_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME]

""" Manages the CSV file extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRCSVFile
"""
class bppiPLRCSVFile(bppiRepository):

    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return CSV_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the CSV file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            csv = csvFileReader(self.log)
            csv.filename = self.config.getParameter(C.PARAM_FILENAME)
            csv.separator = self.config.getParameter(C.PARAM_CSV_SEPARATOR, C.DEFCSVSEP)
            if (not csv.read()):
                raise Exception("Error while reading the CSV file")
            return csv.content
        
        except Exception as e:
            self.log.error("extract() Error" + str(e))
            return super().extract()
        