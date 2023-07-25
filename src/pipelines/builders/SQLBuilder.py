__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import pathlib
from string import Template

class SQLBuilder():
    def __init__(self, log, config):
        self.__log = log
        self.__config = config
        pass

    @property
    def log(self):
        return self.__log
    @property
    def config(self):
        return self.__config
    
    def getTemplate(self) -> Template:
        """ returns the template SQL file
        Args:
            filename (_type_): filename (from the INI database.query parameter)
        Returns:
            Template: Return the String template
        """
        try:
            content = self.config.getParameter(C.PARAM_QUERY)
            if (self.config.getParameter(C.CONFIG_SOURCE_NAME, C.EMPTY) == C.CONFIG_SOURCE_SQ3):
                # If config from SQLite or DB, the content is inside the field
                return Template(content)
            else:
                # If config from INI file, the content is inside a file
                return Template(pathlib.Path(content).read_text())
        except Exception as e:
            self.log.error("getTemplate() -> Error when reading the SQL template " + str(e))
            return ""

    def setSubstDict(self) -> dict:
        """ returns a dictionnary with all the values to substitute in the SQL query.
            By default no values to substitute
        Returns:
            dict: dictionnary with values
        """
        return {}

    def build(self) -> str:
        """Build the SQL Query based on a string template (stored in a file)
        Returns:
            str: built SQL Query
        """
        try: 
            # Get the query skeleton in the sql file
            sqlTemplate = self.getTemplate()
            # Create the Substitute dict
            valuesToReplace = self.setSubstDict()
            # replace the values in the template
            return sqlTemplate.substitute(valuesToReplace)

        except Exception as e:
            self.log.error("build() -> Unable to build the Blue Prism Query -> " + str(e))
            return C.EMPTY