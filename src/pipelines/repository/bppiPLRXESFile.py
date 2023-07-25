__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppiapi.repository.bppiRepository import bppiRepository
import pandas as pd
from utils.readers.xesFile import xesFile

XES_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRXESFile
"""
class bppiPLRXESFile(bppiRepository):

    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return XES_MANDATORY_PARAM_LIST

    def initialize(self) -> bool:
        return super().initialize()

    def transform(self, df) -> pd.DataFrame:
        return super().transform(df)

    def extract(self) -> pd.DataFrame: 
        """Read the XES file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            filename = self.config.getParameter(C.PARAM_FILENAME)
            log = xesFile()
            log.filename = filename
            log.getEvents()
            return log.flatContent
        
        except Exception as e:
            self.log.error("bppiPLRXESFile.extract() Error: " + str(e))
            return super().extract()
        