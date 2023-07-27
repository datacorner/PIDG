__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import pandas as pd
from .Reader import Reader 

class bpAPIReader(Reader):
    def read(self) -> bool:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            return True
        
        except Exception as e:
            self.log.error("bpAPIReader.read() Error: " + str(e))
            return False