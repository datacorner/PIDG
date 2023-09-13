__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import pandas as pd
import utils.constants as C
from pipelines.pipeline import pipeline

MANDATORY_PARAM_LIST = [C.PARAM_BPPITOKEN, 
                        C.PARAM_BPPIURL]

class pidgPipeline(pipeline):

    @property
    def url(self) -> str:
        return self.__serverURL
    @property
    def token(self) -> str:
        return self.__token
    
    def checkParameters(self) -> bool:
        """Check the mandatory parameters
        Returns:
            bool: False si at least one mandatory param is missing
        """
        try:
            for param in self.mandatoryParameters:
                if (self.config.getParameter(param, "") == ""):
                    self.log.error("Parameter <{}> is missing".format(param))
                    return False 
            return True
        except Exception as e:
            self.log.error("checkParameters() Error -> " + str(e))
            return False