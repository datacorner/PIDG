__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.repository.bppiPLRODBC import bppiPLRODBC
import pandas as pd
from pipelines.readers.builders.blueprismSQLBuilder import blueprismSQLBuilder
from pipelines.buslogs.blueprismLogs import blueprismLogs
import datetime

CANCEL_SQL_FILTER = "1=1"
BP_MANDATORY_PARAM_LIST = [C.PARAM_CONNECTIONSTRING, 
                           C.PARAM_BPPITOKEN, 
                           C.PARAM_BPPIURL, 
                           C.PARAM_BPPROCESSNAME]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRCSVFile
                - pipelines.repository.bppiPLRODBC
                    - pipelines.repository.bppiPLRBluePrismRepo
    READ data from repository columns (*) means common cols with API:
        (*) logId: log identifier -> C.BPLOG_FIELD_LOGID
        (*) SessionID: session identifier -> C.BPLOG_FIELD_SESSIONID
        (*) stageName: stage name -> C.BPLOG_STAGENAME_COL
        (*) stagetype: stage type -> C.BPLOG_STAGETYPE_COL
        (*) result: result of exec -> C.BPLOG_RESULT_COL
        (*) resourceStartTime: start time -> C.BPLOG_STARTDATETIME_COL
        (*) ResourceName: DW worker name -> C.BPLOG_RESOURCENAME_COL
        actionname: vbo action name
        pagename: page name (if process)
        attributexml : Attributes (bp variables in a XML format)
        OBJECT_TYPE: VBO or PROC
        OBJECT_NAME: Process or VBO Name
"""

class bppiPLRBluePrismRepo(bppiPLRODBC):
    @property
    def mandatoryParameters(self) -> str:
        return BP_MANDATORY_PARAM_LIST

    def __getDeltaTag(self):
        """ Get the last load date to use for the delta loading (when requested)
        Returns:
            _type_: date in straing format
        """
        if (self.config.getParameter(C.PARAM_BPDELTA, C.NO) == C.YES):
            filedelta = self.config.getParameter(C.PARAM_BPDELTA_FILE, C.BP_DEFAULT_DELTAFILE)
            try:
                with open(filedelta, "r") as file:
                    fromdate = file.read()
                return fromdate
            except:
                self.log.error("bppiPLRBluePrismRepo.__getDeltaLoadLastDate() -> Unable to read/get the tagged delta date")
                return C.EMPTY
        else:
            return C.EMPTY

    def __updDeltaTag(self):
        """ Update the date for the next delta load
        """
        if (self.config.getParameter(C.PARAM_BPDELTA, C.NO) == C.YES):
            try:
                filedelta = self.config.getParameter(C.PARAM_BPDELTA_FILE, C.BP_DEFAULT_DELTAFILE)
                with open(filedelta, "w") as file: # store in the delta file the latest delta load 
                    file.write(datetime.datetime.now().strftime(C.BP_DELTADATE_FMT))
            except:
                self.log.error("bppiPLRBluePrismRepo.__updDeltaLoadLastDate() -> Unable to write the tagged new delta date")

    @property
    def query(self) -> str:
        """Build the SQL Query to get the BP logs against the BP repository
            The BP Logs SQL query is stored in the bp.config file and can be customized with several args:
                * {attrxml}: Name of the INPUT/OUTPUT attributes columns (XML format)
                * {processname}: Process Name in Blue Prism
                * {stagetypefilter}: list of stage to filter out
                * {delta}: Delta loading condition on datetime (Between or < >)
                * {tablelog}: Name of the Log table (unicode or not unicode)
        Returns:
            str: built SQL Query
        """
        try: 
            # Get the last delta load if needed:
            lastDeltaDate = self.__getDeltaTag()
            # Build the Query
            sqlBuilder = blueprismSQLBuilder(log=self.log,
                                            query=self.config.getParameter(C.PARAM_QUERY),
                                            configtype=self.config.getParameter(C.CONFIG_SOURCE_NAME, C.CONFIG_SOURCE_INI))
            sqlBuilder.setConnectionParams(bpStageTypes=self.config.getParameter(C.PARAM_BPSTAGETYPES, "0"),
                                           processName=self.config.getParameter(C.PARAM_BPPROCESSNAME),
                                           includeVBO=self.config.getParameter(C.PARAM_BPINCLUDEVBO, C.YES),
                                           unicode=self.config.getParameter(C.PARAM_BPUNICODE),
                                           fromDate=self.config.getParameter(C.PARAM_FROMDATE),
                                           toDate=self.config.getParameter(C.PARAM_TODATE),
                                           deltaDate=lastDeltaDate)
            sql = sqlBuilder.build()
            # Update the date for the next delta load
            self.__updDeltaTag()
            return sql
        except Exception as e:
            self.log.error("bppiPLRBluePrismRepo.__buildQuery() -> Unable to build the Blue Prism Query " + str(e))
            return C.EMPTY

    def transform(self, df) -> pd.DataFrame:
        """Alter the collected data (from the BP Repository) by managing the attributes (stored in a XML format)
        Args:
            df (pd.DataFrame): Data source
        Returns:
            pd.DataFrame: Altered dataset with the selected parameters as new columns
        """
        try:
            logs = blueprismLogs(dfLogs=df, log=self.log)

            # Filter out the df by selecting only the Start & End (main page / process) stages if requested
            if (self.config.getParameter(C.PARAM_BPFILTERSTEND) == C.YES):
                mainpage = self.config.getParameter(C.PARAM_BPMAINPROCESSPAGE, C.BP_MAINPAGE_DEFAULT) 
                logs.removeStartEndStages(mainpage)
            
            # Get the attributes from the BP logs
            logs.addAttributes(self.config.getParameter(C.PARAM_BPPARAMSATTR))

            # Add the stage identifier / event mapping needs
            logs.createStageID()

            # Change the event to map by default if not filled out (surcharge the events.eventcolumn INI parameter)
            if (self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.EMPTY) == C.EMPTY and logs.checkField(C.COL_STAGE_ID)):
                self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.COL_STAGE_ID)

            logs.dropFields([C.COL_OBJECT_TAB, C.BPLOG_OBJTYPE_COL, C.BPLOG_OBJNAME_COL])

            # Filter and/or update the event names if needed/configured
            return super().transform(logs.content)
        
        except Exception as e:
            self.log.error("bppiPLRBluePrismRepo.transform() -> Unable to update the data " + str(e))
            return super().transform(df)
