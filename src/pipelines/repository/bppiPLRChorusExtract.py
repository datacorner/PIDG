__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.repository.bppiPLRCSVFile import bppiPLRCSVFile
import pandas as pd

CHORUSFILE_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME, 
                                    C.PARAM_BPPITOKEN, 
                                    C.PARAM_BPPIURL]

""" Manages the Chorus by file extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRCSVFile
                - pipelines.repository.bppiPLRChorusExtract
"""
class bppiPLRChorusExtract(bppiPLRCSVFile):

    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return CHORUSFILE_MANDATORY_PARAM_LIST

    def initialize(self) -> bool:
        return super().initialize()

    def transform(self, df) -> pd.DataFrame:
        return super().transform(df)

    def extract(self) -> pd.DataFrame: 
        return super().extract()
        