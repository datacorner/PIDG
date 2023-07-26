__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppiapi.repository.bppiRepository import bppiRepository
import pandas as pd
from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError, RFCError
from .reader import reader 
"""
    SE37 check in SAP
    RFC_READ_TABLE (function module)

"""

class sapRFCTable(reader):
    def setConnectionParams(self, ahost, client, sysnr, user, pwd, router):
        self.__ahost = ahost
        self.__client = client
        self.__sysnr = sysnr
        self.__user = user
        self.__pwd = pwd
        self.__router = router

    def setImportParameters(self, rfcfields, rfctable, rowcount):
        self.__rfcfields = rfcfields
        self.__rfctable = rfctable
        self.__rowcount = rowcount

    def __connectToSAP(self) -> Connection:
        """ Connect to the SAP instance via RFC
        Returns:
            connection: SAP Connection
        """
        try:
            # Get the SAP parmaters first
            self.log.info("Connect to SAP via RFC")
            conn = Connection(ashost=self.__ahost, 
                              sysnr=self.__sysnr, 
                              client=self.__client, 
                              user=self.__user, 
                              passwd=self.__pwd, 
                              saprouter=self.__router)
            return conn
        except CommunicationError:
            self.log.error("sapRFCTable.__connectToSAP() Could not connect to server.")
        except LogonError:
            self.log.error("sapRFCTable.__connectToSAP() Could not log in. Wrong credentials?")
            print("Could not log in. Wrong credentials?")
        except (ABAPApplicationError, ABAPRuntimeError):
            self.log.error("sapRFCTable.__connectToSAP(): An error occurred")
        return None

    def __callRfcReadTable(self, conn) -> pd.DataFrame:
        """ Call the RFC_READ_TABLE BAPI and get the dataset as result
        Args:
            conn (_type_): SAP Connection via pyrfc
        Returns:
            pd.DataFrame: DataFrame with the dataset
        """
        try:
            # Get the list of fields to gather
            # Call RFC_READ_TABLE
            self.log.info("Gather data from the SAP Table")
            result = conn.call("RFC_READ_TABLE",
                                ROWCOUNT=self.__rowcount,
                                QUERY_TABLE=self.__rfctable,
                                FIELDS=self.__rfcfields)

            # Get the data & create the dataFrame
            data = result["DATA"]
            self.log.info("<{}> rows has been read from SAP".format(len(data)))
            fields = result["FIELDS"]

            records = []
            for entry in data:
                record = {}
                for i, field in enumerate(fields):
                    field_name = field["FIELDNAME"]
                    idx = int(field["OFFSET"])
                    length = int(field["LENGTH"])
                    field_value = str(entry["WA"][idx:idx+length])
                    record[field_name] = field_value
                records.append(record)
            return pd.DataFrame(records, dtype=str)

        except Exception as e:
            self.log.error("sapRFCTable.__callRfcReadTable() Exception -> " + str(e))
            return pd.DataFrame()
        
    def read(self) -> bool:
        """ Returns all the SAP Table data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            sapConn = self.__connectToSAP()
            if (sapConn != None):
                self.content = self.__callRfcReadTable(sapConn)
            return True
        
        except Exception as e:
            self.log.error("sapRFCTable.read() Error: " + str(e))
            return False