__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.readers.builders.SQLBuilder import SQLBuilder

NO_FILTER = "1=1"

class blueprismSQLBuilder(SQLBuilder):
    
    @property
    def deltaDate(self):
        return self.__deltaDate
    @deltaDate.setter   
    def deltaDate(self, value):
        self.__deltaDate = value
    
    def setSubstDict(self) -> dict:
        """ returns a dictionnary with all the values to substitute in the SQL query
        Returns:
            dict: dictionnary with values
        """
        try: 
            processname = self.config.getParameter(C.PARAM_BPPROCESSNAME)
            stagetypes = self.config.getParameter(C.PARAM_BPSTAGETYPES, "0")
            deltasql = NO_FILTER
            novbo = NO_FILTER

            # Build the filters on the VBO only
            if (self.config.getParameter(C.PARAM_BPINCLUDEVBO, C.YES) != C.YES):
                novbo = C.BPLOG_PROCESSNAME_COL + " IS NULL"

            # Date Filtering and/or DELTA vs FULL
            if (self.deltaDate != ""):
                self.log.info("DELTA Load requested - from <" + str(self.deltaDate) + ">")
                # DELTA LOAD (get date from file first)
                deltasql = " FORMAT(LOG." + C.BPLOG_STARTDATETIME_COL + ",'yyyy-MM-dd HH:mm:ss') >= '" + self.deltaDate + "'"
            else:
                self.log.info("FULL Load requested")
                
                # FULL LOAD / Add the delta extraction filters if required (-fromdate and/or -todate filled)
                fromdate = self.config.getParameter(C.PARAM_FROMDATE)
                todate = self.config.getParameter(C.PARAM_TODATE)
                if ((fromdate != C.EMPTY) and (todate != C.EMPTY)):
                    deltasql = " FORMAT(LOG." + C.BPLOG_STARTDATETIME_COL + ",'yyyy-MM-dd HH:mm:ss') BETWEEN '" + fromdate + "' AND '" + todate + "'"
                elif (fromdate != C.EMPTY):
                    deltasql = " FORMAT(LOG." + C.BPLOG_STARTDATETIME_COL + ",'yyyy-MM-dd HH:mm:ss') >= '" + fromdate + "'"
                elif (todate != C.EMPTY):
                    deltasql = " FORMAT(LOG." + C.BPLOG_STARTDATETIME_COL + ",'yyyy-MM-dd HH:mm:ss') <= '" + todate + "'"

            # BP Logs in unicode ? (default no)
            if (self.config.getParameter(C.PARAM_BPUNICODE) == C.YES):
                tablelog = C.BPLOG_LOG_UNICODE
            else:
                tablelog = C.BPLOG_LOG_NONUNICODE
                
            # Finalize the SQL Query by replacing the parameters
            valuesToReplace = { 
                                "processname" : processname, 
                                "stagetypefilters" : stagetypes, 
                                "onlybpprocess" : novbo, 
                                "delta" : deltasql, 
                                "tablelog" : tablelog
                                }
            return valuesToReplace

        except Exception as e:
            self.log.error("build() -> Unable to build the Blue Prism Query " + str(e))
            return ""