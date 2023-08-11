__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.loaders.bppi.bppiRepository import bppiRepository
import pandas as pd
from pipelines.extractors.csvFileExtractor import csvFileExtractor

CSV_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME]

""" Manages the CSV file extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRCSVFile
"""
class bppiPLRCSVFile(bppiRepository):

    @property
    def mandatoryParameters(self) -> str:
        return CSV_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the CSV file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            csv = csvFileExtractor(self.log)
            csv.filename = self.config.getParameter(C.PARAM_FILENAME)
            csv.separator = self.config.getParameter(C.PARAM_CSV_SEPARATOR, C.DEFCSVSEP)
            if (not csv.read()):
                raise Exception("Error while reading the CSV file")
            return csv.content
        
        except Exception as e:
            self.log.error("bppiPLRCSVFile.extract() Error" + str(e))
            return super().extract()
        