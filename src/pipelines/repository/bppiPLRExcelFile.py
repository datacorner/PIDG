__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppiapi.repository.bppiRepository import bppiRepository
import pandas as pd

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

    def initialize(self) -> bool:
        return super().initialize()

    def transform(self, df) -> pd.DataFrame:
        return super().transform(df)

    def extract(self) -> pd.DataFrame: 
        """Read the Excel file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            filename = self.config.getParameter(C.PARAM_FILENAME)
            sheet = self.config.getParameter(C.PARAM_EXCELSHEETNAME)
            if (sheet == "0" or sheet == ""):
                sheet = 0
            # Read the Excel file and provides a DataFrame
            df = pd.read_excel(filename, sheet_name=sheet) #, engine='openpyxl')
            return df
        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()
        