__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import logging
from logging.handlers import RotatingFileHandler
import utils.constants as C

class log:
    def __init__(self, loggerName, logfilename, level, format):
        self.__logger = logging.getLogger(loggerName)
        logHandler = logging.handlers.RotatingFileHandler(logfilename, 
                                                          mode="a", 
                                                          maxBytes= C.TRACE_MAXBYTES, 
                                                          backupCount=1 , 
                                                          encoding=C.ENCODING)
        logHandler.setFormatter(logging.Formatter(format))
        if (level == "INFO"):
            loglevel = logging.INFO
        elif (level == "DEBUG"):
            loglevel = logging.DEBUG
        elif (level == "WARNING"):
            loglevel = logging.WARNING
        else:
            loglevel = logging.ERROR
        self.__logger.setLevel(loglevel)
        self.__logger.addHandler(logHandler)

    def display(self, message):
        print(message)
    
    def buildMessage(self, _msg):
        final_message = ""
        for msg in _msg:
            final_message += str(msg)
        return final_message
    
    def info(self, *message):
        final_message = self.buildMessage(message)
        self.display("Info> " + final_message)
        self.__logger.info(final_message)

    def error(self, *message):
        final_message = self.buildMessage(message)
        self.display("**ERROR**> " + final_message)
        self.__logger.error(final_message)

    def debug(self, *message):
        final_message = self.buildMessage(message)
        self.display("Debug> " + final_message)
        self.__logger.debug(final_message)

    def warning(self, *message):
        final_message = self.buildMessage(message)
        self.display("*WARNING*> " + final_message)
        self.__logger.warning(final_message)