__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import pandas as pd
from .Extractor import Extractor 
import utils.constants as C
from pathlib import Path
import os
from pipelines.extractors.csvFileExtractor import csvFileExtractor
from pipelines.extractors.excelFileExtractor import excelFileExtractor
from pipelines.extractors.xesFileExtractor import xesFileExtractor

FILE_EXT_CSV = ".CSV"
FILE_EXT_EXCEL = ".XLSX"
FILE_EXT_XES = ".XES"

class folderExtractor(Extractor):
    @property
    def filenamesFilter(self):
        return self.__filenamesFilter
    @filenamesFilter.setter   
    def filenamesFilter(self, value):
        self.__filenamesFilter = value

    @property
    def folderName(self):
        return self.__folderName
    @folderName.setter   
    def folderName(self, value):
        self.__folderName = value

    def read(self) -> bool:
        """ Several tasks to do in this order:
            1) List the folder content
            2) filter out the interresting files 
            3) read the content of each file anc concatenate them in one dataframe
            Note: the structure (columns) must be the same.
        Returns:
            bool: False is any trouble when reading
            Only support xlsx, csv and xes files
        """
        globaldf = pd.DataFrame()
        try:
            # Get the whole list of files to read
            fileList = [f for f in Path(self.folderName).glob(self.filenamesFilter)]
            self.log.info("There are {} file(s) to read and concatenate".format(len(fileList)))
            for file in fileList:
                dataset = None
                self.log.info("Reading {} ...".format(file))
                _,ext = os.path.splitext(file)
                # Instantiate the right extractor
                if (ext.upper() == FILE_EXT_CSV):
                    dataset = csvFileExtractor(self.log)
                    dataset.filename = str(file)
                elif (ext.upper() == FILE_EXT_EXCEL):
                    dataset = excelFileExtractor(self.log)
                    dataset.filename = str(file)
                elif (ext.upper() == FILE_EXT_XES):
                    dataset = xesFileExtractor(self.log)

                # Extract the data and Merge/Concat with previous
                if (dataset != None):
                    if (not dataset.read()):
                        raise Exception("Error while reading {}".format(dataset.filename))
                    self.log.debug("Concatenating {} with {} rows and {} columns...".format(file, dataset.content.shape[0], dataset.content.shape[1]))
                    globaldf = pd.concat([globaldf, dataset.content], ignore_index=True)

            self.log.debug("Final dataset has {} rows and {} columns...".format(globaldf.shape[0], globaldf.shape[1]))
            self.content = globaldf
            return True
        
        except Exception as e:
            self.log.error("folderExtractor.read() Error: " + str(e))
            return False

