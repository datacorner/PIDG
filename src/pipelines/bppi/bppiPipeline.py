__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from pipelines.bppi.repository.bppiApiRepositoryWrapper import bppiApiRepositoryWrapper
from utils.log import log
import pandas as pd
import utils.constants as C
import time
from pipelines.pipeline import pipeline

MANDATORY_PARAM_LIST = [C.PARAM_BPPITOKEN, 
                        C.PARAM_BPPIURL]

class bppiPipeline(pipeline):

    @property
    def url(self) -> str:
        return self.__serverURL
    @property
    def token(self) -> str:
        return self.__token
    
    def checkParameters(self) -> bool:
        """Check the mandatory parameters
        Returns:
            bool: False si at least one mandatory param is missing
        """
        try:
            for param in self.mandatoryParameters:
                if (self.config.getParameter(param, "") == ""):
                    self.log.error("Parameter <{}> is missing".format(param))
                    return False 
            return True
        except Exception as e:
            self.log.error("checkParameters() Error -> " + str(e))
            return False
        
    def initialize(self) -> bool:
        """Initialize the Class instance by gathering the BPPI repository infos.
            * initialize the logger
            * check the mandatory parameters
            * init the API (get the BPPI Repository infos)
        Returns:
            bool: False if error
        """
        try:
            # Init logger
            logfilename = self.config.getParameter(C.PARAM_LOGFOLDER, "") + self.config.getParameter(C.PARAM_LOGFILENAME, C.TRACE_FILENAME)
            print("Log file: {}".format(logfilename))
            level = self.config.getParameter(C.PARAM_LOGLEVEL, C.TRACE_DEFAULT_LEVEL)
            format = self.config.getParameter(C.PARAM_LOGFORMAT, C.TRACE_DEFAULT_FORMAT)
            self.log = log(__name__, logfilename, level, format)
            # Init BPPI APIs
            self.log.info("*** Beggining of Job treatment ***")
            if (not self.checkParameters()):
                raise Exception("Some mandatory parameters are missing")
            return True
        except Exception as e:
            self.log.error("initialize() Error -> " + str(e))
            return False
    
    def getStatus(self, processingId) -> str:
        """Return the status of a process launched on the BPPI server
        Args:
            processingId (_type_): ID of the BPPI Process
        Returns:
            str: Process status (from BPPI server)
        """
        try:
            api = bppiApiRepositoryWrapper(self.config.getParameter(C.PARAM_BPPITOKEN), 
                                            self.config.getParameter(C.PARAM_BPPIURL))
            api.log = self.log
            return api.getProcessingStatus(processingId)
        except Exception as e:
            self.log.error("getStatus() Error -> " + str(e))
            return C.API_STATUS_ERROR

    def waitForEndOfProcessing(self, processId) -> str:
        """Wait for the end of the BPPI process execution
        Args:
            processId (_type_): ID of the BPPI Process
        Returns:
            str: Final Status
        """
        try:
            self.log.info("Wait for the end of a process execution")
            EndOfWait = True
            nbIterations = 0
            api = bppiApiRepositoryWrapper(self.config.getParameter(C.PARAM_BPPITOKEN), 
                                            self.config.getParameter(C.PARAM_BPPIURL))
            api.log = self.log
            while (EndOfWait):
                # 5 - Check the status to veriify if the task is finished
                status = self.getStatus(processId)
                if ((status != C.API_STATUS_IN_PROGRESS) or (nbIterations > C.API_DEF_NB_ITERATION_MAX)):
                    EndOfWait = False
                time.sleep(C.API_DEF_WAIT_DURATION_SEC)
                nbIterations += 1
            return status
        except Exception as e:
            self.log.error("waitForEndOfProcessing() Error -> " + str(e))
            return C.API_STATUS_ERROR
    
    def eventMap(self, df) -> pd.DataFrame:
        """ Map the events with the dataset (in parameter df). 
            Event Map file:
                * CSV format + Header
                * Name in the C.PARAM_EVENTMAPTABLE
                * Column to map with the event map file  in the C.PARAM_EVENTMAPNAME field (orginal dataset)
                * Only 2 columns in the event map file: 
                    - col 1: source event name (the one to map with the source dataset)
                    - col 2: new event name (the one to use for event replacement)
            Mapping Rules:
                * Replace the Col1 per col2 every time (event name replacement)
                * If Col2 empty -> remove the row (remove not necessary events)
                * If Name has not match with Col1 -> remove the row
            If the mapping file does not exists just create a template one with col1 = col2 (so that the user can update himself the column 2)
        Args:
            df (pd.DataFrame): Data Source
        Returns:
            pd.DataFrame: Data altered with the new events & remove the unecesserary ones
        """
        try:
            dfAltered = df
            if (self.config.getParameter(C.PARAM_EVENTMAP, C.NO) == C.YES):
                # Get parameters
                self.log.info("Map the events with the original dataset and the event map table")
                evtMapFilename = self.config.getParameter(C.PARAM_EVENTMAPTABLE)
                if (evtMapFilename == ""):
                    raise Exception("No Event map filename (CSV) was specified")
                evtMapColumnname = self.config.getParameter(C.PARAM_EVENTMAPNAME)
                if (evtMapColumnname == ""):
                    raise Exception("No Event column name (in the data source) was specified")
                # Open the event map file (assuming 1st col -> Original Event, 2nd col -> event altered or if nothing to remove)
                try:
                    dfevtMap = pd.read_csv(evtMapFilename, encoding=C.ENCODING)
                except FileNotFoundError as e:
                    self.log.warning("{} does not exist, create a event map template file instead".format(evtMapFilename))
                    # Create the file template
                    colName = df[evtMapColumnname].value_counts().index
                    dfevtMap = pd.DataFrame(columns=["Source", "Target"])
                    dfevtMap["Source"] = colName
                    dfevtMap["Target"] = colName
                    dfevtMap = dfevtMap.sort_values(by=['Source'])
                    dfevtMap.to_csv(evtMapFilename, encoding=C.ENCODING, index=False)
                    return df # No map to do !
                # Manage the event mapping
                if (dfevtMap.shape[1] != 2):
                    raise Exception("There are more than 2 columns in the event map file.")
                dfevtMap.rename(columns={dfevtMap.columns[0]:evtMapColumnname}, inplace=True)
                originalRecCount = df.shape[0]
                self.log.debug("There are {} records in the original dataset".format(originalRecCount))
                dfAltered = pd.merge(df, dfevtMap, on=evtMapColumnname, how ="inner")
                # Drop rows with a bad/No join (lookup) --> when the Target column is equal to NaN
                dfAltered = dfAltered.dropna(subset=["Target"])
                # Reshape the dataset (columns changes)
                del dfAltered[evtMapColumnname]
                dfAltered.rename(columns={dfevtMap.columns[1]: evtMapColumnname}, inplace=True)
                iNbRemoved = originalRecCount - dfAltered.shape[0]
                if (iNbRemoved != 0):
                    self.log.warning("{} records have been removed ".format(iNbRemoved))
            return dfAltered
        
        except Exception as e:
            self.log.error("eventMap() Error -> {}".format(str(e)))
            return df