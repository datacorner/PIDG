__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import importlib

class pipelineFactory:
	def __init__(self, datasource, config):
		self.__config = config
		self.__datasource = datasource
    
	@property
	def config(self):
		return self.__config
	@property
	def datasource(self):
		return self.__datasource
	
	def createAndExecute(self):
		""" Initialize the process and execute
		Returns:
			int: Number of rows read
			int: Number of rows transformed
			int: Number of rows loaded
		"""
		E_counts, T_counts, L_counts = 0, 0, 0
		try:
			# INSTANCIATE ONLY THE NEEDED CLASS / DATA SOURCE TYPE
			print("Info> BPPI Bridge initialisation ...")
			pipeline = self.create()
			if (pipeline == None):
				raise Exception ("The Data pipeline cannot be created")
		except Exception as e:
			print("Error> pipelineFactory.createAndExecute(): The bridge cannot be initialized: {}".format(str(e)))
		
		try:
			# PROCESS THE DATA
			if (pipeline.initialize()):
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
						if pipeline.load(df):
							L_counts = T_counts
							pipeline.log.info("Data loaded successfully")
							if (self.config.getParameter(C.PARAM_BPPITODOACTIVED, C.NO) == C.YES):
								pipeline.log.info("Execute BPPI To Do ...")
								if (pipeline.executeToDo()):
									pipeline.log.info("BPPI To Do executed successfully")
				pipeline.terminate()
			else:
				print("pipelineFactory.createAndExecute(): The Data pipeline has not been initialized properly")
			return E_counts, T_counts, L_counts
		
		except Exception as e:
			pipeline.log.error("pipelineFactory.createAndExecute(): Error when processing the data: {}".format(str(e)))
			return E_counts, T_counts, L_counts

	def create(self):
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
			if (self.config == None): 
				raise Exception("The configuration is not available or is invalid.")
			if (self.datasource == None): 
				raise Exception("The datasource is not correctly specified or is invalid.")
			if (self.datasource == C.PARAM_SRCTYPE_VALCSV):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRCSVFile").bppiPLRCSVFile
			elif (self.datasource == C.PARAM_SRCTYPE_VALXES):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRXESFile").bppiPLRXESFile
			elif (self.datasource == C.PARAM_SRCTYPE_VALXLS):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRExcelFile").bppiPLRExcelFile
			elif (self.datasource == C.PARAM_SRCTYPE_VALODBC):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRODBC").bppiPLRODBC
			elif (self.datasource == C.PARAM_SRCTYPE_VALBP):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRBluePrismRepo").bppiPLRBluePrismRepo
			elif (self.datasource == C.PARAM_SRCTYPE_VALBPAPI):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRBluePrismApi").bppiPLRBluePrismApi
			elif (self.datasource == C.PARAM_SRCTYPE_VALSAPTABLE):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRSAPRfcTable").bppiPLRSAPRfcTable
			elif (self.datasource == C.PARAM_SRCTYPE_CHORUSFILE):
				datasourceObject = importlib.import_module(C.PIPELINE_FOLDER + "bppiPLRChorusExtract").bppiPLRChorusExtract
			else:
				raise Exception ("Error when loading the Data Source Factory in pipeline folder")
			return datasourceObject(self.config)
		
		except Exception as e:
			print("pipelineFactory.create(): Error when loading the Data Source Factory: {}".format(str(e)))
			return None
