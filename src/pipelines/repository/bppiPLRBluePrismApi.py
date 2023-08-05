__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.bppi.repository.bppiRepository import bppiRepository
import pandas as pd
from pipelines.extractors.bpAPIExtractor import bpAPIExtractor
from pipelines.transformers.bplogsTransformer import bplogsTransformer

BP_MANDATORY_PARAM_LIST = [C.PARAM_BPPITOKEN, 
                           C.PARAM_BPPIURL, 
                           C.PARAM_BPPROCESSNAME,
                           C.PARAM_BPAPI_CLIENT_ID,
                           C.PARAM_BPAPI_SECRET,
                           C.PARAM_BPAPI_AUTH_URL]

""" Manages the Blue Prism API extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRBluePrismApi
    Columns read from the API:
    (*) logId
    (*) SessionID
    (*) stageName
    (*) stageType
    (*) result
    (*) resourceStartTime
    (*) ResourceName
    hasParameters
    status
"""
class bppiPLRBluePrismApi(bppiRepository):
    @property
    def mandatoryParameters(self) -> str:
        return BP_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the Excel file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            api = bpAPIExtractor(self.log)
            api.setConnectionParams(bpProcessName=self.config.getParameter(C.PARAM_BPPROCESSNAME),
                                    clientID=self.config.getParameter(C.PARAM_BPAPI_CLIENT_ID, C.EMPTY),
                                    pageSize=self.config.getParameter(C.PARAM_BPAPI_API_PAGESIZE, "10"),
                                    sslCheck=self.config.getParameter(C.PARAM_BPAPI_SSL_VERIF, C.YES),
                                    secret=self.config.getParameter(C.PARAM_BPAPI_SECRET, C.EMPTY),
                                    urlApi=self.config.getParameter(C.PARAM_BPAPI_API_URL, C.EMPTY),
                                    urlAuth=self.config.getParameter(C.PARAM_BPAPI_AUTH_URL, C.EMPTY))
            if (not api.read()):
                raise Exception("Error while accessing the Blue Prism API")
            return api.content
        
        except Exception as e:
            self.log.error("Extract() Error -> " + str(e))
            return super().extract()
        
    def transform(self, df) -> pd.DataFrame:
        """Alter the collected data (from the BP Repository) by managing the attributes (stored in a XML format)
        Args:
            df (pd.DataFrame): Data source
        Returns:
            pd.DataFrame: Altered dataset with the selected parameters as new columns
        """
        try:
            logs = bplogsTransformer(dfLogs=df, log=self.log)

            # Add the stage identifier / event mapping needs
            logs.createStageID()

            # Change the event to map by default if not filled out (surcharge the events.eventcolumn INI parameter)
            if (self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.EMPTY) == C.EMPTY and logs.checkField(C.COL_STAGE_ID)):
                self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.COL_STAGE_ID)

            # Filter and/or update the event names if needed/configured
            return super().transform(logs.content)
        
        except Exception as e:
            self.log.error("bppiPLRBluePrismApi.transform() -> Unable to update the data " + str(e))
            return super().transform(df)
