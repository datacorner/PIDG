__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppiapi.repository.bppiRepository import bppiRepository
import pandas as pd
from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError, RFCError
"""
    SE37 check in SAP
    RFC_READ_TABLE (function module)

"""
SAP_MANDATORY_PARAM_LIST = [C.PARAM_BPPITOKEN, 
                            C.PARAM_BPPIURL,
                            C.PARAM_SAP_ASHOST,
                            C.PARAM_SAP_CLIENT,
                            C.PARAM_SAP_SYSNR,
                            C.PARAM_SAP_USER, 
                            C.PARAM_SAP_PASSWD,
                            C.PARAM_SAP_RFC_TABLE]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiRepository
                - pipelines.repository.bppiPLRSAPRfcTable
"""
class bppiPLRSAPRfcTable(bppiRepository):

    def __init__(self, config):
        super().__init__(config)

    @property
    def mandatoryParameters(self) -> str:
        return SAP_MANDATORY_PARAM_LIST

    def initialize(self) -> bool:
        return super().initialize()

    def transform(self, df) -> pd.DataFrame:
        return super().transform(df)

    def __connectToSAP(self) -> Connection:
        """ Connect to the SAP instance via RFC
        Returns:
            connection: SAP Connection
        """
        try:
            # Get the SAP parmaters first
            ASHOST = self.config.getParameter(C.PARAM_SAP_ASHOST, C.EMPTY)
            CLIENT = self.config.getParameter(C.PARAM_SAP_CLIENT, C.EMPTY) 
            SYSNR = self.config.getParameter(C.PARAM_SAP_SYSNR, C.EMPTY)
            USER = self.config.getParameter(C.PARAM_SAP_USER, C.EMPTY) 
            PASSWD = self.config.getParameter(C.PARAM_SAP_PASSWD, C.EMPTY)
            SAPROUTER = self.config.getParameter(C.PARAM_SAP_ROUTER, C.EMPTY)
        
            self.log.info("Connect to SAP via RFC")
            conn = Connection(ashost=ASHOST, 
                              sysnr=SYSNR, 
                              client=CLIENT, 
                              user=USER, 
                              passwd=PASSWD, 
                              saprouter=SAPROUTER)
            return conn
        except CommunicationError:
            self.log.error("CommunicationError() Could not connect to server.")
        except LogonError:
            self.log.error("LogonError() Could not log in. Wrong credentials?")
            print("Could not log in. Wrong credentials?")
        except (ABAPApplicationError, ABAPRuntimeError):
            self.log.error("ABAPApplicationError/ABAPRuntimeError() An error occurred")
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
            field_names = self.config.getParameter(C.PARAM_SAP_RFC_FIELDS, C.EMPTY).split(',')
            table_name = self.config.getParameter(C.PARAM_SAP_RFC_TABLE)
            row_limit = int(self.config.getParameter(C.PARAM_SAP_RFC_ROWCOUNT, "0"))
            # Call RFC_READ_TABLE
            self.log.info("Gather data from the SAP Table")
            result = conn.call("RFC_READ_TABLE",
                                ROWCOUNT=row_limit,
                                QUERY_TABLE=table_name,
                                FIELDS=field_names)

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
            self.log.error("call_rfc_read_table() Exception -> " + str(e))
            return pd.DataFrame()

    def extract(self) -> pd.DataFrame: 
        """Read the SAP Table file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            sapConn = self.__connectToSAP()
            if (sapConn != None):
                df = self.__callRfcReadTable(sapConn)
            return df
        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()
        