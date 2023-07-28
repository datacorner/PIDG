__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import json

class repConfig():
    """ This class contains all the informations from the BPPI Repository Configuration page (Data Source).
    """
    def __init__(self, httpResponse = None):
        super().__init__()
        if (httpResponse == None):
            self.__httpResponse = None
            self.__repositoryId = ""
            self.__repositoryTableName = ""
            self.__username = ""
            self.__password = ""
            self.__dbConnectionString = ""
            self.__query = ""
            self.__todoLists = []
            super().loaded = False
            self.__jsonContent = json.dumps({}).encode("utf8")
        else:
            self.__jsonContent = httpResponse.content
            self.__httpResponse = httpResponse
            self.parse(httpResponse.content)
        return
    
    def parse(self, httpResponse):
        try:
            j = json.loads(httpResponse)
            self.__repositoryId = j['repositoryId']
            self.__repositoryTableName = j['repositoryTableName']
            self.__todoLists = j['todoLists']
            self.__username = j['username']
            self.__password = j['password']
            self.__dbConnectionString = j['dbConnectionString']
            self.__query = j['query']
            self.__loaded = True
        except:
            self.__loaded = False

    @property
    def jsonContent(self):
        return self.__jsonContent
    
    @property
    def repositoryId(self):
        return self.__repositoryId
    
    @property
    def repositoryTableName(self):
        return self.__repositoryTableName
    @repositoryTableName.setter   
    def repositoryTableName(self, value):
        self.__repositoryTableName = value
        
    @property
    def todoLists(self):
        return self.__todoLists
    @todoLists.setter   
    def todoLists(self, value):
        self.__todoLists = value

    @property
    def loaded(self):
        return self.__loaded
    @loaded.setter   
    def loaded(self, value):
        self.__loaded = value