__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.loaders.bppi.bppiRepository import bppiRepository
import pandas as pd
from pipelines.extractors.sapRFCTableExtractor import sapRFCTableExtractor

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
    @property
    def mandatoryParameters(self) -> str:
        return SAP_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the SAP Table file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            sap = sapRFCTableExtractor(self.log)
            sap.setConnectionParams(ahost=self.config.getParameter(C.PARAM_SAP_ASHOST, C.EMPTY), 
                                    client=self.config.getParameter(C.PARAM_SAP_CLIENT, C.EMPTY), 
                                    sysnr=self.config.getParameter(C.PARAM_SAP_SYSNR, C.EMPTY), 
                                    user=self.config.getParameter(C.PARAM_SAP_USER, C.EMPTY), 
                                    pwd=self.config.getParameter(C.PARAM_SAP_PASSWD, C.EMPTY), 
                                    router=self.config.getParameter(C.PARAM_SAP_ROUTER, C.EMPTY))
            sap.setImportParameters(rfcfields=self.config.getParameter(C.PARAM_SAP_RFC_FIELDS, C.EMPTY).split(','),
                                    rfctable=self.config.getParameter(C.PARAM_SAP_RFC_TABLE),
                                    rowcount=int(self.config.getParameter(C.PARAM_SAP_RFC_ROWCOUNT, "0")))
            if (not sap.read()):
                raise Exception("Error while reading the XES file")
            return sap.content

        except Exception as e:
            self.log.error("extract() Error -> " + str(e))
            return super().extract()
        