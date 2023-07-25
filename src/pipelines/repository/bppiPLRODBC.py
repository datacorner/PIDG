__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.repository.bppiPLRCSVFile import bppiPLRCSVFile
from pipelines.builders.SQLBuilder import SQLBuilder
import pyodbc
import pandas as pd

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
    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return ODBC_MANDATORY_PARAM_LIST

    @property
    def query(self) -> str:
        return SQLBuilder(self.log, self.config).build()

    def initialize(self) -> bool:
        return super().initialize()
    
    def transform(self, df) -> pd.DataFrame:
        return super().transform(df)
    
    def extract(self) -> pd.DataFrame: 
        """Read the DB by executing the query and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        tableResult = pd.DataFrame()
        try:
            self.log.info("Execute the ODBC Query and load the result into the BPPI repository")
            if (self.repositoryConfig.loaded):
                odbc = self.config.getParameter(C.PARAM_CONNECTIONSTRING)
                query = self.query
                sqlserverConnection = pyodbc.connect(odbc)
                self.log.debug("Connected to ODBC Data source")
                if (not sqlserverConnection.closed):
                    self.log.debug("Execute the query: {}".format(query))
                    tableResult = pd.read_sql(query, sqlserverConnection)
                    sqlserverConnection.close()
                    self.log.debug("<{}> rows read".format(tableResult.shape[0]))
            return tableResult
        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            try:
                sqlserverConnection.close()
            except:
                return super().extract()
            return super().extract()