__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.readers.builders.SQLBuilder import SQLBuilder

NO_FILTER = "1=1"

class blueprismSQLBuilder(SQLBuilder):
    def setConnectionParams(self, 
                            processName=C.EMPTY, 
                            bpStageTypes="0", 
                            includeVBO=C.YES, 
                            fromDate=C.EMPTY, 
                            toDate=C.EMPTY, 
                            unicode=C.YES,
                            deltaDate=C.EMPTY):
        self.__processName = processName    # self.config.getParameter(C.PARAM_BPPROCESSNAME)
        self.__bpStageTypes = bpStageTypes  # self.config.getParameter(C.PARAM_BPSTAGETYPES, "0")
        self.__includeVBO = includeVBO      # self.config.getParameter(C.PARAM_BPINCLUDEVBO, C.YES)
        self.__fromDate = fromDate        # self.config.getParameter(C.PARAM_FROMDATE)
        self.__toDate = toDate          # self.config.getParameter(C.PARAM_TODATE)
        self.__unicode = unicode        # self.config.getParameter(C.PARAM_BPUNICODE)
        self.__deltaDate = deltaDate

    def setSubstDict(self) -> dict:
        """ returns a dictionnary with all the values to substitute in the SQL query
        Returns:
            dict: dictionnary with values
        """
        try: 
            deltasql = NO_FILTER
            novbo = NO_FILTER

            # Build the filters on the VBO only
            if (self.__includeVBO != C.YES):
                novbo = C.BPLOG_PROCESSNAME_COL + " IS NULL"

            # Date Filtering and/or DELTA vs FULL
            if (self.__deltaDate != C.EMPTY):
                self.log.info("DELTA Load requested - from <" + str(self.__deltaDate) + ">")
                # DELTA LOAD (get date from file first)
                deltasql = " FORMAT(" + C.BPLOG_FILTERDATE_COL + ",'yyyy-MM-dd HH:mm:ss') >= '" + self.__deltaDate + "'"
            else:
                self.log.info("FULL Load requested")
                # FULL LOAD / Add the delta extraction filters if required (-fromdate and/or -todate filled)
                if ((self.__fromDate != C.EMPTY) and (self.__toDate != C.EMPTY)):
                    deltasql = " FORMAT(" + C.BPLOG_FILTERDATE_COL + ",'yyyy-MM-dd HH:mm:ss') BETWEEN '" + self.__fromDate + "' AND '" + self.__toDate + "'"
                elif (self.__fromDate != C.EMPTY):
                    deltasql = " FORMAT(" + C.BPLOG_FILTERDATE_COL + ",'yyyy-MM-dd HH:mm:ss') >= '" + self.__fromDate + "'"
                elif (self.__toDate != C.EMPTY):
                    deltasql = " FORMAT(" + C.BPLOG_FILTERDATE_COL + ",'yyyy-MM-dd HH:mm:ss') <= '" + self.__toDate + "'"

            # BP Logs in unicode ? (default no)
            if (self.__unicode == C.YES):
                tablelog = C.BPLOG_LOG_UNICODE
            else:
                tablelog = C.BPLOG_LOG_NONUNICODE
                
            # Finalize the SQL Query by replacing the parameters
            valuesToReplace = { 
                                "processname" : self.__processName, 
                                "stagetypefilters" : self.__bpStageTypes, 
                                "onlybpprocess" : novbo, 
                                "delta" : deltasql, 
                                "tablelog" : tablelog
                                }
            return valuesToReplace

        except Exception as e:
            self.log.error("build() -> Unable to build the Blue Prism Query " + str(e))
            return ""