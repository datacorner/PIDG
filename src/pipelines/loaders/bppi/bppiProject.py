__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from bppi.repository.bppiApiRepositoryWrapper import bppiApiRepositoryWrapper
from pipelines.pidgPipeline import pidgPipeline
import utils.constants as C

MANDATORY_PARAM_LIST = [C.PARAM_BPPITOKEN, 
                        C.PARAM_BPPIURL]

class bppiProject(pidgPipeline):
    def __init__(self, config):
        super().__init__(config)
        self.__projectInfos = None   # BPPI Project infos (gathered from the bppi server)
