__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import pandas as pd
from .Extractor import Extractor 
import pyodbc
import warnings

warnings.filterwarnings('ignore')

class odbcExtractor(Extractor):
    def setConnectionParams(self, connectionstring, query):
        self.__connString = connectionstring
        self.__query = query

    @property
    def query(self) -> str:
        return self.__query

    def read(self) -> bool:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            self.log.info("Connect to the ODBC Datasource ...")
            odbcConnection = pyodbc.connect(self.__connString)
            self.log.info("Connected to ODBC Data source")
            if (not odbcConnection.closed):
                self.log.debug("Execute the query: {}".format(self.query))
                self.content = pd.read_sql(self.query, odbcConnection)
                odbcConnection.close()
                self.log.debug("<{}> rows read".format(self.content.shape[0]))
            return True
        
        except Exception as e:
            self.log.error("odbcReader.read() Error: " + str(e))
            try:
                odbcConnection.close()
            except:
                pass
            return False