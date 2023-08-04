__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import logging

ENCODING = "utf-8"
YES = "yes"
NO = "no"
EMPTY = ""
DEFCSVSEP = ","

# Pipeline datasource default classes storage
PIPELINE_FOLDER = 'pipelines.repository.' 

# Configuration type
CONFIG_SOURCE_NAME = "configsource"
CONFIG_SOURCE_SQ3 = "sqlite3"
CONFIG_SOURCE_INI = "ini"   

# Parameter Names (INI/Command line)
PARAM_PIPELINE_PATH = "pipeline.path"                   # default path where the pipelines are stored (optional)
PARAM_PIPELINE_CLASSNAME = "pipeline.classname"         # pipeline class name / must derive from the pipeline class
PARAM_FILENAME = "source.filename"                      # {csv|xes} Source file dataset
PARAM_CSV_SEPARATOR ="source.separator"                 # {csv} CSV fields separator (by default comma)
PARAM_CONFIGFILE = "configfile"                         # {odbc|bprepo} Config / INI file
PARAM_EXCELSHEETNAME = "source.sheet"                   # {excel} Excel spreadsheet name
PARAM_FROMDATE = "source.fromdate"                      # {bprepo}From Date (delta extraction)
PARAM_TODATE = "source.todate"                          # {bprepo}To Date (delta extraction)
PARAM_BPPITOKEN = "bppi.token"                          # {csv|xes|excel|odbc|bprepo} BPPI Token
PARAM_BPPIURL = "bppi.url"                              # {csv|xes|excel|odbc|bprepo} BPPI URL
PARAM_CONNECTIONSTRING = "database.connectionstring"    # {ODBC/Blue Prism} ODBC Connection String
PARAM_QUERY = "database.query"                          # {ODBC|bprepo} Query to gather data
PARAM_BPPROCESSNAME = "blueprism.processname"           # {bprepo} Process Name  (to gather the logs from)
PARAM_BPSTAGETYPES = "blueprism.stagetypefilters"       # {bprepo} filter out these stages (list of stages type separated by comma)
PARAM_BPINCLUDEVBO = "blueprism.includevbo"             # {bprepo} yes/no : Extract the VBO logs
PARAM_BPUNICODE = "blueprism.unicode"                   # {bprepo} yes/no : Blue Prism logs in unicode or not
PARAM_BPPITABLE = "bppi.table"                          # {odbc|bprepo} Name of the table in the BPPI repository
PARAM_BPPITODOACTIVED = "bppi.todos"                    # {csv|xes|excel|odbc|bprepo} Execute the to do (yes/no)
PARAM_BPPITODOS = "bppi.todolist"                       # {odbc|bprepo} List of BPPI TO DOs to execute after loading
PARAM_LOGFILENAME = "other.logfilename"                 # {csv|xes|excel|odbc|bprepo} Filename of the Log file
PARAM_LOGFOLDER = "other.logfolder"                     # {csv|xes|excel|odbc|bprepo} Folder to store the Logs
PARAM_LOGLEVEL = "other.loglevel"                       # {csv|xes|excel|odbc|bprepo} Log level (DEBUG|INFO|WARNING|ERROR)
PARAM_LOGFORMAT = "other.logformat"                     # {csv|xes|excel|odbc|bprepo} Log format (Cf. Python logger doc)
PARAM_BPPARAMSATTR = "blueprism.parameters"             # {bprepo} List (separated by a comma) of the BP parameters/attributes to gather (will be added in new columns)
PARAM_EVENTMAP = "events.eventmap"                           # {odbc|bprepo} yes/no : manage event mapping
PARAM_EVENTMAPTABLE = "events.eventmaptable"                 # {odbc|bprepo} Map the events with the dataset. This param contains the name of the csv file which stores the event map (col 1: source event name, col 2: new event name)
PARAM_EVENTMAPNAME = "events.eventcolumn"                    # {odbc|bprepo} Name of the event column name in the original source
PARAM_BPFILTERSTEND = "blueprism.startendfilter"        # {bprepo} yes/no: filtr out all Start & End stages except the Main Page ones
PARAM_BPMAINPROCESSPAGE = "blueprism.mainprocesspage"   # {bprepo} BP Process Main Page name
PARAM_BPDELTA = "blueprism.delta"                       # {bprepo} delta load activated (yes/no), if no full load
PARAM_BPDELTA_FILE = "blueprism.deltafile"              # {bprepo} file where the latest date load is saved (for delta load only)
PARAM_SAP_ASHOST = "sap.ashost"                         # {saptable} AP Host name or IP
PARAM_SAP_CLIENT = "sap.client"                         # {saptable} SAP Client
PARAM_SAP_SYSNR = "sap.sysnr"                           # {saptable} SAP System Number
PARAM_SAP_USER = "sap.user"                             # {saptable} SAP User
PARAM_SAP_PASSWD = "sap.passwd"                         # {saptable} SAP Password
PARAM_SAP_ROUTER = "sap.saprouter"                      # {saptable} SAP Router (if any)
PARAM_SAP_RFC_TABLE = "sap.rfctable"                    # {saptable} RFC Table to request
PARAM_SAP_RFC_FIELDS = "sap.rfcfields"                  # {saptable} List of fields to gather (separated by a comma)
PARAM_SAP_RFC_ROWCOUNT = "sap.rowlimit"                 # {saptable} Row Count limit (Nb Max of rows retreived from SAP)
PARAM_BPAPI_SSL_VERIF = "blueprismapi.ssl_verification" # {bpapi} Verification SSL ?
PARAM_BPAPI_CLIENT_ID = "blueprismapi.client_id"        # {bpapi} BP API Client ID
PARAM_BPAPI_SECRET = "blueprismapi.client_secret"       # {bpapi} BP API Client Secret 
PARAM_BPAPI_AUTH_URL = "blueprismapi.auth_url"          # {bpapi} BP Authentication Server
PARAM_BPAPI_API_URL = "blueprismapi.api_url"            # {bpapi} BP API Server
PARAM_BPAPI_API_PAGESIZE = "blueprismapi.api_page_size" # {bpapi} API Page size

# GLOBAL HTTP REQUEST
HTTP_API_OK = 200

# BLUE PRISM API
PBAPI_VER = "/api/v7"
BPAPI_SESSIONS_LIST = "/sessions"
BPAPI_SESSION_HEAD = "/sessions/{}"
BPAPI_SESSION_LOGS = "/sessions/{}/logs"
BPAPI_SESSION_PARAMS = "/sessions/{}/parameters"

# BPPI API
API_1_0 = "/api/ext/1.0/"
API_REPOSITORY_CONFIG = "repository/repository-import-configuration"
API_SERVER_UPLOAD_INFOS = "repository/{}/file/upload-url"
API_SERVER_LOAD_2_REPO = "repository/{}/load"
API_PROCESSING_STATUS = "processing"
API_EXECUTE_TODO = "repository/{}/execute-todo-list"
API_DEF_WAIT_DURATION_SEC = 2
API_DEF_NB_ITERATION_MAX = 60
API_STATUS_IN_PROGRESS = "IN_PROGRESS"
API_STATUS_ERROR = "ERROR"
API_BLOC_SIZE_LIMIT = 10000 # Same limitation as the current API call via java

# Logger configuration
TRACE_DEFAULT_LEVEL = logging.DEBUG
TRACE_DEFAULT_FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
TRACE_FILENAME = "bppiapiwrapper.log"
TRACE_MAXBYTES = 1000000

# Dump file suffix
TEMP_SQLDUMP = "-temp-sqlserver-dump.csv"

# Blue Prism stuff
BPLOG_FIELD_LOGID = "logId"
BPLOG_FIELD_SESSIONID = "SessionID"
BPLOG_STARTDATETIME_COL = "resourceStartTime"       # Name of the Start Date & time column in the BP Repo
BPLOG_FILTERDATE_COL = "LOG.startdatetime"
BPLOG_RESOURCENAME_COL = "ResourceName"             # DW name
BPLOG_STAGETYPE_COL = "stageType"                   # Name of the stagetype column in the BP Repo
BPLOG_STAGENAME_COL = "stageName"                   # Name of the stagename column in the BP Repo
BPLOG_RESULT_COL = 'result'                         # Execution result
BPLOG_PAGENAME_COL = "pagename"                     # Only in PB repo
BPLOG_ACTIONNAME_COL = "actionname"                 # Only in PB repo
BPLOG_OBJTYPE_COL = "OBJECT_TYPE"                   # Only in PB repo
BPLOG_OBJNAME_COL = 'OBJECT_NAME'                   # Only in PB repo
BPLOG_PAGENAME_COL = "pagename"                     # Name of the pagename column in the BP Repo
BPLOG_PROCESSNAME_COL = "processname"               # Name of the process name column in the BP Repo
BPLOG_ATTRIBUTE_COL = "attributexml"                # Name of the attributexml column in the BP Repo
BPLOG_LOG_UNICODE = "BPASessionLog_Unicode"         # BP Log table name for unicode
BPLOG_LOG_NONUNICODE = "BPASessionLog_NonUnicode"   # BP Log table name for non unicode
BPLOG_INI4SQL = "bplogs.sql"                        # File which contains the BP SQL Query
BP_STAGE_START = "Start"                            # Name of the BP Start stage
BP_STAGE_END = "End"                                # Name of the BP End stage
BP_MAINPAGE_DEFAULT = "Main Page"                   # Name of the BP Main Page (process)
BP_DEFAULT_DELTAFILE = "bpdelta.tag"                # Default filename for the delta tag
BP_DELTADATE_FMT = "%Y-%m-%d %H:%M:%S"              # Delta date format %Y-%m-%d %H:%M:%S
COL_STAGE_ID = "stageId"
COL_OBJECT_TAB = "OBJECT_TAB"

# SQLite configuration SPecifics
PARAM_SQ_ID = "id"                                  # When using SQLite config / ID of the config
SQLITE_GETCONFIG = "SELECT * FROM VIEW_GET_FULLCONFIG_BLUEPRISM_REPO WHERE ID={}"
       