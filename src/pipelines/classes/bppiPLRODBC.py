__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.classes.bppiPLRCSVFile import bppiPLRCSVFile
from pipelines.extractors.builders.SQLBuilder import SQLBuilder
import pandas as pd
from pipelines.extractors.odbcExtractor import odbcExtractor

# Mandatory params to check
ODBC_MANDATORY_PARAM_LIST = [C.PARAM_CONNECTIONSTRING, 
                             C.PARAM_BPPITOKEN, 
                             C.PARAM_BPPIURL, 
                             C.PARAM_QUERY]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRCSVFile
                - pipelines.repository.bppiPLRODBC
"""
class bppiPLRODBC(bppiPLRCSVFile):
    @property
    def mandatoryParameters(self) -> str:
        return ODBC_MANDATORY_PARAM_LIST

    @property
    def query(self) -> str:
        return SQLBuilder(self.log, 
                          self.config.getParameter(C.PARAM_QUERY),
                          self.config.getParameter(C.CONFIG_SOURCE_NAME, C.CONFIG_SOURCE_INI)).build()
    
    def extract(self) -> pd.DataFrame: 
        """Read the DB by executing the query and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            odbc = self.config.getParameter(C.PARAM_CONNECTIONSTRING)
            reader = odbcExtractor(self.log)
            reader.setConnectionParams(odbc, self.query)
            if (not reader.read()):
                raise Exception("Error while connecting/reading the ODBC Data Source")
            return reader.content

        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()