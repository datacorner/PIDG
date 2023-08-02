__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.repository.bppiPLRODBC import bppiPLRODBC
import pandas as pd
import xml.etree.ElementTree as ET
import warnings
import numpy as np
from pipelines.readers.builders.blueprismSQLBuilder import blueprismSQLBuilder
import datetime

warnings.filterwarnings('ignore')
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
                self.log.error("__getDeltaLoadLastDate() -> Unable to read/get the tagged delta date")
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
                self.log.error("__updDeltaLoadLastDate() -> Unable to write the tagged new delta date")

    @property
    def query(self) -> str:
        """Build the SQL Query to get the BP logs against the BP repository
            The BP Logs SQL qeury is stored in the bp.config file and can be customized with several args:
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
            self.log.error("__buildQuery() -> Unable to build the Blue Prism Query " + str(e))
            return C.EMPTY
        
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
                        df_new_row = pd.DataFrame.from_records({'logid': logid, 
                                                                'Name' : input.attrib["name"], 
                                                                'value' :input.attrib["value"], 
                                                                'in_out' : 'I'}, index=[0])
                        dfattributes = pd.concat([dfattributes, df_new_row])
                for output in root.findall("./outputs/output"):
                    if (output.attrib["type"] == "text"):    # only get the text output parameters
                        df_new_row = pd.DataFrame.from_records({'logid': logid, 
                                                                'Name' : output.attrib["name"], 
                                                                'value' :output.attrib["value"], 
                                                                'in_out' : 'O'}, index=[0])
                        dfattributes = pd.concat([dfattributes, df_new_row]) 
            return dfattributes
        except Exception as e:
            self.log.error("__parseAttrs() -> Unable to parse the BP Attribute " + str(e))
            return dfattributes

    def __getAttributesFromLogs(self, df) -> pd.DataFrame:
        """Extract the logs (especially the parameters from the logs which are stored in XML format)
            Note: if no parameters in the list, no import
        Args:
            df (Dataframe): Dataframe with the logs
            config (bppiapi.appConfig): list of parameters from the INI file
        Returns:
            DataFrame: logs altered with parameters
        """
        try:
            parameters = self.config.getParameter(C.PARAM_BPPARAMSATTR, C.EMPTY)
            # Manage the IN/OUT parameters from the logs
            if (len(parameters) > 0):
                # Extract the input and output parameters
                self.log.info("Extract the input and output parameters")
                dfattributes = pd.DataFrame(columns= ["logid", "Name", "value", "in_out"])
                for index, row in df.iterrows():
                    if (row[C.BPLOG_ATTRIBUTE_COL] != None):
                        dfattributes = self.__parseAttrs(row["logid"], row[C.BPLOG_ATTRIBUTE_COL], dfattributes)
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
                dfattributesInCols = pd.pivot_table(dfattributes, values='value', index=['logid'], columns=['FullName'], aggfunc=np.sum, fill_value="")
                dfattributesInCols.reset_index()
                # Merge the Dataframes
                dffinal = df.merge(dfattributesInCols, on="logid", how='left')
                dffinal = dffinal.drop(C.BPLOG_ATTRIBUTE_COL, axis=1)
                return dffinal
            else:
                self.log.info("No parameters required in the configuration file")
                return df
            
        except Exception as e:
            self.log.error("__getAttributesFromLogs() -> Unable to get attributes from the Blue Prism logs " + str(e))
            return df
    
    def transform(self, df) -> pd.DataFrame:
        """Alter the collected data (from the BP Repository) by managing the attributes (stored in a XML format)
        Args:
            df (pd.DataFrame): Data source
        Returns:
            pd.DataFrame: Altered dataset with the selected parameters as new columns
        """

        try:
            # Filter out the df by selecting only the Start & End (main page / process) stages if requested
            if (self.config.getParameter(C.PARAM_BPFILTERSTEND) == C.YES):
                mainpage = self.config.getParameter(C.PARAM_BPMAINPROCESSPAGE, C.BP_MAINPAGE_DEFAULT) 
                # Remove the logs with stagename = "End" outside the "Main Page"
                oldCount = df.shape[0]
                df = df[~((df[C.BPLOG_STAGENAME_COL] == C.BP_STAGE_END) & (df[C.BPLOG_PAGENAME_COL] != mainpage))]
                self.log.warning("{} records have been removed (No <End> stage outside the Main Process Page)".format(oldCount - df.shape[0]))
                # Remove the logs with stagename = "Start" outside the "Main Page"
                oldCount = df.shape[0] 
                df = df[~((df[C.BPLOG_STAGENAME_COL] == C.BP_STAGE_START) & (df[C.BPLOG_PAGENAME_COL] != mainpage))]
                self.log.warning("{} records have been removed (No <Start> stage outside the Main Process Page)".format(oldCount - df.shape[0]))
            
            # Get the attributes from the BP logs
            df = self.__getAttributesFromLogs(df)

            # Create a new col OBJECT_TAB with the page name or the VBO action
            df[C.COL_OBJECT_TAB] = df.apply(lambda row: row["pagename"] if row["pagename"] != None else row["actionname"], axis=1)
            # Create the unique stage Identifier: STAGE_ID: STAGE_ID format: {VBO|PROC}/{Process or Object Name}/{Process Page or VBO Action}/{Stage name}
            df[C.COL_STAGE_ID] = df[['OBJECT_TYPE', 'OBJECT_NAME', C.COL_OBJECT_TAB, 'stagename']].agg('/'.join, axis=1)
            # Change the event to map by default if not filled out (surcharge the events.eventcolumn INI parameter)
            if (self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.EMPTY) == C.EMPTY):
                self.config.setParameter(C.PARAM_EVENTMAPTABLE, C.COL_STAGE_ID)

            # Filter and/or update the event names if needed/configured
            df = super().transform(df)
            return df
        
        except Exception as e:
            self.log.error("transform() -> Unable to update the data " + str(e))
            return super().transform(df)
