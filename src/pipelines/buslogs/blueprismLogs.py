__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import pandas as pd
import xml.etree.ElementTree as ET
from utils.log import log
import numpy as np

BP_MANDATORY_FIELD_LIST = [C.BPLOG_FIELD_SESSIONID, 
                           C.BPLOG_STAGENAME_COL, 
                           C.BPLOG_STARTDATETIME_COL]

""" Manage the Blue Prism logs in general
    Output interface for the logs:
        (*) logId: log identifier -> C.BPLOG_FIELD_LOGID
        (*) SessionID: session identifier -> C.BPLOG_FIELD_SESSIONID
        (*) stageName: stage name -> C.BPLOG_STAGENAME_COL
        (*) stagetype: stage type -> C.BPLOG_STAGETYPE_COL
        (*) result: result of exec -> C.BPLOG_RESULT_COL
        (*) resourceStartTime: start time -> C.BPLOG_STARTDATETIME_COL
        (*) ResourceName: DW worker name -> C.BPLOG_RESOURCENAME_COL
        stageId: identifier for the stage (needed for the event map)
"""

class blueprismLogs():
    @property
    def mandatoryFields(self) -> str:
        return BP_MANDATORY_FIELD_LIST
    
    def __init__(self, dfLogs, log = None):
        self.__source = C.EMPTY
        self.__dfBluePrismLogs = dfLogs
        self.__log = log

    @property
    def log(self) -> log:
        return self.__log
    
    @property
    def content(self) -> pd.DataFrame:
        return self.__dfBluePrismLogs
    
    @property
    def source(self):
        return self.__source
    @source.setter   
    def source(self, value):
        self.__source = value

    def checkField(self, fieldName):
        return set(fieldName).issubset(self.__dfBluePrismLogs.columns)

    @property
    def structCheck(self) -> bool:
        """Check the mandatory fields
        Returns:
            bool: False si at least one mandatory param is missing
        """
        try:
            return set(BP_MANDATORY_FIELD_LIST).issubset(self.__dfBluePrismLogs.columns)
        except Exception as e:
            self.log.error("blueprismLogs.dfStructureCheck() Error -> " + str(e))
            return False

    def __parseAttrs(self, logid, attribute, dfattributes) -> pd.DataFrame:
        """ Parse the attributexml field and extract (only) the text data (not the collection)
        Args:
            logid (str): ID of the log line (for later merge)
            attribute (str): attributexml value (XML format)
            dfattributes (DataFrame): Dataframe with tne incremental parameters added into
        Returns:
            pd.DataFrame: _description_
        """
        try:
            #    Blue Prism Log Format expected:
            #    <parameters>
            #        <inputs>
            #            <input name="Nom" type="text" value="Benoit Cayla" />
            #            ...
            #        </inputs>
            #        <outputs>
            #            <output name="Contact Form" type="flag" value="True" />
            #            ...
            #        </outputs>
            #    </parameters>
            root = ET.fromstring(attribute)
            if (root.tag == "parameters"):
                for input in root.findall("./inputs/input"):
                    if (input.attrib["type"] == "text"):    # only get the text input parameters
                        df_new_row = pd.DataFrame.from_records({C.BPLOG_FIELD_LOGID: logid, 
                                                                'Name' : input.attrib["name"], 
                                                                'value' :input.attrib["value"], 
                                                                'in_out' : 'I'}, index=[0])
                        dfattributes = pd.concat([dfattributes, df_new_row])
                for output in root.findall("./outputs/output"):
                    if (output.attrib["type"] == "text"):    # only get the text output parameters
                        df_new_row = pd.DataFrame.from_records({C.BPLOG_FIELD_LOGID: logid, 
                                                                'Name' : output.attrib["name"], 
                                                                'value' :output.attrib["value"], 
                                                                'in_out' : 'O'}, index=[0])
                        dfattributes = pd.concat([dfattributes, df_new_row]) 
            return dfattributes
        except Exception as e:
            self.log.error("blueprismLogs.__parseAttrs() -> Unable to parse the BP Attribute " + str(e))
            return dfattributes

    def __getAttributesFromLogs(self, parameters) -> pd.DataFrame:
        """Extract the logs (especially the parameters from the logs which are stored in XML format)
            Note: if no parameters in the list, no import
        Args:
            parameters (str / list): list of parameters separated by a comma
        Returns:
            DataFrame: logs altered with parameters
        """
        try:
            # Manage the IN/OUT parameters from the logs
            if (len(parameters) > 0):
                # Extract the input and output parameters
                self.log.info("Extract the input and output parameters")
                dfattributes = pd.DataFrame(columns= [C.BPLOG_FIELD_LOGID, "Name", "value", "in_out"])
                for index, row in self.content.iterrows():
                    if (row[C.BPLOG_ATTRIBUTE_COL] != None):
                        dfattributes = self.__parseAttrs(row[C.BPLOG_FIELD_LOGID], 
                                                         row[C.BPLOG_ATTRIBUTE_COL], 
                                                         dfattributes)
                self.log.debug("Number of attributes found: {}".format(str(dfattributes.shape[0])))
                # Only keep the desired parameters
                self.log.debug("Filter out the desired parameters")
                # Build the filter with the parameters list
                params = [ "\"" + x + "\"" for x in parameters.split(",") ]
                paramQuery = "Name in (" + ",".join(params) + ")"
                dfattributes = dfattributes.query(paramQuery)
                self.log.debug("Number of attributes found: {}".format(str(dfattributes.shape[0])))
                # Pivot the parameter values to create one new column per parameter
                self.log.info("Build the final dataset with the desired parameters")
                # add the IN or OUT parameter (the commented line below creates 2 differents parameters if the same param for IN and OUT)
                dfattributes['FullName'] = dfattributes['Name']
                dfattributesInCols = pd.pivot_table(dfattributes, 
                                                    values='value', 
                                                    index=[C.BPLOG_FIELD_LOGID], 
                                                    columns=['FullName'], 
                                                    aggfunc=np.sum, 
                                                    fill_value="")
                self.log.info("Adding {} Blue Prism variables in the set".format(dfattributesInCols.shape[1]))
                dfattributesInCols.reset_index()
                # Merge the Dataframes
                dffinal = self.content.merge(dfattributesInCols, 
                                             on=C.BPLOG_FIELD_LOGID,
                                             how='left')
                dffinal = dffinal.drop(C.BPLOG_ATTRIBUTE_COL, axis=1)
                return dffinal
            else:
                self.log.info("No parameters required in the configuration file")
                return self.content
            
        except Exception as e:
            self.log.error("blueprismLogs.__getAttributesFromLogs() -> Unable to get attributes from the Blue Prism logs " + str(e))
            return self.content

    def addAttributes(self, attributes) -> bool:
        """Extract the logs (especially the parameters from the logs which are stored in XML format). 
            Only possible with the BP Repo import.
        Args:
            attributes (str / list): list of parameters separated by a comma
        Returns:
            bool: True if there was a change (attributes added to the dataset)
        """
        try:
            if (not self.content.empty and self.checkField([C.BPLOG_ATTRIBUTE_COL])):
                dfModified = self.__getAttributesFromLogs(attributes)
                self.__dfBluePrismLogs = dfModified
                return True
            return False
        
        except Exception as e:
            self.log.error("blueprismLogs.addAttributes() -> Unable to manage the Blue Prism logs dataset " + str(e))
            return False

    def removeStartEndStages(self, mainpage) -> bool:
        """ Remove all the Start and end stages which are not in the main page
        Args:
            mainpage (_type_): Name of the main BP process page
        Returns:
            bool: True if no errors
        """
        try:
            df = self.__dfBluePrismLogs.copy()

            # Remove the logs with stagename = "End" outside the "Main Page"
            oldCount = df.shape[0]
            df = df[~((df[C.BPLOG_STAGENAME_COL] == C.BP_STAGE_END) & (df[C.BPLOG_PAGENAME_COL] != mainpage))]
            self.log.warning("{} records have been removed (No <End> stage outside the Main Process Page)".format(oldCount - df.shape[0]))

            # Remove the logs with stagename = "Start" outside the "Main Page"
            oldCount = df.shape[0] 
            df = df[~((df[C.BPLOG_STAGENAME_COL] == C.BP_STAGE_START) & (df[C.BPLOG_PAGENAME_COL] != mainpage))]
            self.log.warning("{} records have been removed (No <Start> stage outside the Main Process Page)".format(oldCount - df.shape[0]))

            self.__dfBluePrismLogs = df
            return True
        
        except Exception as e:
            self.log.error("blueprismLogs.removeStartEndStage() -> Unable to manage the remove the start and end stages from the logs " + str(e))
            return False
        
    def createStageID(self) -> bool:
        """ Add a new field which determine the Stage identifier
            ONLY for Repository import

        Returns:
            bool: True is field created successfully
        """
        try:
            if (not self.content.empty and self.checkField([C.BPLOG_PAGENAME_COL, C.BPLOG_ACTIONNAME_COL])):
                df = self.__dfBluePrismLogs.copy()
                df[C.COL_OBJECT_TAB] = df.apply(lambda row: row[C.BPLOG_PAGENAME_COL] if row[C.BPLOG_PAGENAME_COL] != None else row[C.BPLOG_ACTIONNAME_COL], axis=1)
                # Create the unique stage Identifier: STAGE_ID: STAGE_ID format: {VBO|PROC}/{Process or Object Name}/{Process Page or VBO Action}/{Stage name}
                df[C.COL_STAGE_ID] = df[[C.BPLOG_OBJTYPE_COL, 
                                        C.BPLOG_OBJNAME_COL, 
                                        C.COL_OBJECT_TAB, 
                                        C.BPLOG_STAGENAME_COL]].agg('/'.join, axis=1)
                self.log.debug("Adding Stage ID field: {}".format(C.COL_STAGE_ID))
                self.__dfBluePrismLogs = df
            elif (self.checkField([C.BPLOG_STAGENAME_COL])):
                self.__dfBluePrismLogs[C.COL_STAGE_ID] = self.__dfBluePrismLogs[C.BPLOG_STAGENAME_COL]

            return True
        except Exception as e:
            self.log.error("blueprismLogs.removeStartEndStage() -> Unable to remove the start and end stages from the logs " + str(e))
            return False

    def dropFields(self, fields):
        """ Drop fields from the set
        Args:
            fields (list): field list to drop
        Returns:
            bool: True is no error
        """
        try:
            self.log.debug("Removing {} fieds".format(len(fields)))
            self.__dfBluePrismLogs = self.__dfBluePrismLogs.drop(fields, axis=1)
            return True
        
        except Exception as e:
            self.log.error("blueprismLogs.dropFields() -> Unable to remove the fields from the set" + str(e))
            return False