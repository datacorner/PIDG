__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from config.appConfig import appConfig
import utils.constants as C
from utils.log import log
import pandas as pd

class pipeline:
    def __init__(self, config):
        self.__config = config          # All the configuration parameters
        self.__trace = None             # Logger

    # Contains all the config parameters (from the INI file)
    @property
    def config(self) -> appConfig:
        return self.__config
    @config.setter   
    def config(self, value):
        self.__config = value

    @property
    def mandatoryParameters(self) -> str:
        return C.EMPTY
    
    @property
    def log(self) -> log:
        return self.__trace
    @log.setter   
    def log(self, value):
        self.__trace = value

    def checkParameters(self) -> bool:
        """Check the mandatory parameters
        Returns:
            bool: False si at least one mandatory param is missing
        """
        return True
    
    def initialize(self) -> bool:
        """Initialize the Class instance for the pipeline
            * initialize the logger
            * check the mandatory parameters
            * iother inits ...
        Returns:
            bool: False if error
        """
        return True

    def terminate(self) -> bool:
        # For surcharge
        self.log.info("*** End of Job treatment ***")
        return True
    
    def extract(self) -> pd.DataFrame: 
        """This method must be surchaged and aims to collect the data from the datasource to provides the corresponding dataframe
        Returns:
            pd.DataFrame: Dataset in a pd.Dataframe object
        """
        return pd.DataFrame()

    def transform(self, df) -> pd.DataFrame: 
        """ Surcharge this method to enable modification in the Dataset after gathering the data and before uploding them in BPPI
            By default just manage the event mapping.
        Args:
            df (pd.DataFrame): source dataset
        Returns:
            pd.DataFrame: altered dataset
        """
        return self.eventMap(df)

    def load(self, dfDataset) -> bool:
        """ Surcharge this method to upload a dataset (Pandas DataFrame) into BPPI
        Args:
            dfDataset (pd.DataFrame): DataFrame with the Data to upload
        Returns:
            bool: False if error
        """
        return True