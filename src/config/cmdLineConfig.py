__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
from config.appConfig import appConfig

class cmdLineConfig:
	
	@staticmethod
	def readDatabase(parser):
		return None, None

	@staticmethod
	def readSqlite(parser):
		""" This function gather the arguments sent in the CLI and build the configuration object / USE FOR SQLITE FILE CONFIGURATION FILE ONLY
		Args:
			parser (argparse.ArgumentParser): CLI arguments
		Raises:
			Exception: Unable to gather the CLI args
		Returns:
			utils.appConfig: config object
			string: Data Source Tag (command line)
		"""
		try:
			config = appConfig()
			# Parser CLI arguments
			parser.add_argument("-" + C.PARAM_FILENAME, help="SQLite 3 data file", required=True)
			parser.add_argument("-" + C.PARAM_SQ_ID, help="Pipeline Configuration ID inside the configuration file", required=True)
			args = vars(parser.parse_args())
			# Load configuration via the INI file
			config.loadFromSQLite(args[C.PARAM_FILENAME], args[C.PARAM_SQ_ID])

			#src = config.getParameter(C.PARAM_SRCTYPE)
			# Config "exceptions" ...
			file_management = (src == C.PARAM_SRCTYPE_VALCSV or 
							src == C.PARAM_SRCTYPE_VALXLS or 
							src == C.PARAM_SRCTYPE_VALXES or 
							src == C.PARAM_SRCTYPE_CHORUSFILE)
			if (file_management):
				# For File (CSV/XES/Excel) load only, takes the CLI args and put them in the config object
				config.addParameter(C.PARAM_FILENAME, args[C.PARAM_FILENAME])
				if (src == C.PARAM_SRCTYPE_VALCSV or src == C.PARAM_SRCTYPE_CHORUSFILE):
					config.addParameter(C.PARAM_CSV_SEPARATOR, args[C.PARAM_CSV_SEPARATOR])
				if (src == C.PARAM_SRCTYPE_VALXLS):
					config.addParameter(C.PARAM_EXCELSHEETNAME, args[C.PARAM_EXCELSHEETNAME])
			return config

		except Exception as e:
			print(e)
			parser.print_help()
			return None, None


	@staticmethod
	def manageArgs(args):
		""" manage the arguments in command line with the ini config file
		Args:
			args (_type_): command line arguments
		Returns:
			appConfig: cinfiguration object
		"""
		config = appConfig()
		# Load configuration via the INI file
		if (args[C.PARAM_CONFIGFILE] != 0):
			config.loadFromINIFile(args[C.PARAM_CONFIGFILE])
		else:
			raise Exception("Missing config file argument {}".format(C.PARAM_CONFIGFILE))
		return config

	@staticmethod
	def readIni(parser):
		""" This function gather the arguments sent in the CLI and build the configuration object / USE FOR INI FILE CONFIGURATION FILE ONLY
		Args:
			parser (argparse.ArgumentParser): CLI arguments
		Raises:
			Exception: Unable to gather the CLI args
		Returns:
			utils.appConfig: config object
			string: Data Source Tag (command line)
		"""
		try:
			# Parser CLI arguments
			parser.add_argument("-" + C.PARAM_CONFIGFILE, help="(All) Config file with all configuration details (INI format)", required=True)
			args = vars(parser.parse_args())
			config = cmdLineConfig.manageArgs(args)
			return config

		except Exception as e:
			print("ERROR> " + str(e))
			parser.print_help()
			return None, None
		
	@staticmethod
	def emulate_readIni(configfile):
		""" This function gather the arguments sent in the CLI and build the configuration object / USE FOR INI FILE CONFIGURATION FILE ONLY
		Args:
			parser (argparse.ArgumentParser): CLI arguments
		Raises:
			Exception: Unable to gather the CLI args
		Returns:
			utils.appConfig: config object
			string: Data Source Tag (command line)
		"""
		try:
			config = appConfig()
			# Check Data Source Type
			args = dict(configfile=configfile)
			config = cmdLineConfig.manageArgs(args)
			return config

		except Exception as e:
			print("ERROR> " + str(e))
			return None