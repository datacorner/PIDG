__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import utils.constants as C
import pandas as pd
from .Extractor import Extractor 
import requests 
import urllib.parse
import warnings

AUTH_TOKEN_SUFFIX_URL = "/connect/token"
warnings.filterwarnings('ignore')

class bpAPIExtractor(Extractor):

    def setConnectionParams(self, urlAuth, urlApi, sslCheck, pageSize, clientID, secret, bpProcessName):
        self.__urlAuth = urlAuth
        self.__sslCheck = sslCheck
        self.__pageSize = pageSize
        self.__clientID = clientID
        self.__secret = secret
        self.__urlApi = urlApi 
        self.__bpProcessName = bpProcessName

    def __buildAPIURL(self):
        return self.__urlApi + C.PBAPI_VER

    def __getSSLVerification(self):
        return (self.__sslCheck == C.YES)

    def __getPageSize(self):
        return self.__pageSize

    def __getAccessToken(self):
        """ OAuth2 protocol usage with the Blue Prism API to get the access token
        Returns:
            str: Blue Prism API Access Token
        """
        try:
            self.log.debug("BP API - Get the Blue Prism API access token")
            # Obtain an access token using client credentials grant
            token_params = {
                "grant_type": "client_credentials",
                "client_id": self.__clientID,
                "client_secret": self.__secret,
            }
            token_response = requests.post(self.__urlAuth + AUTH_TOKEN_SUFFIX_URL, 
                                           data=token_params, 
                                           verify=self.__getSSLVerification())
            token_data = token_response.json()
            self.log.debug("BP API - Blue Prism Access Token has been returned successfully")
            # The access token can be extracted from the response
            return token_data["access_token"]
        
        except Exception as e:
            self.log.error("bpAPIReader.__getAccessToken() -> Unable to get the Blue Prism API Access Token, " + str(e))
            return None

    def __getSessionIDList(self, access_token):
        """ Get the list of Blue Prism Sessions,by using the access token for making authorized API requests
        Args:
            access_token (str): Blue Prism API Token access
        Returns:
            DataFrame: List of Session ID
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session list")
            headers = {
                "Authorization": "Bearer " + access_token,
            }
            api_endpoint = self.__buildAPIURL() + C.BPAPI_SESSIONS_LIST
            params = { 'sessionParameters.processName.eq': self.__bpProcessName }
            api_endpoint += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            api_response = requests.get(api_endpoint, 
                                        headers=headers, 
                                        verify=self.__getSSLVerification())
            if (api_response.status_code == C.HTTP_API_OK):
                df = pd.DataFrame.from_dict(api_response.json()["items"], orient='columns')
                self.log.debug("BP API - {} sessions have been returned.".format(len(df)))
                return df["sessionId"]
            else:
                self.log.error("bpAPIReader.__getSessionIDList() -> API Call error, {}".format((api_response.status_code)))
                return pd.DataFrame()
            
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionIDList() -> Unable to get the Blue Prism session list, " + str(e))
            return pd.DataFrame()
 
    def __getSessionDetails(self, access_token, sessionID):
        """ Returns the global informations on a Blue Prism Session (header)
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            DataFrame: Session details
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session information (header)")
            api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_HEAD).format(sessionID)
            headers = {
                "Authorization": "Bearer " + access_token,
            }
            api_response = requests.get(api_endpoint, 
                                        headers=headers, 
                                        verify=self.__getSSLVerification())
            if (api_response.status_code == C.HTTP_API_OK):
                return api_response.json()
            else:
                raise Exception("API Call error, {}".format((api_response.status_code)))
            
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionDetails() -> Unable to get the Blue Prism session global info, " + str(e))
            return pd.DataFrame()
        
    def __getSessionLogs(self, access_token, sessionID):
        """ Returns the all the sessions logs. The API works with pages (Max 1000 logs per page), so we've to loop into the returned pages.
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            DataFrame: Session logs
        """
        try:
            self.log.debug("BP API - Get the Blue Prism session [{}] details".format(sessionID))
            loop_on_page = True
            all_logs = pd.DataFrame()
            next_page_token = ""
            iteration = 1
            # The API returns logs per pages (Max 1000 logs per page)
            while (loop_on_page):
                self.log.debug("BP API - Get logs per page, iteration N°{}".format(iteration))
                # Build URL API Call
                api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_LOGS).format(sessionID)
                params = { 'sessionLogsParameters.itemsPerPage': self.__getPageSize() }
                if (next_page_token != ""):
                    params.update( { "sessionLogsParameters.pagingToken" : next_page_token })
                api_endpoint += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

                headers = {  "Authorization": "Bearer " + access_token }
                api_response = requests.get(api_endpoint, 
                                            headers=headers, 
                                            verify=self.__getSSLVerification())
                # Aggregate the logs (all pages)
                if (api_response.status_code == C.HTTP_API_OK):
                    df = pd.DataFrame.from_dict(api_response.json()["items"], orient='columns')
                    all_logs = pd.concat([all_logs, df]) 
                    next_page_token = api_response.json()["pagingToken"]
                if (next_page_token == None or api_response.status_code != C.HTTP_API_OK):
                    self.log.debug("bpAPIReader.__getSessionInfos() -> No more pages")
                    loop_on_page = False
                iteration += 1
            self.log.debug("BP API - {} sessions details (steps/stages) have been returned.".format(len(all_logs)))
            return all_logs
        
        except Exception as e:
            self.log.error("bpAPIReader.__getSessionLogs() -> Unable to get the Blue Prism session [{}] details, {}".format(sessionID, str(e)))
            return pd.DataFrame()

    def __getSessionParameters(self, access_token, sessionID):
        """ Returns the all the sessions parameters. 
            *** In progress **
        Args:
            access_token (str): Blue Prism API Token access
            sessionID (str): Blue Prism Session ID
        Returns:
            json: parameters
        """
        ssl_verification = self.__getSSLVerification()
        api_endpoint = (self.__buildAPIURL() + C.BPAPI_SESSION_PARAMS).format(sessionID)
        headers = {
            "Authorization": "Bearer " + access_token,
        }
        api_response = requests.get(api_endpoint, headers=headers, verify=ssl_verification)
        return api_response.json()

    def read(self) -> bool:
        """ Returns all the BP Repository data in a df
        Returns:
            bool: False is any trouble when reading
        """
        try:
            access_token = self.__getAccessToken()
            if (access_token != None):
                sessionIDList = self.__getSessionIDList(access_token)
                logs = pd.DataFrame()
                # Aggregate the logs from all the sessions
                for session in sessionIDList:
                    self.log.debug("BP API - Collect logs from session {} ...".format(session))
                    session_info = self.__getSessionDetails(access_token, session)
                    session_logs = self.__getSessionLogs(access_token, session)
                    # Add Session log data
                    session_logs["ResourceName"] = session_info['resourceName']
                    session_logs["status"] = session_info['status']
                    session_logs["SessionID"] = session
                    logs = pd.concat([logs, session_logs]) 
                    self.log.debug("BP API - session {} logs collected successfully, Total: {} rows/logs".format(session, logs.shape[0]))
            self.content = logs
            return True
        
        except Exception as e:
            self.log.error("bpAPIReader.read() Error: " + str(e))
            return False