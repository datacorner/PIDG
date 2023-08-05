__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import pandas as pd
from .Extractor import Extractor 

class excelFileExtractor(Extractor):
    @property
    def filename(self):
        return self.__filename
    @filename.setter   
    def filename(self, value):
        self.__filename = value

    @property
    def sheet(self):
        return self.__sheet
    @sheet.setter   
    def sheet(self, value):
        self.__sheet = value

    def read(self) -> bool:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            if (self.sheet == "0" or self.sheet == ""):
                self.sheet = 0
            # Read the Excel file and provides a DataFrame
            self.content = pd.read_excel(self.filename, 
                               sheet_name=self.sheet) #, engine='openpyxl')
            return True
        
        except Exception as e:
            self.log.error("bpRepo.read() Error: " + str(e))
            return False