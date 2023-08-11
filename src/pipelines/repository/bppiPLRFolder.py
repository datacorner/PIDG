__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from pipelines.bppi.repository.bppiRepository import bppiRepository
import pandas as pd
from pipelines.extractors.folderExtractor import folderExtractor

FOLDER_MANDATORY_PARAM_LIST = [C.PARAM_FILENAME]

""" Manages the Blue Prism Repository extraction interface
    Class hierarchy:
    - bppiapi.bppiPipeline
        - bppiapi.repository.bppiRepository
"""
class bppiPLRFolder(bppiRepository):
    @property
    def mandatoryParameters(self) -> str:
        return FOLDER_MANDATORY_PARAM_LIST

    def extract(self) -> pd.DataFrame: 
        """ Several tasks to do in this order:
            1) List the folder content
            2) filter out the interresting files 
            3) read the content of each file anc concatenate them in one dataframe
        Returns:
            pd.DataFrame: Dataframe with the source data
        """
        try:
            folder = folderExtractor(self.log)
            folder.folderName = self.config.getParameter(C.PARAM_FOLDER_NAME)
            folder.filenamesFilter = self.config.getParameter(C.PARAM_FOLDER_FILEFILTER)
            if (not folder.read()):
                raise Exception("Error while reading the folder content")
            return folder.content
        
        except Exception as e:
            self.log.error("extract() Error" + str(e))
            return super().extract()