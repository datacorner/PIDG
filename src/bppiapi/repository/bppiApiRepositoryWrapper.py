__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import requests
import json
from bppiapi.repository.repConfig import repConfig
from bppiapi.uploadConfig import uploadConfig
from urllib import request
import utils.constants as C

class bppiApiRepositoryWrapper:
    """This class acts as a gateway for the BPPI API calls
    """
    def __init__(self, token, serverURL):
        self.__token = token
        self.__serverURL = serverURL
        self.__log = None

    @property
    def log(self):
        return self.__log
    @log.setter   
    def log(self, value):
        self.__log = value

    @property
    def apiRootPath(self):
        return self.__serverURL + C.API_1_0
    @property
    def URL(self):
        return self.__serverURL
    @property
    def Token(self):
        return self.__token

    def getRepositoryConfiguration(self) -> repConfig:
        """ HTTP GET / Gather the repository details & config from the server
        Returns:
            repConfig: BPPI repository config
        """
        try: 
            # Get Api call for getting Repository informations
            self.log.info("BPPI API - Get Api call for getting Repository informations ...")
            url = self.apiRootPath + C.API_REPOSITORY_CONFIG
            self.log.debug("BPPI API - HTTP GET Request sent: " + url)
            headers = {}
            headers["Authorization"] = "Bearer " + self.Token
            headers["content-type"] = "application/json"
            httpResponse = requests.get(url , headers=headers) 
            repositoryCfg = repConfig(httpResponse) # content in repositoryCfg.jsonContent
            if (repositoryCfg.loaded):
                self.log.info("BPPI API - Informations from BPPI Repository collected successfully")
            else:
                raise Exception ("Impossible to collect repository informations.")
            return repositoryCfg
        
        except Exception as e:
            self.log.error("bppiApiRepositoryWrapper.getRepositoryConfiguration() - " + str(e))
            return repConfig()

    def prepareUpload(self, repositoryId) -> uploadConfig:
        """ HTTP POST Call / get the Server info for upload / timeline.getUploadData
        Args:
            repositoryId (_type_): BPPI Repository ID
        Returns:
            uploadConfig: Upload details configuration
        """
        try: 
            self.log.info("BPPI API - Get the Server info for upload ...")
            url = self.apiRootPath + C.API_SERVER_UPLOAD_INFOS.format(repositoryId)
            self.log.debug("BPPI API - HTTP POST Request " + url)
            jsondata = json.dumps({"fileName": "timeline.csv"}).encode("utf8")
            self.log.debug("BPPI API - HTTP POST Data sent: ", jsondata)
            req = request.Request(url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Authorization', 'Bearer ' + self.Token)
            httpResponse = request.urlopen(req, jsondata).read().decode("utf8")
            cfg = uploadConfig(httpResponse) # see cfg.jsonContent
            if (cfg.loaded):
                self.log.info("BPPI API - Upload prepared successfully")
            else:
                raise Exception ("Impossible to prepare the upload")
            return cfg
        
        except Exception as e:
            self.log.error("bppiApiRepositoryWrapper.prepareUpload() - " + str(e))
            return uploadConfig()

    def uploadData(self, csvData, url, headersAcl) -> bool:
        """HTTP PUT Call / Upload data (csv format) to the server
        Args:
            csvData (_type_): Data (CSV format)
            url (_type_): BPPI URL (upload destination <- uploadConfig)
            headersAcl (_type_): Header ACL (<- uploadConfig)
        Returns:
            bool: _description_
        """
        try:
            self.log.info("BPPI API - Upload CSV formatted data to the BPPI Server")
            headers = {}
            headers["Authorization"] = "Bearer " + self.Token
            headers["content-type"] = "text/csv"
            headers.update(headersAcl)
            self.log.debug("BPPI API - HTTP PUT Request " + url)
            response = requests.put(url , data=csvData, headers=headers)
            self.log.debug("BPPI API - HTTP Response {}".format(str(response)))
            return response.ok
        except Exception as e:
            self.log.error("bppiApiRepositoryWrapper.uploadData() - UploadData Error | " + str(e))
            return False

    def loadFileToBPPIRepository(self, repositoryId, fkeys, repositoryTable) -> str:
        """ HTTP POST Call / Upload the file in BPPI repo / timeline.loadFileIntoRepositoryTable
        Args:
            repositoryId (_type_): BPPI Repository ID
            fkeys (_type_): Keys
            repositoryTable (_type_): Table to create/append in the Repository
        Returns:
            str: ID of the Process execution
        """
        try:
            self.log.info("BPPI API - Load the file to the BPPI repository")
            url = self.apiRootPath + C.API_SERVER_LOAD_2_REPO.format(repositoryId)
            self.log.debug("BPPI API - HTTP POST Request " + url)
            req = request.Request(url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Authorization', 'Bearer ' + self.Token)
            js = {}
            js["fileKeys"] = json.loads(fkeys)
            js["tableName"] = repositoryTable
            jsondata = json.dumps(js).encode("utf8")
            self.log.debug("HTTP POST Data sent: ", jsondata)
            httpResponse = request.urlopen(req, jsondata).read()
            jres2 = json.loads(httpResponse.decode("utf8"))
            self.log.debug("BPPI API - HTTP Response {}".format(jres2))
            self.log.info("BPPI API - Loading the file with process ID {} ".format(jres2["processingId"]))
            return jres2["processingId"]
        
        except Exception as e:
            self.log.error("bppiApiRepositoryWrapper.loadFileToBPPIRepository() - loadFileToBPPIRepository Error | " + str(e))
            return str(-1)

    def getProcessingStatus(self, processID) -> str:
        """ HTTP Returns the processing Status 
        Args:
            processID (_type_): Process ID
        Raises:
            Exception: Exception / Error with HTTP dump
        Returns:
            str: Status
        """
        try:
            self.log.info("BPPI API - Check status for the BPPI Task {}".format(processID))
            url = self.apiRootPath + C.API_PROCESSING_STATUS + "/" + processID
            self.log.debug("HTTP GET Request " + url)
            response = requests.get(url, headers={ 'Authorization': 'Bearer ' + self.Token, 'content-type': 'application/json' })
            jres = json.loads(response.content)
            self.log.debug("BPPI API - HTTP Response {}".format(response.content))
            self.log.info("BPPI API - BPPI Task {} status is {} ".format(processID, jres["status"]))
            if (jres["status"] == C.API_STATUS_ERROR):
                raise Exception(json.dumps(jres))
            return jres["status"]
        
        except Exception as e:
            self.log.error("bppiApiRepositoryWrapper.getProcessingStatus() - getProcessingStatus Error | " + str(e))
            return C.API_STATUS_ERROR

    def executeTODO(self, repositoryId, todo, tableName) -> str:
        """ HTTPPOST Call / get the Server info for upload / timeline.getUploadData
        Args:
            repositoryId (_type_): Repository ID
            todo (_type_): TO DO Name
            tableName (_type_): Table name
        Returns:
            str: Process ID
        """
        try: 
            self.log.info("BPPI API - Execute a To Do in BPPI repository")
            url = self.apiRootPath + C.API_EXECUTE_TODO.format(repositoryId)
            self.log.debug("bBPPI API - HTTP POST Request " + url)
            jsondata = json.dumps({"todoListNames": todo, "tableName" : tableName}).encode("utf8")
            self.log.debug("BPPI API - HTTP POST Data sent: ", jsondata)
            req = request.Request(url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Authorization', 'Bearer ' + self.Token)
            httpResponse = request.urlopen(req, jsondata).read()
            jres2 = json.loads(httpResponse.decode("utf8"))
            self.log.debug("BPPI API - HTTP Response {}".format(jres2))
            self.log.info("BPPI API - Loading the file with process ID: " + jres2["processingId"])
            return jres2["processingId"]
        except Exception as e:
            self.log.error(e)
            return str(-1)