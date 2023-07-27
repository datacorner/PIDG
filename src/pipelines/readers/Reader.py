__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import pandas as pd
from utils.log import log

class Reader:
    def __init__(self, log = None):
        self.__content = pd.DataFrame()
        self.__log = log

    @property
    def log(self) -> log:
        return self.__log

    @property
    def content(self):
        return self.__content
    @content.setter   
    def content(self, value):
        self.__content = value

    def read(self) -> bool:
        """ Returns all the data in a DataFrame format
        Returns:
            bool: False is any trouble when reading
        """
        return True
