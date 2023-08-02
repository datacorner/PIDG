__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig
from utils.log import log
import utils.constants as C

def main() -> None:
	"""Entry point for the application script"""
	
	# Get configuration from cmdline & ini file
	config = cmdLineConfig.readIni(argparse.ArgumentParser())
	# Get the logger
	log = pipelineFactory.getLogger(config)
	# Execute the pipeline 
	pipelineFactory(config, log).process()