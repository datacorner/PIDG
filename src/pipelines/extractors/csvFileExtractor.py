__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import pandas as pd
from .Extractor import Extractor 
import utils.constants as C

class csvFileExtractor(Extractor):
    @property
    def filename(self):
        return self.__filename
    @filename.setter   
    def filename(self, value):
        self.__filename = value

    @property
    def separator(self):
        return self.__separator
    @separator.setter   
    def separator(self, value):
        self.__separator = value

    def read(self) -> bool:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            self.content = pd.read_csv(self.filename, 
                                       encoding=C.ENCODING, 
                                       delimiter=self.separator)
            return True
        
        except Exception as e:
            self.log.error("bpRepo.read() Error: " + str(e))
            return False