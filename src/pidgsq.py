__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from pipelines.pipelineFactory import pipelineFactory
from config.cmdLineConfig import cmdLineConfig

if __name__ == "__main__":
	# Get configuration from cmdline & ini file
	config, src = cmdLineConfig.readSqlite(argparse.ArgumentParser())
	# Process 
	pipelineFactory(src, config).createAndExecute()