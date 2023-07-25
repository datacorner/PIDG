__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import json

class uploadConfig():
    def __init__(self, httpResponse = None):
        self.__loaded = False
        if (httpResponse == None):
            self.__url = ""
            self.__key = ""
            self.__headers = ""
            self.__jsonContent = json.dumps({}).encode("utf8")
        else:
            self.load(httpResponse)
        return
    
    def load(self, httpResponse):
        try:
            self.__jsonContent = httpResponse
            j = json.loads(httpResponse)
            self.__url = j['url']
            self.__headers = j['headers']
            self.__key = j['key']
            self.__loaded = True
        except:
            self.__loaded = False

    @property
    def jsonContent(self):
        return self.__jsonContent
    @property
    def url(self):
        return self.__url
    @property
    def key(self):
        return self.__key
    @property
    def headers(self):
        return self.__headers
    
    @property
    def loaded(self):
        return self.__loaded
    @loaded.setter   
    def loaded(self, value):
        self.__loaded = value