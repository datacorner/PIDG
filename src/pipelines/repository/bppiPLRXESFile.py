__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.bppi.repository.bppiRepository import bppiRepository
import pandas as pd
from pipelines.readers.xesFileReader import xesFileReader

XES_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
            - pipelines.repository.bppiPLRXESFile
"""
class bppiPLRXESFile(bppiRepository):

    @property
    def mandatoryParameters(self) -> str:
        return XES_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """Read the XES file and build the dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            filename = self.config.getParameter(C.PARAM_FILENAME)
            xes = xesFileReader(self.log)
            xes.filename = filename
            if (not xes.read()):
                raise Exception("Error while reading the XES file")
            return xes.content

        except Exception as e:
            self.log.error("bppiPLRXESFile.extract() Error: " + str(e))
            return super().extract()
        