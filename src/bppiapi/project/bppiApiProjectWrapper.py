__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import requests
import json
import utils.constants as C

class bppiApiProjectWrapper:
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
    
    def getProjectsList(self):
        try: 
            return True
        except Exception as e:
            self.log.error("getRepositoryConfiguration Error | " + str(e))
            return False
        