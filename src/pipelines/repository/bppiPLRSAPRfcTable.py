__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from bppiapi.repository.bppiRepository import bppiRepository
import pandas as pd
from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError, RFCError

from pipelines.readers.sapRFCTable import sapRFCTable
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

    def extract(self) -> pd.DataFrame: 
        """Read the SAP Table file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            ASHOST = self.config.getParameter(C.PARAM_SAP_ASHOST, C.EMPTY) 
            CLIENT = self.config.getParameter(C.PARAM_SAP_CLIENT, C.EMPTY) 
            SYSNR = self.config.getParameter(C.PARAM_SAP_SYSNR, C.EMPTY)
            USER = self.config.getParameter(C.PARAM_SAP_USER, C.EMPTY) 
            PASSWD = self.config.getParameter(C.PARAM_SAP_PASSWD, C.EMPTY)
            SAPROUTER = self.config.getParameter(C.PARAM_SAP_ROUTER, C.EMPTY)
            field_names = self.config.getParameter(C.PARAM_SAP_RFC_FIELDS, C.EMPTY).split(',')
            table_name = self.config.getParameter(C.PARAM_SAP_RFC_TABLE)
            row_limit = int(self.config.getParameter(C.PARAM_SAP_RFC_ROWCOUNT, "0"))
            sap = sapRFCTable(self.log)
            sap.setConnectionParams(ahost=ASHOST, 
                                    client=CLIENT, 
                                    sysnr=SYSNR, 
                                    user=USER, 
                                    pwd=PASSWD, 
                                    router=SAPROUTER)
            sap.setImportParameters(rfcfields=field_names,
                                    rfctable=table_name,
                                    rowcount=row_limit)
            if (not sap.read()):
                raise Exception("Error while reading the XES file")
            return sap.content

        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()
        