__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import importlib
from .pipeline import pipeline
from utils.log import log

class pipelineFactory:
	def __init__(self, config, log):
		self.__config = config
		self.__log = log

	@property
	def config(self):
		return self.__config
	@property
	def log(self) -> log:
		return self.__log
	
	@staticmethod
	def getLogger(config) -> log:
		if (config != None):
			# Init logger
			logfilename = config.getParameter(C.PARAM_LOGFOLDER, "") + config.getParameter(C.PARAM_LOGFILENAME, C.TRACE_FILENAME)
			print("Log file: {}".format(logfilename))
			level = config.getParameter(C.PARAM_LOGLEVEL, C.TRACE_DEFAULT_LEVEL)
			format = config.getParameter(C.PARAM_LOGFORMAT, C.TRACE_DEFAULT_FORMAT)
			return log(__name__, logfilename, level, format)
		else:
			raise Exception ("Configuration failed, impossible to create the logger.")

	def process(self):
		""" Initialize the process and execute the pipeline
		Returns:
			int: Number of rows read
			int: Number of rows transformed
			int: Number of rows loaded
		"""
		try:
			# INSTANCIATE ONLY THE NEEDED CLASS / DATA SOURCE TYPE
			self.log.info("BPPI Bridge initialisation ...")
			pipeline = self.create()
			if (pipeline == None):
				raise Exception ("The Data pipeline has not been created successfully")
		except Exception as e:
			self.log.error("pipelineFactory.process(): The BPPI bridge cannot be initialized: {}".format(str(e)))
			return
		
		return self.execute(pipeline=pipeline)
	
	def execute(self, pipeline):
		""" Execute the pipeline
		Returns:
			int: Number of rows read
			int: Number of rows transformed
			int: Number of rows loaded
		"""
		E_counts, T_counts, L_counts = 0, 0, 0
		try:
			# PROCESS THE DATA
			if (pipeline.initialize()): # init logs here ...
				pipeline.log.info("The BPPI Bridge has been initialized successfully")
				pipeline.log.info("Extract data from Data Source ...")
				df = pipeline.extract()	# EXTRACT (E of ETL)
				E_counts = df.shape[0]
				pipeline.log.info("Data extracted successfully, {} rows to import into BPPI".format(E_counts))
				if (df.shape[0] == 0):
					pipeline.log.info("** There are no data to process, terminate here **")
				else:
					pipeline.log.info("Transform imported data ...")
					df = pipeline.transform(df)	# TRANSFORM (T of ETL)
					T_counts = df.shape[0]
					pipeline.log.info("Data transformed successfully, {} rows - after transformation - to import into BPPI".format(T_counts))
					if (df.empty != True): 
						# LOAD (L of ETL)
						pipeline.log.info("Load data into the BPPI Repository table ...")
						if pipeline.load(df): # LOAD (L of ETL)
							L_counts = T_counts
							pipeline.log.info("Data loaded successfully")
							if (self.config.getParameter(C.PARAM_BPPITODOACTIVED, C.NO) == C.YES):
								pipeline.log.info("Execute one or more BPPI <ToDo> ...")
								if (pipeline.afterLoad()):
									pipeline.log.info("BPPI To Do executed successfully")
				pipeline.log.info("Data Counts -> E:{} T:{} L:{}".format(E_counts, T_counts, L_counts))
			else:
				self.log.error("pipelineFactory.createAndExecute(): The Data pipeline has not been initialized properly")
			
			pipeline.terminate()
			return E_counts, T_counts, L_counts
		
		except Exception as e:
			self.log.error("pipelineFactory.createAndExecute(): Error when processing the data: {}".format(str(e)))
			return E_counts, T_counts, L_counts

	def create(self) -> pipeline:
		""" This function dynamically instanciate the right data pipeline (manages ETL) class to create a pipeline object. 
			This to avoid in loading all the connectors (if any of them failed for example) when making a global import, 
			by this way only the needed import is done on the fly
			Args:
				pipeline (str): Datasource type
				config (config): Configuration set
			Returns:
				Object: Data Source Object
		"""
		try:
			# Get the pipeline class to instantiate from the config
			pipelinePath = self.config.getParameter(C.PARAM_PIPELINE_PATH, C.PIPELINE_FOLDER)
			pipelineClass = self.config.getParameter(C.PARAM_PIPELINE_CLASSNAME, C.PIPELINE_FOLDER)
			fullClassPath = pipelinePath + "." + pipelineClass
			
			# Instantiate the pipeline object
			self.log.debug("pipelineFactory.create(): Import module -> {}".format(fullClassPath))
			datasourceObject = importlib.import_module(fullClassPath)
			self.log.debug("pipelineFactory.create(): Module {} imported, instantiate the class".format(fullClassPath))
			pipelineClass = getattr(datasourceObject, pipelineClass)
			pipelineObject = pipelineClass(self.config, self.log)
			self.log.info("Pipeline created successfully")
			return pipelineObject
		
		except Exception as e:
			self.log.error("pipelineFactory.create(): Error when loading the Data Source Factory: {}".format(str(e)))
			return None
