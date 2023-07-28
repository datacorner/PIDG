__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.bppi.repository.bppiRepository import bppiRepository
import pandas as pd
from pipelines.readers.excelFileReader import excelFileReader

EXCEL_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME, 
                              C.PARAM_BPPITOKEN, 
                              C.PARAM_BPPIURL]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRExcelFile
"""
class bppiPLRExcelFile(bppiRepository):

    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return EXCEL_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the Excel file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            excel = excelFileReader(self.log)
            excel.filename = self.config.getParameter(C.PARAM_FILENAME)
            excel.sheet = self.config.getParameter(C.PARAM_EXCELSHEETNAME)
            if (not excel.read()):
                raise Exception("Error while reading the Excel file")
            return excel.content
        
        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()
        